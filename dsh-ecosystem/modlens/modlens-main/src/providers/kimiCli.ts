// Kimi Code CLI provider: rides an existing `kimi` login, no API key.
//
// Everything here follows the CLI as observed on 0.36.1, which differs from
// the Claude one in three ways that shape this file:
//
// - No `--json-schema`, so nothing enforces the contract server-side and the
//   prompt carries the filled-in JSON template instead, parsed leniently.
// - No `--allowedTools`, so the agent's own tools cannot be narrowed. What
//   matters is narrower anyway: skill discovery reaches the shared skill
//   directories, so kimi can find the modlens skill and read the image BY
//   CALLING MODLENS, which is this provider recursing into itself. Observed
//   directly on 0.36.1. Whether it takes that route is the model's choice, so
//   it happens sometimes, which is worse to diagnose than always.
//   `--skills-dir` pointed at an empty directory replaces discovery, and kimi
//   then feeds the image to its own model.
// - `--auto` is refused alongside `--prompt` ("Cannot combine --prompt with
//   --auto"), so it is not passed.
//
// Output is NDJSON under `--output-format stream-json`: a version line, then
// assistant and tool lines, then a resume hint. The plain `text` format
// prefixes the answer with a bullet and mixes reasoning into stderr, which is
// why it is not used.
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { buildVisionPrompt, JSON_TEMPLATE_INSTRUCTION } from '../prompt.ts';
import { extractJson, truncate } from '../util/json.ts';
import type {
    BuildProviderInvocationOptions,
    ProviderInvocation,
    ProviderParsedOutput,
    VisionProvider,
} from './index.ts';

/** Set on the child so a modlens started by kimi can see it is a re-entry. */
export const KIMI_REENTRY_ENV = 'MODLENS_INSIDE_KIMI_CLI';

/**
 * A fresh empty directory standing in for skill discovery, minted per call.
 * A fixed path could be pre-created holding a skill, which would hand the
 * guard's own name to whatever wanted to defeat it; mkdtemp gives a directory
 * nobody else can have populated.
 *
 * Removed when this process exits rather than after the run: the directory has
 * to outlive the child, and an exit hook covers the paths a finally would miss
 * (a failed spawn, a timeout kill, a caller that never awaits). It is empty, so
 * the worst a missed cleanup costs is one directory entry.
 */
function freshEmptySkillsDir(): string {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'modlens-kimi-skills-'));
    process.once('exit', () => {
        try {
            fs.rmdirSync(dir);
        } catch {
            // Gone already, or not empty because something wrote into it,
            // which is not this process's business to clean up.
        }
    });
    return dir;
}

export function buildKimiCliInvocation(
    options: BuildProviderInvocationOptions,
): ProviderInvocation {
    // Belt to the --skills-dir brace: if this process was itself started by
    // kimi, running kimi again is a loop with a longer period, not a read.
    if (process.env[KIMI_REENTRY_ENV] === '1') {
        throw new Error(
            'kimi-cli refused: this modlens run was started by kimi itself, so calling kimi again would loop. Pick another provider for the nested read, or let the outer read answer.',
        );
    }

    if (options.imageKind === 'remote') {
        throw new Error(
            'kimi-cli provider reads local files only. Download the image first, or use -p gemini-api for remote URLs.',
        );
    }

    const prompt = `${buildVisionPrompt({
        imageSource: options.imageSource,
        imageKind: 'local',
        extraPrompt: options.extraPrompt,
    })}

${JSON_TEMPLATE_INSTRUCTION}`;

    const model = options.model || options.settings?.model;
    const args = [
        '-p',
        prompt,
        '--output-format',
        'stream-json',
        // Not a preference: without it kimi may load the modlens skill and
        // read the image by running modlens, which is this process calling
        // itself. Observed, and intermittent, which is the bad kind.
        '--skills-dir',
        freshEmptySkillsDir(),
        ...(model ? ['-m', model] : []),
    ];

    return {
        command: options.providerBin || 'kimi',
        args,
        cwd: path.resolve(options.workdir || path.dirname(options.imageSource)),
        env: { [KIMI_REENTRY_ENV]: '1' },
    };
}

export function parseKimiCliOutput(stdout: string): ProviderParsedOutput {
    // Last assistant line wins: the run emits an empty one before each tool
    // call, and the answer is whatever it said last.
    let answer: string | null = null;
    for (const line of stdout.split('\n')) {
        const trimmed = line.trim();
        if (trimmed === '') continue;
        let entry: { role?: string; content?: unknown };
        try {
            entry = JSON.parse(trimmed) as typeof entry;
        } catch {
            // The CLI prints its version banner and other stray text on some
            // paths; a line that is not JSON is not an answer.
            continue;
        }
        if (entry.role === 'assistant' && typeof entry.content === 'string' && entry.content) {
            answer = entry.content;
        }
    }

    if (answer === null) {
        throw new Error(
            `Kimi CLI produced no answer. Check that it is signed in (run \`kimi\` and /login) and that its model accepts image input. Got: ${truncate(stdout)}`,
        );
    }

    const result = extractJson(answer);
    if (result === null) {
        throw new Error(`Kimi CLI returned non-JSON output: ${truncate(answer)}`);
    }

    // The ndjson carries no model or usage line, and inventing one would put
    // a guess where callers read a fact. Absent says unknown, which is true.
    return { result, meta: { conversationId: null, durationSeconds: null, usage: null } };
}

// Whatever the install made default: unlike the Claude CLI there is no
// obvious cheap tier to pin, and kimi refuses to run without a default_model
// of its own, so an unset model means "use the one the user chose".
export const KIMI_CLI_DEFAULT_MODEL = '';

export const kimiCliProvider: VisionProvider = {
    name: 'kimi-cli',
    defaultModel: KIMI_CLI_DEFAULT_MODEL,
    buildInvocation: buildKimiCliInvocation,
    parseOutput: parseKimiCliOutput,
    // Same reason claude-cli isolates: the agent runs with a real toolset, so
    // it gets a throwaway directory holding only the image.
    isolateWorkdir: true,
};
