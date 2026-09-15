// Windows cannot spawn what POSIX can. npm/pnpm/yarn install every JS CLI as
// a trio (a bare-named POSIX sh shim, a .cmd, a .ps1); a bare
// `spawn('claude')` finds none of them (ENOENT, read as "not installed"),
// and handing spawn the .cmd directly hits Node's post-CVE-2024-27980
// refusal to run batch files without a shell (EINVAL) — issue #31.
//
// Wrapping the .cmd in `cmd.exe /d /s /c` is not open to us: cmd's command
// line cannot carry a raw CR or LF, and our provider arguments are whole
// multi-line vision prompts, so a wrapped prompt is truncated at its first
// newline and anything after it is read as a second command. So the shim is
// read, and what it would have run is spawned directly.
//
// HOW that is decided changed completely after issue #43. The first design
// classified each line against a whitelist and reasoned about the ones it
// recognised. Six review rounds found six defects in it, every one the same
// shape: a line cannot be judged on its own, because whether it runs at all
// is a property of the file. The last was an `IF EXIST` whose condition is
// false, where cmd runs nothing and the old reader still produced a plan that
// spawned the provider. Trading a loud failure for a silent wrong action is
// worse than the bug being fixed.
//
// So this does not parse batch. It RECOGNISES the four shapes the two real
// generators emit, and each recognised shape carries its own closed recipe
// for what to spawn. There is no general block tree and no free composition,
// because free composition is where every defect lived. A file that is not
// one of the four is declined, and the caller's own spawn error stands.
//
// The existence test is the security-sensitive part. Its operand is never
// taken from the file: each recipe tests the one candidate the template is
// about to run, built from the shim's own directory, and the file's text has
// to match that candidate exactly. A path captured out of an untrusted file
// and handed to the filesystem is a file-existence oracle at best, and a UNC
// or device path turns a "check" into network I/O and authentication that
// reading a local shim never authorised.
import * as fs from 'fs';
import * as path from 'path';
import { findOnPath } from '../providers/availability.ts';
import {
    canonicalWindowsEnv,
    envValue,
    withoutWindowsEnvVariable,
    withWindowsEnvAssignment,
} from './winEnv.ts';

export interface SpawnPlan {
    command: string;
    args: string[];
    /**
     * The complete environment for the child, present only when the shim
     * would have changed it. Both generators edit PATHEXT on the branch that
     * runs a bare `node`, and the child can observe that, so a plan dropping
     * it would not be the spawn the shell performs.
     */
    env?: NodeJS.ProcessEnv;
}

/**
 * Three answers, not two. `fs.existsSync` folds a permission error, an I/O
 * failure and an odd reparse point into "absent", and absent is a decision
 * that changes which program runs. Anything that is not a clean yes or a
 * clean no declines the shim instead.
 */
export type Existence = 'present' | 'directory' | 'absent' | 'unknown';

/** Exported for tests: the predicate is where directory-blindness lived. */
export function existenceOf(target: string): Existence {
    try {
        return fs.statSync(target).isDirectory() ? 'directory' : 'present';
    } catch (error) {
        return (error as NodeJS.ErrnoException).code === 'ENOENT' ? 'absent' : 'unknown';
    }
}

/**
 * PATH elements the way the Windows search reads them: `;` splits only
 * outside quotes, and the quotes themselves are not part of the directory
 * name. Handing the quoted spelling to the filesystem probed a directory
 * that does not exist, which silently deleted the entry from the search
 * and ran whichever node the next entry held.
 */
function splitWindowsPath(pathValue: string): string[] {
    const entries: string[] = [];
    let current = '';
    let inQuotes = false;
    for (const char of pathValue) {
        if (char === '"') {
            inQuotes = !inQuotes;
            continue;
        }
        if (char === ';' && !inQuotes) {
            if (current) entries.push(current);
            current = '';
            continue;
        }
        current += char;
    }
    if (current) entries.push(current);
    return entries;
}

export interface ResolveDeps {
    platform: NodeJS.Platform;
    readFileSync: (p: string) => string;
    resolveOnPath: (bin: string, env: NodeJS.ProcessEnv) => string | null;
    existence: (p: string) => Existence;
}

const REAL_DEPS: ResolveDeps = {
    platform: process.platform,
    readFileSync: (p) => fs.readFileSync(p, 'utf-8'),
    resolveOnPath: findOnPath,
    existence: existenceOf,
};

/** What a recognised template decided to run. */
interface Recipe {
    command: string;
    args: string[];
    env?: NodeJS.ProcessEnv;
}

/** The PATHEXT edit both generators write, and only in this exact form. */
const PATHEXT_EDIT = /^@?SET PATHEXT=%PATHEXT:;\.([A-Z]+);=;%$/;

/**
 * Apply cmd's case-insensitive PATHEXT substring replacement, as the
 * assignment it really is.
 *
 * `SET NAME=` with nothing after it deletes the variable rather than leaving
 * it empty, and the difference is not cosmetic here: an empty PATHEXT yields
 * no extension candidates, so the bare lookup would test only an
 * extensionless `node` and decline, while cmd falls back to its own default
 * list and still finds node.exe. The child would also see a variable cmd's
 * child does not have.
 */
function withPathextEdit(env: NodeJS.ProcessEnv, removed: string): NodeJS.ProcessEnv {
    const canonical = canonicalWindowsEnv(env);
    const key = Object.keys(canonical).find((name) => name.toUpperCase() === 'PATHEXT');
    const current = key === undefined ? '' : (canonical[key] ?? '');
    const needle = new RegExp(`;\\.${removed};`, 'gi');
    const edited = current.replace(needle, ';');
    if (edited === '') {
        return withoutWindowsEnvVariable(canonical, 'PATHEXT');
    }
    return withWindowsEnvAssignment(canonical, 'PATHEXT', edited);
}

const DEFAULT_PATHEXT = '.COM;.EXE;.BAT;.CMD';

/**
 * Resolve a bare command the way cmd would. cmd tries the current directory
 * before PATH unless NoDefaultCurrentDirectoryInExePath is set, and in each
 * directory it tries the PATHEXT extensions before the bare name itself.
 * Searching PATH alone, or preferring the bare name, can choose a different
 * file than the shell.
 *
 * A hit that is itself a batch file is refused: spawning it directly is the
 * EINVAL this whole module exists to route around, and there is no second
 * shim to read.
 */
function resolveLikeCmd(
    name: string,
    env: NodeJS.ProcessEnv,
    cwd: string | undefined,
    deps: ResolveDeps,
): string | null {
    const effectiveEnv = canonicalWindowsEnv(env);
    const exts = (
        Object.entries(effectiveEnv).find(([key]) => key.toUpperCase() === 'PATHEXT')?.[1] ??
        DEFAULT_PATHEXT
    )
        .split(';')
        .map((ext) => ext.trim())
        .filter(Boolean);
    const skipCwd = Object.keys(effectiveEnv).some(
        (key) => key.toUpperCase() === 'NODEFAULTCURRENTDIRECTORYINEXEPATH',
    );
    const pathValue =
        Object.entries(effectiveEnv).find(([key]) => key.toUpperCase() === 'PATH')?.[1] ?? '';
    const effectiveCwd = cwd ?? process.cwd();
    const dirs = [
        ...(skipCwd ? [] : [effectiveCwd]),
        ...splitWindowsPath(pathValue).map((dir) => path.win32.resolve(effectiveCwd, dir)),
    ];
    for (const dir of dirs) {
        // Extensions first, the bare name last. Windows CI settled this: with
        // PATHEXT=.EXE and both `node` and `node.EXE` present, real cmd runs
        // node.EXE. It also matches what issue #30 found the hard way, since
        // npm installs a bare-named POSIX shim beside the real executable and
        // resolving that first hands spawn a file Windows cannot run.
        for (const suffix of [...exts, '']) {
            const candidate = path.win32.join(dir, `${name}${suffix}`);
            const found = deps.existence(candidate);
            if (found === 'unknown') {
                return null;
            }
            // A directory that happens to carry the name is skipped and the
            // search continues, which is what cmd does; counting it as the
            // winner handed spawn a directory while cmd ran the next hit.
            if (found === 'present') {
                return /\.(cmd|bat)$/i.test(candidate) ? null : candidate;
            }
        }
    }
    return null;
}

/**
 * A `%dp0%`/`%~dp0`-rooted path from a template, as an absolute path. Only
 * those two spellings and a plain absolute path are accepted, and nothing
 * else may remain: a surviving `%VAR%` is one cmd would expand from the
 * environment, and this does not reimplement cmd's expansion.
 */
function templatePath(text: string, shimDir: string): string | null {
    const rooted = /^%(?:dp0%|~dp0)\\?(.*)$/i.exec(text);
    if (!rooted) {
        // Only a drive-qualified local path: UNC and device paths pass
        // isAbsolute, and spawning one does strictly more than checking one.
        // No real generator writes them (cmd-shim roots everything in %dp0%,
        // and pnpm's pinned nodeExecPath is drive-qualified), so refusing
        // costs nothing that recognition was supposed to allow.
        return isFullyQualifiedLocalPath(text) && !text.includes('%') ? text : null;
    }
    const rest = rooted[1];
    if (rest.includes('%') || rest === '') {
        return null;
    }
    return path.win32.normalize(path.win32.join(shimDir, rest));
}

/**
 * Refuse the shim directories whose mere existence check reaches off this
 * machine or into a device namespace.
 */
function isFullyQualifiedLocalPath(target: string): boolean {
    return /^[A-Za-z]:[\\/]/.test(target);
}

/** Interpreter flags a shebang can carry, conservatively. */
const FLAG = /^--?[A-Za-z0-9][-A-Za-z0-9._]*(?:=[-A-Za-z0-9._/\\:]+)?$/;

/**
 * Split the tokens a template puts between the interpreter and `%*`: any
 * number of plain flags, then exactly one quoted template path, the script
 * being launched. Anything else is not one of these templates.
 */
function interpreterTail(middle: string, shimDir: string): string[] | null {
    const tokens = middle
        .trim()
        .split(/\s+/)
        .filter((token) => token !== '');
    if (tokens.length === 0) {
        return null;
    }
    const quoted = /^"([^"]*)"$/.exec(tokens[tokens.length - 1]);
    if (!quoted) {
        return null;
    }
    const entry = templatePath(quoted[1], shimDir);
    if (entry === null) {
        return null;
    }
    const flags = tokens.slice(0, -1);
    return flags.every((flag) => FLAG.test(flag)) ? [...flags, entry] : null;
}

/**
 * The Node choice, given the environment that is actually in force when the
 * program starts. That environment differs between the three templates, which
 * is the whole reason they cannot share one recipe:
 *
 * - npm 4.1.0 through 9.0.1 put the PATHEXT edit inside the ELSE block, which
 *   is inside SETLOCAL, and the execution line begins with `endLocal`. The
 *   edit is therefore undone before the lookup and before the child starts.
 *   npm fixed exactly this in 9.0.2 (npm/cmd-shim#64), so honouring the edit
 *   here would reproduce a bug the shim does not have.
 * - npm 9.0.2 moved it onto the execution line after `endLocal`, where it
 *   applies, and applies on both arms because the line is shared.
 * - pnpm puts it inside the ELSE block and never calls endlocal, so it
 *   applies, but only on that arm.
 *
 * The candidate tested for the conditional is the one about to be run, built
 * from the shim's own directory, and the arm not taken is never consulted.
 */
function nodeRecipe(
    shimDir: string,
    tail: string[],
    effective: { present: NodeJS.ProcessEnv; absent: NodeJS.ProcessEnv },
    env: NodeJS.ProcessEnv,
    cwd: string | undefined,
    deps: ResolveDeps,
): Recipe | null {
    const local = path.win32.join(shimDir, 'node.exe');
    const found = deps.existence(local);
    if (found === 'unknown') {
        return null;
    }
    // IF EXIST matches directories too, so a directory named node.exe takes
    // this arm exactly as it would under cmd, and the spawn fails the same
    // way cmd's would. Only the PATH lookup is pickier than IF EXIST.
    if (found === 'present' || found === 'directory') {
        return {
            command: local,
            args: tail,
            ...(effective.present === env ? {} : { env: effective.present }),
        };
    }
    // cmd resolves `node` at this moment, under the environment this arm has
    // in force. Reaching for process.execPath instead would run a different
    // Node than the shell whenever a portable install, an overridden PATH or
    // a node in the working directory is in play.
    const resolved = resolveLikeCmd('node', effective.absent, cwd, deps);
    return resolved === null
        ? null
        : {
              command: resolved,
              args: tail,
              ...(effective.absent === env ? {} : { env: effective.absent }),
          };
}

const NPM_PROLOGUE = [
    '@ECHO off',
    'GOTO start',
    ':find_dp0',
    'SET dp0=%~dp0',
    'EXIT /b',
    ':start',
    'SETLOCAL',
    'CALL :find_dp0',
];

// Every generator writes whitespace before %*, and requiring it matters: cmd
// expands %* in place, so a hand-glued `"...cli.js"%*` concatenates the first
// caller argument onto the script path while a split argv would not.
const NPM_PREFIX = 'endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & ';
/** 4.1.0 through 9.0.1: nothing between the prefix and the interpreter. */
const NPM_EXEC_LEGACY = /^"%_prog%"(.*)\s%\*$/;
/** 9.0.2 onwards: the PATHEXT edit rides the execution line, after endLocal. */
const NPM_EXEC_CURRENT = /^set PATHEXT=%PATHEXT:;\.([A-Z]+);=;% & "%_prog%"(.*)\s%\*$/;
const NPM_NATIVE_EXEC = /^"([^"]*)"\s+%\*$/;
// pnpm's optional NODE_PATH preamble, four lines between @SETLOCAL and the
// rest, emitted whenever extendNodePath is on, which is pnpm's default with
// the isolated linker. The value is taken verbatim and only ever placed into
// the child's environment, exactly where the shim itself puts it; %% is
// refused because a surviving expansion is one cmd would perform and this
// module does not reimplement cmd's expansion.
const PNPM_NODE_PATH_IF = /^@IF NOT DEFINED NODE_PATH \($/;
const PNPM_NODE_PATH_SET = /^@SET "NODE_PATH=([^"%]+)"$/;
const PNPM_NODE_PATH_PREPEND = /^@SET "NODE_PATH=([^"%]+);%NODE_PATH%"$/;
const PNPM_IF = /^@IF EXIST "([^"]*)" \($/;
const PNPM_ARM = /^"([^"]*)"(.*)\s%\*$/;
const PNPM_BARE_ARM = /^node(.*)\s%\*$/;
const PNPM_ONELINE = /^@"([^"]*)"(.*)\s%\*$/;

/**
 * Trim each line and drop the trailing blank ones. Leading indentation is
 * decoration inside these templates (cmd ignores it), and the token splitting
 * below works off internal whitespace, so nothing meaningful is lost.
 */
function normalizeLines(content: string): string[] {
    const lines = content.split(/\r?\n/).map((line) => line.trim());
    while (lines.length > 0 && lines[lines.length - 1] === '') {
        lines.pop();
    }
    return lines;
}

/**
 * npm's two shapes. The prologue is fixed, and its jump lands on a label the
 * prologue itself defines, so the lines after it do run. That is checked as
 * one block rather than line by line, which is the whole point.
 */
function matchNpm(
    lines: string[],
    shimDir: string,
    env: NodeJS.ProcessEnv,
    cwd: string | undefined,
    deps: ResolveDeps,
): Recipe | null {
    if (lines.length < NPM_PROLOGUE.length) {
        return null;
    }
    if (!NPM_PROLOGUE.every((expected, index) => lines[index] === expected)) {
        return null;
    }
    const body = lines.slice(NPM_PROLOGUE.length).filter((line) => line !== '');

    // Native: the program, and nothing else.
    if (body.length === 1) {
        const native = NPM_NATIVE_EXEC.exec(body[0]);
        if (!native) {
            return null;
        }
        const target = templatePath(native[1], shimDir);
        if (target === null || !/\.exe$/i.test(target)) {
            return null;
        }
        const normalizedDir = path.win32.normalize(shimDir);
        const dp0 = normalizedDir.endsWith('\\') ? normalizedDir : `${normalizedDir}\\`;
        return {
            command: target,
            args: [],
            env: withWindowsEnvAssignment(env, 'dp0', dp0),
        };
    }

    // Node, in one of the two npm eras. They differ only in where the PATHEXT
    // edit sits, and that decides whether it reaches the child at all, so
    // they are two templates rather than one with a hole in it.
    if (body[0] !== 'IF EXIST "%dp0%\\node.exe" (') return null;
    if (body[1] !== 'SET "_prog=%dp0%\\node.exe"') return null;
    if (body[2] !== ') ELSE (') return null;
    if (body[3] !== 'SET "_prog=node"') return null;

    if (body.length === 7) {
        // 4.1.0 through 9.0.1: the edit is inside SETLOCAL and the execution
        // line begins with endLocal, so it is gone before anything runs.
        if (!PATHEXT_EDIT.test(body[4])) return null;
        if (body[5] !== ')') return null;
        if (!body[6].startsWith(NPM_PREFIX)) return null;
        const exec = NPM_EXEC_LEGACY.exec(body[6].slice(NPM_PREFIX.length));
        if (!exec) return null;
        const tail = interpreterTail(exec[1], shimDir);
        return tail === null
            ? null
            : nodeRecipe(shimDir, tail, { present: env, absent: env }, env, cwd, deps);
    }

    if (body.length === 6) {
        // 9.0.2 onwards: the edit moved after endLocal onto the shared line,
        // so it applies, and applies whichever arm was taken.
        if (body[4] !== ')') return null;
        if (!body[5].startsWith(NPM_PREFIX)) return null;
        const exec = NPM_EXEC_CURRENT.exec(body[5].slice(NPM_PREFIX.length));
        if (!exec) return null;
        const tail = interpreterTail(exec[2], shimDir);
        if (tail === null) return null;
        const edited = withPathextEdit(env, exec[1]);
        return nodeRecipe(shimDir, tail, { present: edited, absent: edited }, env, cwd, deps);
    }

    return null;
}

/**
 * pnpm's two shapes, each optionally led by the NODE_PATH preamble peeled
 * off below (the default isolated-linker layout). Still declined: the
 * optional PATH preamble prependToPath emits, a non-default option whose
 * reproduction would also have to interpolate %PATH%; that decline is the
 * one recorded gap left here, and it is a smaller one than NODE_PATH was.
 */
function matchPnpm(
    lines: string[],
    shimDir: string,
    env: NodeJS.ProcessEnv,
    cwd: string | undefined,
    deps: ResolveDeps,
): Recipe | null {
    if (lines[0] !== '@SETLOCAL') {
        return null;
    }
    let body = lines.slice(1).filter((line) => line !== '');

    // The optional NODE_PATH preamble applies to whichever arm runs, so it
    // is peeled off here and folded into the base environment both arms
    // inherit. cmd's DEFINED cannot see an empty variable (SET NAME= deletes
    // it), so an empty value reads as not defined and is replaced, not
    // prepended. A preamble that starts like this shape but does not finish
    // it declines the shim: half a template is not a smaller template.
    let baseEnv = env;
    if (body.length > 0 && PNPM_NODE_PATH_IF.test(body[0])) {
        if (body.length < 5) return null;
        const set = PNPM_NODE_PATH_SET.exec(body[1]);
        const prepend = PNPM_NODE_PATH_PREPEND.exec(body[3]);
        if (!set || body[2] !== ') ELSE (' || !prepend || body[4] !== ')') return null;
        // Both branches must name the same directories, or the branch
        // changes more than whether a prepend happens.
        if (set[1] !== prepend[1]) return null;
        const currentValue = envValue(env, 'NODE_PATH', 'win32');
        const defined = currentValue !== undefined && currentValue !== '';
        baseEnv = withWindowsEnvAssignment(
            env,
            'NODE_PATH',
            defined ? `${set[1]};${currentValue}` : set[1],
        );
        body = body.slice(5);
    }

    // Native, or a pinned absolute Node: one line, no branch.
    if (body.length === 1) {
        const one = PNPM_ONELINE.exec(body[0]);
        if (!one) {
            return null;
        }
        const program = templatePath(one[1], shimDir);
        if (program === null) {
            return null;
        }
        const onelineEnv = baseEnv === env ? {} : { env: baseEnv };
        if (one[2].trim() === '') {
            return /\.exe$/i.test(program) ? { command: program, args: [], ...onelineEnv } : null;
        }
        const tail = interpreterTail(one[2], shimDir);
        return tail === null || /\.(cmd|bat)$/i.test(program)
            ? null
            : { command: program, args: tail, ...onelineEnv };
    }

    // The Node choice.
    if (body.length !== 6) {
        return null;
    }
    const opened = PNPM_IF.exec(body[0]);
    if (!opened) return null;
    const local = path.win32.join(shimDir, 'node.exe');
    const candidate = templatePath(opened[1], shimDir);
    if (candidate === null || candidate.toLowerCase() !== local.toLowerCase()) {
        return null;
    }
    const present = PNPM_ARM.exec(body[1]);
    if (!present) return null;
    const presentProgram = templatePath(present[1], shimDir);
    if (presentProgram === null || presentProgram.toLowerCase() !== local.toLowerCase()) {
        return null;
    }
    if (body[2] !== ') ELSE (') return null;
    const edit = PATHEXT_EDIT.exec(body[3]);
    if (!edit) return null;
    const absent = PNPM_BARE_ARM.exec(body[4]);
    if (!absent) return null;
    if (body[5] !== ')') return null;

    const tail = interpreterTail(present[2], shimDir);
    const otherTail = interpreterTail(absent[1], shimDir);
    // Both arms must launch the same script. If they do not, the branch
    // changes more than which Node runs, and this template does not describe
    // what the file does.
    if (tail === null || otherTail === null || tail.join(' ') !== otherTail.join(' ')) {
        return null;
    }
    // pnpm never calls endlocal, so its edit survives to the child, but it is
    // written inside the ELSE block and so applies to that arm alone.
    return nodeRecipe(
        shimDir,
        tail,
        { present: baseEnv, absent: withPathextEdit(baseEnv, edit[1]) },
        env,
        cwd,
        deps,
    );
}

/**
 * What a `.cmd` shim would really run, or null when it is not one of the
 * recognised templates.
 */
export function recognizeShim(
    cmdPath: string,
    content: string,
    env: NodeJS.ProcessEnv,
    cwd?: string,
    deps: ResolveDeps = REAL_DEPS,
): Recipe | null {
    if (!isFullyQualifiedLocalPath(cmdPath)) {
        return null;
    }
    const shimDir = path.win32.dirname(cmdPath);
    const lines = normalizeLines(content);
    if (lines.length === 0) {
        return null;
    }
    return matchNpm(lines, shimDir, env, cwd, deps) ?? matchPnpm(lines, shimDir, env, cwd, deps);
}

/**
 * Turn a provider invocation into something the current platform can spawn.
 * POSIX passes through untouched. On Windows a bare name resolves through
 * PATH and PATHEXT to the real file; a `.cmd`/`.bat` matching one of the four
 * generator templates becomes a direct spawn of what it would have run.
 * Anything else passes through, so the caller's own ENOENT/EINVAL is the one
 * that fires, naming the command.
 *
 * `env` must be the environment the child will actually receive. A planner
 * reading one environment while the child gets another is its own way for the
 * plan and the shell to disagree.
 */
export function resolveSpawnPlan(
    command: string,
    args: string[],
    env: NodeJS.ProcessEnv = process.env,
    cwd?: string,
    deps: ResolveDeps = REAL_DEPS,
): SpawnPlan {
    if (deps.platform !== 'win32') {
        return { command, args };
    }
    let resolved = command;
    if (!command.includes('/') && !command.includes('\\')) {
        resolved = deps.resolveOnPath(command, env) ?? command;
    }
    if (!/\.(cmd|bat)$/i.test(path.win32.basename(resolved))) {
        return { command: resolved, args };
    }
    // This check precedes every read and existence probe. A UNC or device
    // path can perform network authentication or device I/O merely by being
    // opened, while root-relative and drive-relative paths do not name the
    // same file independently of process state.
    if (!isFullyQualifiedLocalPath(resolved)) {
        return { command: resolved, args };
    }
    let content: string;
    try {
        content = deps.readFileSync(resolved);
    } catch {
        return { command: resolved, args };
    }
    const recipe = recognizeShim(resolved, content, env, cwd, deps);
    if (recipe === null) {
        return { command: resolved, args };
    }
    // Every recognised template runs exactly one program. None of the four
    // has a reachable path that runs nothing, so there is no "would not have
    // run it" outcome to report yet. If a template ever has one, it needs an
    // answer of its own rather than being folded into the passthrough above,
    // which would turn a quiet exit into EINVAL.
    return {
        command: recipe.command,
        args: [...recipe.args, ...args],
        ...(recipe.env ? { env: recipe.env } : {}),
    };
}
