import * as childProcess from 'child_process';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { describe, expect, it } from 'vitest';
import { type Existence, existenceOf, recognizeShim, resolveSpawnPlan } from './winExec.ts';

// Every fixture here is verbatim output from a real generator, each version
// installed in its own directory so one cannot quietly overwrite another:
// `cmd-shim` 4.1.0, 9.0.1 and 9.0.2 run directly, and `@zkochan/cmd-shim`
// 9.0.7 read out of its own generateCmdShim source, because that one only
// writes the .cmd on win32. Hand-written fixtures are what let six rounds of
// defects hide: they agreed with the parser because the same head wrote both.

/**
 * npm 4.1.0 and 9.0.1, byte-identical. The PATHEXT edit is inside the ELSE
 * block, which is inside SETLOCAL, and the execution line begins with
 * `endLocal`: the edit is undone before the lookup and before the child
 * starts. npm fixed that in 9.0.2 (npm/cmd-shim#64).
 */
const NPM_NODE_LEGACY = `@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0

IF EXIST "%dp0%\\node.exe" (
  SET "_prog=%dp0%\\node.exe"
) ELSE (
  SET "_prog=node"
  SET PATHEXT=%PATHEXT:;.JS;=;%
)

endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & "%_prog%"  "%dp0%\\..\\pkg\\cli.js" %*`;

/**
 * npm 9.0.2: no PATHEXT inside the block, and the edit moved onto the
 * execution line after `endLocal`, where it does reach the child, on either
 * arm, because the line is shared.
 */
const NPM_NODE_CURRENT = `@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0

IF EXIST "%dp0%\\node.exe" (
  SET "_prog=%dp0%\\node.exe"
) ELSE (
  SET "_prog=node"
)

endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & set PATHEXT=%PATHEXT:;.JS;=;% & "%_prog%"  "%dp0%\\..\\pkg\\cli.js" %*`;

/** npm, a compiled binary. Identical in 4.1.0 and 9.0.2. */
const NPM_NATIVE = `@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0
"%dp0%\\..\\pkg\\prog.exe"   %*`;

/** pnpm, a Node entry. */
const PNPM_NODE = `@SETLOCAL
@IF EXIST "%~dp0\\node.exe" (
  "%~dp0\\node.exe"  "%~dp0\\..\\pkg\\cli.js" %*
) ELSE (
  @SET PATHEXT=%PATHEXT:;.JS;=;%
  node  "%~dp0\\..\\pkg\\cli.js" %*
)`;

/** pnpm, a compiled binary. */
const PNPM_NATIVE = `@SETLOCAL
@"%~dp0\\..\\pkg\\prog.exe"   %*`;

/** pnpm with nodeExecPath: one pinned absolute Node, no branch. */
const PNPM_PINNED = `@SETLOCAL
@"C:\\runtimes\\node20\\node.exe"  "%~dp0\\..\\pkg\\cli.js" %*`;

const SHIM = 'C:\\proj\\node_modules\\.bin\\thing.CMD';
const SHIM_DIR = 'C:\\proj\\node_modules\\.bin';

interface DepOverrides {
    existence?: (p: string) => Existence;
    resolveOnPath?: (bin: string) => string | null;
    readFileSync?: () => string;
}

function deps(overrides: DepOverrides = {}) {
    return {
        platform: 'win32' as NodeJS.Platform,
        readFileSync: overrides.readFileSync ?? (() => ''),
        resolveOnPath: overrides.resolveOnPath ?? ((bin: string) => `C:\\path\\${bin}.exe`),
        existence: overrides.existence ?? ((): Existence => 'absent'),
    };
}

/** An existence stub where exactly one path is there. */
const onlyPresent =
    (target: string) =>
    (probe: string): Existence =>
        probe.toLowerCase() === target.toLowerCase() ? 'present' : 'absent';

const recognize = (
    content: string,
    overrides: DepOverrides = {},
    env: NodeJS.ProcessEnv = {},
    cwd?: string,
) => recognizeShim(SHIM, content, env, cwd, deps(overrides));

const resolveShim = (
    content: string,
    overrides: DepOverrides = {},
    env: NodeJS.ProcessEnv = {},
    cwd?: string,
    args: string[] = [],
) =>
    resolveSpawnPlan('thing', args, env, cwd, {
        ...deps(overrides),
        readFileSync: () => content,
        resolveOnPath: () => SHIM,
    });

describe('the four real generator templates', () => {
    it('npm Node, with the Node beside the shim present', () => {
        const recipe = resolveShim(NPM_NODE_LEGACY, { existence: () => 'present' });
        expect(recipe).toEqual({
            command: `${SHIM_DIR}\\node.exe`,
            args: ['C:\\proj\\node_modules\\pkg\\cli.js'],
        });
    });

    it('npm 4.1.0 and 9.0.1 fall back without the PATHEXT edit', () => {
        // The edit sits inside SETLOCAL and endLocal runs first, so cmd looks
        // node up under the ORIGINAL environment and the child gets it
        // unchanged. Honouring the edit would reproduce the bug npm fixed.
        const recipe = resolveShim(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\nodejs\\node.EXE') },
            { PATHEXT: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' },
        );
        expect(recipe?.command).toBe('C:\\nodejs\\node.EXE');
        expect(recipe?.args).toEqual(['C:\\proj\\node_modules\\pkg\\cli.js']);
        expect(recipe?.env).toBeUndefined();
    });

    it('npm 9.0.2 carries the edit, on whichever arm ran', () => {
        // Moved after endLocal and onto the shared line, so it survives and
        // is not branch-local.
        const env = { PATHEXT: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' };
        const present = resolveShim(NPM_NODE_CURRENT, { existence: () => 'present' }, env);
        expect(present?.command).toBe(`${SHIM_DIR}\\node.exe`);
        expect(present?.env?.PATHEXT).toBe('.COM;.EXE;.VBS');

        const absent = resolveShim(
            NPM_NODE_CURRENT,
            { existence: onlyPresent('C:\\nodejs\\node.EXE') },
            env,
        );
        expect(absent?.command).toBe('C:\\nodejs\\node.EXE');
        expect(absent?.env?.PATHEXT).toBe('.COM;.EXE;.VBS');
    });

    it('npm native', () => {
        expect(resolveShim(NPM_NATIVE)).toEqual({
            command: 'C:\\proj\\node_modules\\pkg\\prog.exe',
            args: [],
            env: { dp0: `${SHIM_DIR}\\` },
        });
    });

    it('pnpm Node, both arms', () => {
        expect(resolveShim(PNPM_NODE, { existence: () => 'present' })).toEqual({
            command: `${SHIM_DIR}\\node.exe`,
            args: ['C:\\proj\\node_modules\\pkg\\cli.js'],
        });
        const onPath = resolveShim(
            PNPM_NODE,
            { existence: onlyPresent('C:\\nodejs\\node.EXE') },
            { PATHEXT: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' },
        );
        expect(onPath?.command).toBe('C:\\nodejs\\node.EXE');
        // pnpm never calls endlocal, so its edit does reach the child, but
        // only on this arm.
        expect(onPath?.env?.PATHEXT).toBe('.COM;.EXE;.VBS');
    });

    it('pnpm native', () => {
        expect(resolveShim(PNPM_NATIVE)).toEqual({
            command: 'C:\\proj\\node_modules\\pkg\\prog.exe',
            args: [],
        });
    });

    it('pnpm with a pinned Node runtime', () => {
        expect(resolveShim(PNPM_PINNED)).toEqual({
            command: 'C:\\runtimes\\node20\\node.exe',
            args: ['C:\\proj\\node_modules\\pkg\\cli.js'],
        });
    });

    it('carries shebang flags through in order', () => {
        const withFlags = NPM_NODE_LEGACY.replace(
            '"%_prog%"  "%dp0%\\..\\pkg\\cli.js" %*',
            '"%_prog%" --max-old-space-size=4096 --no-warnings "%dp0%\\..\\pkg\\cli.js" %*',
        );
        expect(recognize(withFlags, { existence: () => 'present' })?.args).toEqual([
            '--max-old-space-size=4096',
            '--no-warnings',
            'C:\\proj\\node_modules\\pkg\\cli.js',
        ]);
    });
});

describe('reachability decides, not line shape (#43)', () => {
    // The defect that withdrew this work from 3.17.1: cmd runs nothing when
    // the condition is false, and the old reader still produced a plan that
    // spawned the provider. A loud failure became a silent wrong action.
    it('does not treat a lone false branch as if it ran', () => {
        const singleBranch = `@IF EXIST "Z:\\not-here" (
  @node "C:\\pkg\\cli.js" %*
)`;
        expect(recognize(singleBranch)).toBeNull();
    });

    it('does not treat a nested false branch as if it ran', () => {
        const nested = `@IF EXIST "Z:\\not-here" (
  @IF EXIST "C:\\pkg\\cli.js" (
    @node "C:\\pkg\\cli.js" %*
  )
)`;
        expect(recognize(nested)).toBeNull();
    });

    it('does not accept a jump over the execution line', () => {
        const jumped = `GOTO done
@node "C:\\pkg\\cli.js" %*
:done`;
        expect(recognize(jumped)).toBeNull();
    });

    it('declines a template with an extra command spliced in', () => {
        const spliced = NPM_NODE_LEGACY.replace(
            'title %COMSPEC% & "%_prog%"',
            'title %COMSPEC% & whoami & "%_prog%"',
        );
        expect(recognize(spliced, { existence: () => 'present' })).toBeNull();
    });

    it('declines a template with an extra line added anywhere', () => {
        expect(recognize(`${NPM_NATIVE}\n@whoami`)).toBeNull();
        expect(recognize(`@whoami\n${PNPM_NATIVE}`)).toBeNull();
    });
});

describe('the existence test is narrow on purpose', () => {
    it('only ever tests the Node beside the shim', () => {
        const tested: string[] = [];
        recognize(NPM_NODE_LEGACY, {
            existence: (p) => {
                tested.push(p);
                return 'present';
            },
        });
        expect(tested).toEqual([`${SHIM_DIR}\\node.exe`]);
    });

    it('declines when the condition names anything else', () => {
        // The operand comes out of an untrusted file. Testing what it asks
        // for makes it a file-existence oracle, and a UNC or device path
        // makes a "check" reach the network.
        const elsewhere = PNPM_NODE.replace('"%~dp0\\node.exe" (', '"\\\\server\\share\\probe" (');
        expect(recognize(elsewhere, { existence: () => 'present' })).toBeNull();
    });

    it('declines a shim living on a UNC path outright', () => {
        expect(
            recognizeShim('\\\\server\\share\\bin\\thing.CMD', PNPM_NATIVE, {}, undefined, deps()),
        ).toBeNull();
    });

    it('declines when existence cannot be determined', () => {
        // A permission error is not an answer, and existsSync would call it
        // absent, which silently changes which Node runs.
        expect(recognize(NPM_NODE_LEGACY, { existence: () => 'unknown' })).toBeNull();
    });

    it('declines when the bare node it would fall back to is not findable', () => {
        // cmd would fail here too. Reaching for our own binary instead would
        // run a different Node than the shell.
        expect(
            recognize(NPM_NODE_LEGACY, { existence: () => 'absent', resolveOnPath: () => null }),
        ).toBeNull();
    });
});

describe('tokens must be provably literal', () => {
    it('declines an entry cmd would expand from the environment', () => {
        expect(
            recognize(NPM_NODE_LEGACY.replace('%dp0%\\..\\pkg\\cli.js', '%TARGET%\\cli.js'), {
                existence: () => 'present',
            }),
        ).toBeNull();
    });

    it('declines an entry named by a positional parameter', () => {
        expect(
            recognize(NPM_NODE_LEGACY.replace('%dp0%\\..\\pkg\\cli.js', '%1\\cli.js'), {
                existence: () => 'present',
            }),
        ).toBeNull();
    });

    it('declines a PATHEXT edit carrying anything but an extension removal', () => {
        expect(
            recognize(NPM_NODE_LEGACY.replace(';.JS;=;%', ';.JS;=;anything at all %'), {
                existence: () => 'absent',
            }),
        ).toBeNull();
    });

    it('declines when the two pnpm arms launch different scripts', () => {
        const mismatched = PNPM_NODE.replace(
            '  node  "%~dp0\\..\\pkg\\cli.js" %*',
            '  node  "%~dp0\\..\\pkg\\other.js" %*',
        );
        expect(recognize(mismatched, { existence: () => 'absent' })).toBeNull();
    });
});

describe('resolveSpawnPlan', () => {
    it('passes everything through on POSIX', () => {
        const plan = resolveSpawnPlan('claude', ['-p', 'x'], {}, undefined, {
            ...deps(),
            platform: 'darwin' as NodeJS.Platform,
        });
        expect(plan).toEqual({ command: 'claude', args: ['-p', 'x'] });
    });

    it('appends the caller arguments after the template ones, unescaped', () => {
        const plan = resolveSpawnPlan('thing', ['-p', 'read this\nand this'], {}, undefined, {
            ...deps({ readFileSync: () => NPM_NODE_LEGACY, existence: () => 'present' }),
            resolveOnPath: () => SHIM,
        });
        expect(plan.command).toBe(`${SHIM_DIR}\\node.exe`);
        // Nothing goes through a shell, so a multi-line prompt stays one argv
        // entry rather than being cut at its first newline.
        expect(plan.args).toEqual([
            'C:\\proj\\node_modules\\pkg\\cli.js',
            '-p',
            'read this\nand this',
        ]);
    });

    it('leaves an unrecognised shim to the caller own spawn error', () => {
        const plan = resolveSpawnPlan('thing', ['-p', 'x'], {}, undefined, {
            ...deps({ readFileSync: () => '@whoami %*' }),
            resolveOnPath: () => SHIM,
        });
        expect(plan.command).toBe(SHIM);
        expect(plan.args).toEqual(['-p', 'x']);
        expect(plan.env).toBeUndefined();
    });

    it('is unchanged for a plain executable', () => {
        const plan = resolveSpawnPlan('C:\\tools\\agy.exe', ['-p'], {}, undefined, deps());
        expect(plan).toEqual({ command: 'C:\\tools\\agy.exe', args: ['-p'] });
    });

    it.each([
        'bin\\thing.cmd',
        'C:bin\\thing.cmd',
        '\\bin\\thing.cmd',
        '\\\\server\\share\\thing.cmd',
        '\\\\?\\C:\\bin\\thing.cmd',
        '\\\\.\\PIPE\\thing.cmd',
    ])('refuses %s before reading it', (command) => {
        const reads: string[] = [];
        const probes: string[] = [];
        const plan = resolveSpawnPlan(command, ['rem noop'], {}, undefined, {
            ...deps(),
            readFileSync: (target) => {
                reads.push(target);
                return PNPM_NATIVE;
            },
            existence: (target) => {
                probes.push(target);
                return 'present';
            },
        });
        expect(reads, command).toEqual([]);
        expect(probes, command).toEqual([]);
        expect(plan, command).toEqual({ command, args: ['rem noop'] });
    });

    it('declines a false branch through the stable planner entry point', () => {
        const singleBranch = `@IF EXIST "Z:\\not-here" (
  @node "C:\\pkg\\cli.js" %*
)`;
        expect(resolveShim(singleBranch, {}, {}, undefined, ['placeholder'])).toEqual({
            command: SHIM,
            args: ['placeholder'],
        });
    });
});

describe('the bare node lookup is cmd lookup (#43)', () => {
    const env = { PATHEXT: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' };

    it('tries the working directory before PATH, the way cmd does', () => {
        const recipe = recognize(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\work\\node.EXE') },
            env,
            'C:\\work',
        );
        expect(recipe?.command).toBe('C:\\work\\node.EXE');
    });

    it('skips the working directory when Windows is told to', () => {
        // NoDefaultCurrentDirectoryInExePath is the documented opt-out, and
        // ignoring it would run a node the shell would not have.
        const recipe = recognize(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\work\\node.EXE') },
            { ...env, NoDefaultCurrentDirectoryInExePath: '1' },
            'C:\\work',
        );
        expect(recipe).toBeNull();
    });

    it('declines a hit that is itself a batch file', () => {
        // Spawning that directly is the EINVAL this module exists to avoid,
        // and there is no second shim to read.
        const recipe = recognize(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\nodejs\\node.CMD') },
            { PATHEXT: '.CMD', PATH: 'C:\\nodejs' },
        );
        expect(recipe).toBeNull();
    });

    it('declines when a probe cannot be answered', () => {
        expect(recognize(NPM_NODE_LEGACY, { existence: () => 'unknown' }, env)).toBeNull();
    });

    it('leaves one PATHEXT key behind, whatever case it arrived in', () => {
        const recipe = recognize(
            NPM_NODE_CURRENT,
            { existence: () => 'present' },
            { PathExt: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' },
        );
        const keys = Object.keys(recipe?.env ?? {}).filter(
            (key) => key.toLowerCase() === 'pathext',
        );
        expect(keys).toEqual(['PathExt']);
        expect(recipe?.env?.PathExt).toBe('.COM;.EXE;.VBS');
    });

    it('declines a shim path that is not absolute', () => {
        expect(recognizeShim('bin\\thing.CMD', PNPM_NATIVE, {}, undefined, deps())).toBeNull();
    });

    it('uses process.cwd when the child cwd is omitted', () => {
        const inheritedCwdNode = path.win32.join(process.cwd(), 'node.EXE');
        const plan = resolveShim(
            NPM_NODE_LEGACY,
            { existence: onlyPresent(inheritedCwdNode) },
            env,
        );
        expect(plan.command).toBe(inheritedCwdNode);
    });

    it('anchors a relative PATH entry to the child cwd', () => {
        const plan = resolveShim(
            NPM_NODE_LEGACY,
            {
                existence: (candidate) =>
                    ['C:\\work\\tools\\node.EXE', 'C:\\fallback\\node.EXE'].includes(candidate)
                        ? 'present'
                        : 'absent',
            },
            { PATHEXT: '.EXE', PATH: 'tools;C:\\fallback' },
            'C:\\work',
        );
        expect(plan.command).toBe('C:\\work\\tools\\node.EXE');
    });

    it('checks PATHEXT candidates before the bare name', () => {
        const probes: string[] = [];
        const plan = resolveShim(
            NPM_NODE_LEGACY,
            {
                existence: (candidate) => {
                    probes.push(candidate);
                    return candidate === 'C:\\tools\\node' || candidate === 'C:\\tools\\node.EXE'
                        ? 'present'
                        : 'absent';
                },
            },
            { PATHEXT: '.EXE', PATH: 'C:\\tools', NoDefaultCurrentDirectoryInExePath: '1' },
        );
        // Real cmd picks node.EXE when both exist, which the Windows
        // differential test below proves rather than assumes.
        expect(plan.command).toBe('C:\\tools\\node.EXE');
        expect(probes).toEqual([`${SHIM_DIR}\\node.exe`, 'C:\\tools\\node.EXE']);
    });

    it('reads duplicate PATH and PATHEXT keys the way Node passes them', () => {
        const plan = resolveShim(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\right\\node.EXE') },
            {
                Path: 'C:\\wrong',
                PATH: 'C:\\right',
                PathExt: '.CMD',
                PATHEXT: '.EXE',
                NoDefaultCurrentDirectoryInExePath: '1',
            },
        );
        expect(plan.command).toBe('C:\\right\\node.EXE');
    });

    it.skipIf(process.platform !== 'win32')(
        'runs the same program cmd runs, for the same shim',
        () => {
            // The one check neither reasoning nor a stubbed filesystem can
            // make: hand a real shim to a real cmd.exe, hand the same shim to
            // the planner, and require the two to end the same way. It
            // reports what cmd does rather than encoding a guess about it,
            // which is how the previous version of this test got the lookup
            // order backwards.
            const root = fs.mkdtempSync(path.join(os.tmpdir(), 'modlens-winexec-'));
            try {
                const work = path.join(root, 'work');
                const toolsDir = path.join(work, 'tools');
                const shimDir = path.join(root, 'shims');
                const pkgDir = path.join(root, 'pkg');
                fs.mkdirSync(toolsDir, { recursive: true });
                fs.mkdirSync(shimDir, { recursive: true });
                fs.mkdirSync(pkgDir, { recursive: true });

                // A distinctive exit code, so a run that merely starts
                // something cannot be mistaken for a run of the right thing.
                fs.writeFileSync(path.join(pkgDir, 'cli.js'), 'process.exit(7);\n');
                // Both candidates present, which is the case that decides the
                // order: an extensionless file and the real executable.
                fs.writeFileSync(path.join(toolsDir, 'node'), '@rem noop\r\n@exit /b 9\r\n');
                fs.copyFileSync(process.execPath, path.join(toolsDir, 'node.EXE'));
                const shim = path.join(shimDir, 'thing.cmd');
                fs.writeFileSync(shim, NPM_NODE_LEGACY);

                const env = {
                    ...process.env,
                    PATH: 'tools',
                    PATHEXT: '.EXE',
                    NoDefaultCurrentDirectoryInExePath: '1',
                };
                const comspec =
                    process.env.ComSpec ??
                    path.join(process.env.SystemRoot ?? 'C:\\Windows', 'System32', 'cmd.exe');
                const viaCmd = childProcess.spawnSync(comspec, ['/d', '/s', '/c', shim], {
                    cwd: work,
                    env,
                });

                const plan = resolveSpawnPlan(shim, [], env, work, {
                    platform: 'win32',
                    readFileSync: (target) => fs.readFileSync(target, 'utf-8'),
                    resolveOnPath: () => shim,
                    existence: (target) => {
                        try {
                            fs.statSync(target);
                            return 'present';
                        } catch (error) {
                            return (error as NodeJS.ErrnoException).code === 'ENOENT'
                                ? 'absent'
                                : 'unknown';
                        }
                    },
                });
                const direct = childProcess.spawnSync(plan.command, plan.args, {
                    cwd: work,
                    env: plan.env ?? env,
                });

                // The script ran, through whichever node cmd picked.
                expect(viaCmd.status).toBe(7);
                expect(direct.status).toBe(viaCmd.status);
            } finally {
                fs.rmSync(root, { recursive: true, force: true });
            }
        },
    );
});

describe('existence tells a directory from a file (review)', () => {
    it('reports a directory as directory, not present', () => {
        // The lookup skips directories; the predicate mapping both to
        // "present" is where spawn was handed a directory cmd would skip.
        const root = fs.mkdtempSync(path.join(os.tmpdir(), 'modlens-exist-'));
        const dir = path.join(root, 'node');
        fs.mkdirSync(dir);
        const file = path.join(root, 'node.exe');
        fs.writeFileSync(file, 'MZ');

        expect(existenceOf(dir)).toBe('directory');
        expect(existenceOf(file)).toBe('present');
        expect(existenceOf(path.join(root, 'missing'))).toBe('absent');
        fs.rmSync(root, { recursive: true, force: true });
    });
});

describe("pnpm's NODE_PATH preamble, the default isolated-linker layout", () => {
    // Verbatim from @zkochan/cmd-shim 9.0.7 with nodePath set, the block
    // pnpm emits whenever extendNodePath is on, which is its default.
    const PNPM_WITH_NODE_PATH = `@SETLOCAL
@IF NOT DEFINED NODE_PATH (
  @SET "NODE_PATH=C:\\proj\\node_modules\\.pnpm\\node_modules"
) ELSE (
  @SET "NODE_PATH=C:\\proj\\node_modules\\.pnpm\\node_modules;%NODE_PATH%"
)
@IF EXIST "%~dp0\\node.exe" (
  "%~dp0\\node.exe"  "%~dp0\\pkg2\\cli.js" %*
) ELSE (
  @SET PATHEXT=%PATHEXT:;.JS;=;%
  node  "%~dp0\\pkg2\\cli.js" %*
)`;

    const PNPM_NATIVE_WITH_NODE_PATH = `@SETLOCAL
@IF NOT DEFINED NODE_PATH (
  @SET "NODE_PATH=C:\\hoist"
) ELSE (
  @SET "NODE_PATH=C:\\hoist;%NODE_PATH%"
)
@"%~dp0\\pkg2\\tool2.exe"   %*`;

    const env = { PATHEXT: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' };

    it('recognises the node form and sets NODE_PATH when the child had none', () => {
        const recipe = recognize(
            PNPM_WITH_NODE_PATH,
            { existence: onlyPresent('C:\\proj\\node_modules\\.bin\\node.exe') },
            env,
        );

        expect(recipe?.command).toBe('C:\\proj\\node_modules\\.bin\\node.exe');
        expect(recipe?.args).toEqual(['C:\\proj\\node_modules\\.bin\\pkg2\\cli.js']);
        expect(recipe?.env?.NODE_PATH).toBe('C:\\proj\\node_modules\\.pnpm\\node_modules');
    });

    it('prepends to an existing NODE_PATH, whatever its spelling', () => {
        const recipe = recognize(
            PNPM_WITH_NODE_PATH,
            { existence: onlyPresent('C:\\proj\\node_modules\\.bin\\node.exe') },
            { ...env, Node_Path: 'D:\\already' },
        );

        const value = Object.entries(recipe?.env ?? {}).find(
            ([key]) => key.toLowerCase() === 'node_path',
        )?.[1];
        expect(value).toBe('C:\\proj\\node_modules\\.pnpm\\node_modules;D:\\already');
    });

    it('treats an empty NODE_PATH as undefined, the way cmd DEFINED does', () => {
        // SET NAME= deletes in cmd, so an empty-but-present variable is a
        // Node-side artifact cmd could never observe as defined.
        const recipe = recognize(
            PNPM_WITH_NODE_PATH,
            { existence: onlyPresent('C:\\proj\\node_modules\\.bin\\node.exe') },
            { ...env, NODE_PATH: '' },
        );

        expect(recipe?.env?.NODE_PATH).toBe('C:\\proj\\node_modules\\.pnpm\\node_modules');
    });

    it('keeps the PATHEXT edit on the bare-node arm alongside NODE_PATH', () => {
        const recipe = recognize(
            PNPM_WITH_NODE_PATH,
            { existence: onlyPresent('C:\\nodejs\\node.EXE') },
            env,
        );

        expect(recipe?.command).toBe('C:\\nodejs\\node.EXE');
        expect(recipe?.env?.NODE_PATH).toBe('C:\\proj\\node_modules\\.pnpm\\node_modules');
        const pathext = Object.entries(recipe?.env ?? {}).find(
            ([key]) => key.toLowerCase() === 'pathext',
        )?.[1];
        expect(pathext).toBe('.COM;.EXE;.VBS');
    });

    it('recognises the native form and carries NODE_PATH to the child', () => {
        const recipe = recognize(PNPM_NATIVE_WITH_NODE_PATH, {}, env);

        expect(recipe?.command).toBe('C:\\proj\\node_modules\\.bin\\pkg2\\tool2.exe');
        expect(recipe?.env?.NODE_PATH).toBe('C:\\hoist');
    });

    it('declines a preamble whose two branches name different directories', () => {
        const twisted = PNPM_WITH_NODE_PATH.replace('C:\\hoist', 'C:\\other').replace(
            'NODE_PATH=C:\\proj\\node_modules\\.pnpm\\node_modules;%NODE_PATH%',
            'NODE_PATH=C:\\elsewhere;%NODE_PATH%',
        );

        expect(
            recognize(
                twisted,
                { existence: onlyPresent('C:\\proj\\node_modules\\.bin\\node.exe') },
                env,
            ),
        ).toBeNull();
    });

    it('declines a preamble carrying an expansion it cannot perform', () => {
        const expanded = PNPM_WITH_NODE_PATH.replace(
            '@SET "NODE_PATH=C:\\proj\\node_modules\\.pnpm\\node_modules"',
            '@SET "NODE_PATH=%APPDATA%\\hoist"',
        );

        expect(
            recognize(
                expanded,
                { existence: onlyPresent('C:\\proj\\node_modules\\.bin\\node.exe') },
                env,
            ),
        ).toBeNull();
    });

    it('declines the preamble on an npm-shaped shim, where no generator writes it', () => {
        const grafted = `@ECHO off\n${PNPM_WITH_NODE_PATH.split('\n').slice(1).join('\n')}`;

        expect(
            recognize(
                grafted,
                { existence: onlyPresent('C:\\proj\\node_modules\\.bin\\node.exe') },
                env,
            ),
        ).toBeNull();
    });
});

describe('the lookup is as picky as cmd about what a hit is (review)', () => {
    const env = { PATHEXT: '.EXE', PATH: 'C:\\tools;C:\\nodejs' };

    it('skips a directory that carries the name and keeps searching', () => {
        // cmd requires an executable file; counting a directory as the winner
        // handed spawn C:\tools\node while cmd ran the node one entry later.
        const existence = (probe: string): Existence => {
            if (probe.toLowerCase() === 'c:\\tools\\node') return 'directory';
            if (probe.toLowerCase() === 'c:\\nodejs\\node.exe') return 'present';
            return 'absent';
        };
        const recipe = recognize(NPM_NODE_LEGACY, { existence }, env);

        expect(recipe?.command).toBe('C:\\nodejs\\node.EXE');
    });

    it('reads a quoted PATH entry the way the search does', () => {
        // cmd strips the quotes per element; probing the quoted spelling
        // deleted the entry from the search and ran another node entirely.
        const recipe = recognize(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\Program Files\\nodejs\\node.EXE') },
            { PATHEXT: '.EXE', PATH: '"C:\\Program Files\\nodejs";C:\\other' },
        );

        expect(recipe?.command).toBe('C:\\Program Files\\nodejs\\node.EXE');
    });

    it('keeps a quoted semicolon inside one PATH entry', () => {
        const recipe = recognize(
            NPM_NODE_LEGACY,
            { existence: onlyPresent('C:\\odd;dir\\node.EXE') },
            { PATHEXT: '.EXE', PATH: '"C:\\odd;dir";C:\\other' },
        );

        expect(recipe?.command).toBe('C:\\odd;dir\\node.EXE');
    });
});

describe('a target the file supplies stays on this machine (review)', () => {
    it('declines a UNC target in the native template', () => {
        // Spawning \\server\share does strictly more than checking it, and
        // no real generator writes one, so recognition refuses rather than
        // matching cmd into the network.
        const recipe = recognize('@SETLOCAL\n@"\\\\server\\share\\payload.exe"   %*');

        expect(recipe).toBeNull();
    });

    it('declines a device-qualified target even with a spawnable extension', () => {
        const recipe = recognize('@SETLOCAL\n@"\\\\.\\C:\\payload.exe"   %*');

        expect(recipe).toBeNull();
    });

    it('declines an entry glued to %*, which cmd would concatenate', () => {
        // cmd expands %* in place, so "...cli.js"%* runs cli.js-p for a first
        // argument of -p; a split argv is not that spawn, so decline.
        const glued = PNPM_NATIVE.replace('"   %*', '"%*');

        expect(recognize(glued)).toBeNull();
    });
});

describe('PATHEXT assignment semantics', () => {
    it('performs cmd string substitution case-insensitively', () => {
        const plan = resolveShim(
            NPM_NODE_CURRENT,
            { existence: () => 'present' },
            { PATHEXT: '.COM;.EXE;.js;.VBS' },
        );
        expect(plan.env?.PATHEXT).toBe('.COM;.EXE;.VBS');
    });

    it('edits the duplicate-key value Node would pass to cmd', () => {
        const plan = resolveShim(
            NPM_NODE_CURRENT,
            { existence: () => 'present' },
            {
                PathExt: '.COM;.js',
                PATHEXT: '.COM;.EXE;.JS;.VBS',
            },
        );
        const keys = Object.keys(plan.env ?? {}).filter((key) => key.toLowerCase() === 'pathext');
        expect(keys).toEqual(['PATHEXT']);
        expect(plan.env?.PATHEXT).toBe('.COM;.EXE;.VBS');
    });
});

describe('child environment fidelity', () => {
    it('carries npm native dp0 into the child environment', () => {
        const plan = resolveShim(NPM_NATIVE, {}, { EXISTING: 'kept' });
        expect(plan.env).toEqual({ EXISTING: 'kept', dp0: `${SHIM_DIR}\\` });
    });
});

describe('directly spawnable pinned programs', () => {
    it.each(['cmd', 'BAT'])('declines a pnpm pinned .%s program', (extension) => {
        const batchPinned = PNPM_PINNED.replace('node.exe', `node.${extension}`);
        expect(resolveShim(batchPinned, {}, {}, undefined, ['placeholder'])).toEqual({
            command: SHIM,
            args: ['placeholder'],
        });
    });
});

describe('an emptied PATHEXT is deleted, not blanked (#43)', () => {
    // cmd's `SET NAME=` removes the variable rather than leaving it empty.
    // The case that reaches it here is an environment with no PATHEXT at all:
    // the substitution has nothing to work on, and writing an empty key back
    // gave the bare lookup zero extension candidates, so it tested only an
    // extensionless `node` and declined, while cmd falls back to its own
    // default list and runs node.exe. The child also saw a variable cmd's
    // child does not have.
    const noPathext = { PATH: 'C:\\nodejs' };

    it('writes no PATHEXT when there was none to edit', () => {
        const plan = resolveShim(NPM_NODE_CURRENT, { existence: () => 'present' }, noPathext);
        expect(Object.keys(plan.env ?? {}).some((k) => k.toUpperCase() === 'PATHEXT')).toBe(false);
    });

    it('still finds node.exe on the fallback arm, through the default list', () => {
        const plan = resolveShim(
            NPM_NODE_CURRENT,
            { existence: onlyPresent('C:\\nodejs\\node.EXE') },
            noPathext,
        );
        expect(plan.command).toBe('C:\\nodejs\\node.EXE');
    });

    it('keeps a PATHEXT that the edit merely shortened', () => {
        // Only a genuinely empty result is a deletion. `.COM;.EXE;.JS;.VBS`
        // still has entries after `.JS` goes, so the variable stays.
        const plan = resolveShim(
            NPM_NODE_CURRENT,
            { existence: () => 'present' },
            { PATHEXT: '.COM;.EXE;.JS;.VBS', PATH: 'C:\\nodejs' },
        );
        expect(plan.env?.PATHEXT).toBe('.COM;.EXE;.VBS');
    });
});
