import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { describe, expect, it, vi } from 'vitest';

// A child process started from a host with no console of its own gets a console
// allocated for it, and Windows shows that console's window. The desktop app is
// such a host, so a read popped a black window per child until #60.
// `windowsHide` suppresses it, defaults to false in Node, and is ignored off
// Windows. The window cannot be asserted from here, since the option is a no-op
// on this platform and CI's Windows runners are headless.
//
// So the property asserted instead is that the option cannot be missing. An
// earlier version of this file scanned every call site for it, and a review
// found four ways past the scanner: a `windowsHide: false`, a call reached
// through a local alias, a matching string inside an unrelated option, and a
// later spread overriding the value. Reading call sites was the wrong shape.
// Creating a child now goes through one wrapper per shipped piece, each writing
// the option after the caller's, so there is no call site to inspect and
// nothing for the next person to remember.

vi.mock('child_process', () => ({
    spawn: vi.fn(() => ({ pid: 1 })),
    execFileSync: vi.fn(() => 'stdout'),
}));

const { execFileSync, spawn } = await import('child_process');
const { execFileSyncHidden, spawnHidden } = await import('./util/spawnHidden.ts');

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

/**
 * The only two files allowed to reach child_process. Two rather than one
 * because the dsh plugin ships as a unit and cannot import from the CLI it
 * drives. Each holds nothing but its wrapper, so a file that reaches
 * child_process and a file that starts children are the same list.
 */
const WRAPPERS = new Set(['src/util/spawnHidden.ts', 'dsh/spawnHidden.js']);

/**
 * Files that cannot start a process: pure data, prose, and type declarations
 * (the dsh wrapper's .d.ts names child_process in a type import, which is why
 * declarations are here). Everything NOT matched is inspected, so an extension
 * this list has never heard of lands in the check rather than past it: an
 * allowlist of executable extensions read the other way around, and a review
 * walked a .cjs helper straight through the gap it left.
 */
const INERT = /\.(json|md|ya?ml|d\.ts)$/;

/** Every shipped file that could run, tests excluded: they start no user-facing child. */
function shippedSources(): string[] {
    const found: string[] = [];
    const walk = (dir: string): void => {
        for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
            const full = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                walk(full);
                continue;
            }
            if (INERT.test(entry.name) || /\.test\./.test(entry.name)) continue;
            found.push(full);
        }
    };
    walk(path.join(root, 'src'));
    walk(path.join(root, 'dsh'));
    return found;
}

describe('no child process is started with a visible console (#60)', () => {
    it('writes windowsHide after the caller, so no call site can drop it', () => {
        vi.mocked(spawn).mockClear();
        vi.mocked(execFileSync).mockClear();

        // The signatures refuse the option, so this is the runtime asking for
        // the wrong thing on purpose: what reaches Node must be true anyway.
        spawnHidden('cmd', ['a'], {
            stdio: ['ignore', 'pipe', 'pipe'],
            windowsHide: false,
        } as never);
        execFileSyncHidden('cmd', ['a'], {
            encoding: 'utf-8',
            windowsHide: false,
        } as never);

        expect(vi.mocked(spawn).mock.calls[0][2]).toMatchObject({ windowsHide: true });
        expect(vi.mocked(execFileSync).mock.calls[0][2]).toMatchObject({ windowsHide: true });
    });

    it('keeps the caller options it was given', () => {
        vi.mocked(spawn).mockClear();

        spawnHidden('cmd', ['a', 'b'], { cwd: '/tmp', stdio: ['ignore', 'pipe', 'pipe'] });

        expect(vi.mocked(spawn).mock.calls[0][0]).toBe('cmd');
        expect(vi.mocked(spawn).mock.calls[0][1]).toEqual(['a', 'b']);
        expect(vi.mocked(spawn).mock.calls[0][2]).toMatchObject({ cwd: '/tmp' });
    });

    it('lets nothing but the wrappers reach child_process', () => {
        // This is the whole guarantee: a child started anywhere else is not a
        // call site that forgot the option, it is a file that cannot exist.
        const reaching = shippedSources()
            // Windows hands back backslashes, the allowlist speaks POSIX.
            .map((file) => path.relative(root, file).split(path.sep).join('/'))
            .filter((relative) => !WRAPPERS.has(relative))
            .filter((relative) =>
                /child_process/.test(fs.readFileSync(path.join(root, relative), 'utf-8')),
            );

        expect(reaching).toEqual([]);
    });

    it('forces the option in the dsh wrapper too, which ships separately', async () => {
        vi.mocked(spawn).mockClear();
        const dsh = await import('../dsh/spawnHidden.js');

        dsh.spawnHidden('cmd', ['a'], { stdio: 'ignore', windowsHide: false });

        expect(vi.mocked(spawn).mock.calls[0][2]).toMatchObject({ windowsHide: true });
    });
});
