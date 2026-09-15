import { execFileSync } from 'child_process';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

/**
 * Build the bundle once, before any suite runs.
 *
 * Two suites drive the real binary, and each used to build it itself. In
 * parallel that meant one of them launching the CLI during the moment vite had
 * emptied dist, which fails as a missing module and reads like an unrelated
 * bug. Building only when dist was absent traded that for something worse: a
 * suite testing yesterday's binary against today's source, and passing.
 */
export default function setup(): void {
    const root = resolve(dirname(fileURLToPath(import.meta.url)));
    // shell:true so Windows resolves `pnpm` to `pnpm.cmd` through PATHEXT.
    execFileSync('pnpm', ['build'], { cwd: root, stdio: 'ignore', shell: true });
}
