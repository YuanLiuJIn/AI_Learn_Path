import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { afterEach, describe, expect, it } from 'vitest';
import { findOnPath, providerAvailable, providerChain } from './availability.ts';

const dirs: string[] = [];
afterEach(() => {
    while (dirs.length > 0) {
        fs.rmSync(dirs.pop() as string, { recursive: true, force: true });
    }
});

/** A PATH containing the named fake binaries and nothing else. */
function pathWith(...bins: string[]): string {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'modlens-avail-'));
    dirs.push(dir);
    for (const bin of bins) {
        fs.writeFileSync(path.join(dir, bin), '#!/bin/sh\nexit 0\n', { mode: 0o755 });
    }
    return dir;
}

const names = (chain: ReturnType<typeof providerChain>) => chain.map((p) => p.name);

describe('providerAvailable', () => {
    it('checks the binary on PATH for subprocess providers', () => {
        expect(providerAvailable('antigravity-cli', {}, { PATH: pathWith('agy') })).toBe(true);
        expect(providerAvailable('antigravity-cli', {}, { PATH: pathWith() })).toBe(false);
    });

    // Real Windows installs ship agy.exe / claude.cmd, never a bare-named
    // file; these run on the Windows CI matrix only.
    it.skipIf(process.platform !== 'win32')('finds Windows binaries via PATHEXT', () => {
        expect(providerAvailable('antigravity-cli', {}, { PATH: pathWith('agy.exe') })).toBe(true);
        expect(
            providerAvailable(
                'claude-cli',
                {},
                {
                    PATH: pathWith('claude.cmd'),
                    PATHEXT: '.COM;.EXE;.BAT;.CMD',
                },
            ),
        ).toBe(true);
        expect(providerAvailable('antigravity-cli', {}, { PATH: pathWith('agy.xyz') })).toBe(false);
    });

    it.skipIf(process.platform !== 'win32')(
        'prefers the executable extension over an npm POSIX shim (#30)',
        () => {
            // npm installs a bare-named sh shim right next to opencode.cmd;
            // resolving the bare file first hands spawnSync something Windows
            // cannot execute.
            const dir = pathWith('opencode', 'opencode.cmd', 'opencode.ps1');
            const found = findOnPath('opencode', {
                PATH: dir,
                PATHEXT: '.COM;.EXE;.BAT;.CMD',
            });
            expect(found?.toLowerCase().endsWith('opencode.cmd')).toBe(true);
        },
    );

    it('requires every setting for openai, not just the key', () => {
        const env = { PATH: pathWith() };
        const partial = { providers: { openai: { apiKey: 'k', baseUrl: 'https://x' } } };
        expect(providerAvailable('openai', partial, env)).toBe(false);
        const full = {
            providers: { openai: { apiKey: 'k', baseUrl: 'https://x', model: 'm' } },
        };
        expect(providerAvailable('openai', full, env)).toBe(true);
    });

    it('reads a provider from whichever single source configures it (#42)', () => {
        // The environment configures a provider the file never mentions.
        expect(providerAvailable('gemini-api', {}, { PATH: pathWith(), GEMINI_API_KEY: 'g' })).toBe(
            true,
        );
        // Once the file mentions it, the file is the source, whole: a key in
        // the environment no longer completes a half-configured entry.
        expect(
            providerAvailable(
                'gemini-api',
                { providers: { 'gemini-api': { model: 'm' } } },
                {
                    PATH: pathWith(),
                    GEMINI_API_KEY: 'g',
                },
            ),
        ).toBe(false);
        expect(
            providerAvailable(
                'gemini-api',
                { providers: { 'gemini-api': { apiKey: 'g' } } },
                {
                    PATH: pathWith(),
                },
            ),
        ).toBe(true);
        expect(providerAvailable('unknown-provider', {}, { PATH: pathWith() })).toBe(false);
    });
});

describe('providerChain', () => {
    const allKeys = {
        providers: {
            'gemini-api': { apiKey: 'g' },
            openai: { apiKey: 'o', baseUrl: 'https://x', model: 'm' },
            anthropic: { apiKey: 'a' },
        },
    };

    it('orders a fully configured local chain inline-first, agents behind', () => {
        const env = { PATH: pathWith('agy', 'claude') };
        expect(names(providerChain('local', allKeys, env))).toEqual([
            'gemini-api',
            'openai',
            'anthropic',
            'antigravity-cli',
            'claude-cli',
        ]);
    });

    it('orders the remote chain inline-first and never includes claude-cli', () => {
        const env = { PATH: pathWith('agy', 'claude') };
        expect(names(providerChain('remote', allKeys, env))).toEqual([
            'gemini-api',
            'openai',
            'anthropic',
            'antigravity-cli',
        ]);
    });

    it('filters out providers that are not set up', () => {
        const env = { PATH: pathWith() };
        const geminiOnly = { providers: { 'gemini-api': { apiKey: 'g' } } };
        expect(names(providerChain('local', geminiOnly, env))).toEqual(['gemini-api']);
        expect(names(providerChain('local', {}, env))).toEqual([]);
    });

    it('admits a provider on its variables only while the file names none (#42)', () => {
        const env = { PATH: pathWith(), GEMINI_API_KEY: 'env-key' };
        expect(names(providerChain('local', {}, env))).toEqual(['gemini-api']);
        // The entry is empty, so it holds no key. It still says the file owns
        // this provider, and the chain has to agree with the resolver about
        // that or it routes an image at a provider with nothing behind it.
        expect(names(providerChain('local', { providers: { 'gemini-api': {} } }, env))).toEqual([]);
        expect(names(providerChain('local', { providers: { gemini: {} } }, env))).toEqual([]);
    });

    it('moves a configured default to the front of the local chain', () => {
        const env = { PATH: pathWith('agy') };
        const prefer = { ...allKeys, provider: 'anthropic' };
        expect(names(providerChain('local', prefer, env))).toEqual([
            'anthropic',
            'gemini-api',
            'openai',
            'antigravity-cli',
        ]);
    });

    it('keeps a configured agent default behind the inline providers for remote URLs', () => {
        const env = { PATH: pathWith('agy') };
        const prefer = { ...allKeys, provider: 'antigravity-cli' };
        expect(names(providerChain('remote', prefer, env))).toEqual([
            'gemini-api',
            'openai',
            'anthropic',
            'antigravity-cli',
        ]);
    });

    it('moves a configured inline default to the front of the remote chain', () => {
        const env = { PATH: pathWith('agy') };
        const prefer = { ...allKeys, provider: 'anthropic' };
        expect(names(providerChain('remote', prefer, env))).toEqual([
            'anthropic',
            'gemini-api',
            'openai',
            'antigravity-cli',
        ]);
    });

    it('ignores an unknown configured default', () => {
        const env = { PATH: pathWith() };
        const broken = { providers: { 'gemini-api': { apiKey: 'g' } }, provider: 'no-such' };
        expect(names(providerChain('local', broken, env))).toEqual(['gemini-api']);
    });
});

describe('kimi-cli only when chosen (#44)', () => {
    const bare = { providers: {} };

    it('stays out of the chain merely for being installed', () => {
        // It spends a Kimi Code subscription, and installing the CLI is not
        // agreement to spend it. claude-cli's automatic membership is a
        // compatibility carve-out this provider has no claim to.
        const local = providerChain('local', bare, { PATH: pathWith('kimi') }).map(
            (provider) => provider.name,
        );
        expect(local).not.toContain('kimi-cli');
    });

    it('runs when it is the configured provider', () => {
        const chain = providerChain(
            'local',
            { ...bare, provider: 'kimi-cli' },
            {
                PATH: pathWith('kimi'),
            },
        ).map((provider) => provider.name);
        expect(chain[0]).toBe('kimi-cli');
    });

    it('never joins a remote read, which it cannot fetch', () => {
        const chain = providerChain(
            'remote',
            { ...bare, provider: 'kimi-cli' },
            {
                PATH: pathWith('kimi'),
            },
        ).map((provider) => provider.name);
        expect(chain).not.toContain('kimi-cli');
    });

    it('is not conjured up by a preference when kimi is not installed', () => {
        const chain = providerChain(
            'local',
            { ...bare, provider: 'kimi-cli' },
            {
                PATH: pathWith(),
            },
        ).map((provider) => provider.name);
        expect(chain).not.toContain('kimi-cli');
    });
});

describe('PATH is read the way the platform reads it (#43)', () => {
    // process.env is case-insensitive on Windows, but a plain object built by
    // spreading it is not, and Windows usually spells the key `Path`. Reading
    // env.PATH off that object found nothing, so every CLI read as missing.
    // The fold is Windows-only on purpose: POSIX names are case-sensitive,
    // and accepting `Path` there would run a program found through a variable
    // POSIX does not define as the search path.
    it.skipIf(process.platform === 'win32')(
        'does not accept a differently cased key on POSIX',
        () => {
            const dir = pathWith('agy');
            expect(findOnPath('agy', { Path: dir })).toBeNull();
            expect(findOnPath('agy', { PATH: dir })).toBe(path.join(dir, 'agy'));
        },
    );
});
