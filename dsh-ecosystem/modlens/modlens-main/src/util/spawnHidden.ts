// The only place in the core that starts a child process.
//
// A child started from a host with no console of its own gets one allocated,
// and Windows shows its window, so a read from a GUI host popped a black window
// per child (issue #60). `windowsHide` suppresses it, defaults to false, and is
// ignored off Windows.
//
// Going through here rather than passing the option at each call site makes the
// invariant structural: the option is written after the caller's options, so it
// cannot be dropped by a spread or a stale copy, and it cannot be forgotten by
// whoever adds the next child, because there is nothing to remember. `Omit`
// rejects the option in a fresh object literal; through a variable or a
// spread it compiles anyway (excess-property checks stop at literals), which
// is why the runtime write after the spread is the guarantee and the type is
// only a hint.
import {
    type ChildProcessByStdio,
    type ExecFileSyncOptionsWithStringEncoding,
    execFileSync,
    type SpawnOptionsWithStdioTuple,
    type StdioNull,
    type StdioPipe,
    spawn,
} from 'child_process';
import type { Readable } from 'stream';

/**
 * Typed for the one stdio shape the core uses, a closed stdin and both output
 * streams piped, so the streams stay non-null for the reader. A different shape
 * needs another overload here, which is a good place to have to stop and think.
 */
export function spawnHidden(
    command: string,
    args: readonly string[],
    options: Omit<SpawnOptionsWithStdioTuple<StdioNull, StdioPipe, StdioPipe>, 'windowsHide'>,
): ChildProcessByStdio<null, Readable, Readable> {
    return spawn(command, args, { ...options, windowsHide: true });
}

export function execFileSyncHidden(
    file: string,
    args: readonly string[],
    options: Omit<ExecFileSyncOptionsWithStringEncoding, 'windowsHide'>,
): string {
    return execFileSync(file, args, { ...options, windowsHide: true });
}
