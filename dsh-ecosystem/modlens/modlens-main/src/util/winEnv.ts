// One rule for reading and folding environment variables on Windows, shared
// by everything that has to agree about them: the outer bare-command lookup,
// the inner Node lookup inside a shim recipe, and the environment a plan
// finally hands the child. Three places deciding this separately is how a
// planner ends up reading one PATH while the child receives another.
//
// Two facts drive it. Windows treats names case-insensitively, so `Path` and
// `PATH` are one variable; and Node, when it builds a custom child
// environment for Windows, sorts the keys and passes the first
// case-insensitive match. `process.env` already behaves this way on Windows,
// but a plain object built by spreading it does not, and that difference is
// invisible until a machine spells the key the other way.

/**
 * Read a variable the way the platform does: by exact name on POSIX, where
 * names are case-sensitive, and by folded name on Windows.
 *
 * The platform gate matters. Accepting `Path` on POSIX would let a scrubbed
 * environment that defines no `PATH` execute a program found through a
 * variable POSIX does not define as the command search path.
 */
export function envValue(
    env: NodeJS.ProcessEnv,
    name: string,
    platform: NodeJS.Platform = process.platform,
): string | undefined {
    if (platform !== 'win32') {
        return env[name];
    }
    const key = windowsKeyFor(env, name);
    return key === undefined ? undefined : env[key];
}

/**
 * Which spelling of `name` Node would pass to a Windows child: the keys are
 * sorted and the first case-insensitive match wins, so insertion order must
 * not decide it.
 */
export function windowsKeyFor(env: NodeJS.ProcessEnv, name: string): string | undefined {
    const folded = name.toUpperCase();
    return enumerateEnvKeys(env)
        .sort()
        .find((candidate) => candidate.toUpperCase() === folded);
}

/**
 * Every key Node would see. It enumerates a custom child environment with
 * `for...in`, which deliberately includes enumerable prototype properties, so
 * `Object.keys` would silently drop variables the child really receives.
 */
function enumerateEnvKeys(env: NodeJS.ProcessEnv): string[] {
    const keys: string[] = [];
    for (const key in env) {
        keys.push(key);
    }
    return keys;
}

/**
 * Fold a plain object into the environment Node would actually give a Windows
 * child: one entry per name, the winning spelling kept, undefined values
 * dropped the way the child environment block drops them.
 */
export function canonicalWindowsEnv(env: NodeJS.ProcessEnv): NodeJS.ProcessEnv {
    const seen = new Set<string>();
    const entries: [string, string][] = [];
    for (const key of enumerateEnvKeys(env).sort()) {
        const folded = key.toUpperCase();
        if (seen.has(folded)) {
            continue;
        }
        seen.add(folded);
        const value = env[key];
        if (value !== undefined) {
            entries.push([key, value]);
        }
    }
    return Object.fromEntries(entries);
}

/**
 * Assign one variable without leaving a second spelling of it behind, which
 * would show the child two answers and let key order pick between them.
 */
export function withWindowsEnvAssignment(
    env: NodeJS.ProcessEnv,
    name: string,
    value: string,
): NodeJS.ProcessEnv {
    const canonical = canonicalWindowsEnv(env);
    const key = windowsKeyFor(canonical, name) ?? name;
    const folded = name.toUpperCase();
    const rest = Object.fromEntries(
        Object.entries(canonical).filter(([candidate]) => candidate.toUpperCase() !== folded),
    );
    return { ...rest, [key]: value };
}

/** Remove every spelling of a variable, which is what `SET NAME=` does. */
export function withoutWindowsEnvVariable(env: NodeJS.ProcessEnv, name: string): NodeJS.ProcessEnv {
    const folded = name.toUpperCase();
    return Object.fromEntries(
        Object.entries(canonicalWindowsEnv(env)).filter(
            ([candidate]) => candidate.toUpperCase() !== folded,
        ),
    );
}
