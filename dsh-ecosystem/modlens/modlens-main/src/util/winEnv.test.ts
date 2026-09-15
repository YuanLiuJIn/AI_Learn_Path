import { describe, expect, it } from 'vitest';
import {
    canonicalWindowsEnv,
    envValue,
    windowsKeyFor,
    withoutWindowsEnvVariable,
    withWindowsEnvAssignment,
} from './winEnv.ts';

const WIN: NodeJS.Platform = 'win32';

describe('envValue', () => {
    it('reads by exact name on POSIX, where names are case-sensitive', () => {
        expect(envValue({ Path: '/wrong' }, 'PATH', 'darwin')).toBeUndefined();
        expect(envValue({ PATH: '/right' }, 'PATH', 'darwin')).toBe('/right');
    });

    it('folds the name on Windows', () => {
        expect(envValue({ Path: 'C:\\right' }, 'PATH', WIN)).toBe('C:\\right');
    });

    it('picks the spelling Node would pass, not the one inserted first', () => {
        // Node sorts a custom Windows child environment and passes the first
        // case-insensitive match, so `Path` wins over `path` however the
        // object was built. Insertion order here disagrees with that sort.
        expect(envValue({ path: 'C:\\wrong', Path: 'C:\\right' }, 'PATH', WIN)).toBe('C:\\right');
        expect(windowsKeyFor({ path: 'a', Path: 'b' }, 'PATH')).toBe('Path');
    });
});

describe('canonicalWindowsEnv', () => {
    it('keeps one spelling per name and drops undefined values', () => {
        const folded = canonicalWindowsEnv({ path: 'wrong', Path: 'right', GONE: undefined });
        expect(folded).toEqual({ Path: 'right' });
    });
});

describe('withWindowsEnvAssignment', () => {
    it('replaces every spelling rather than adding another', () => {
        const next = withWindowsEnvAssignment({ path: 'a', Path: 'b' }, 'PATH', 'c');
        expect(Object.keys(next).filter((k) => k.toUpperCase() === 'PATH')).toEqual(['Path']);
        expect(next.Path).toBe('c');
    });

    it('uses the requested spelling when the variable is new', () => {
        expect(withWindowsEnvAssignment({ OTHER: 'x' }, 'dp0', 'C:\\bin\\')).toEqual({
            OTHER: 'x',
            dp0: 'C:\\bin\\',
        });
    });
});

describe('withoutWindowsEnvVariable', () => {
    it('removes every spelling, which is what SET NAME= does', () => {
        expect(
            withoutWindowsEnvVariable({ pathext: 'a', PATHEXT: 'b', KEEP: 'c' }, 'PATHEXT'),
        ).toEqual({ KEEP: 'c' });
    });
});

describe('keys Node would see, not just own ones', () => {
    // Node enumerates a custom child environment with for...in and
    // deliberately includes enumerable prototype properties. Reading only own
    // keys silently drops variables the child really receives, which can make
    // a CLI read as missing or strip a credential from a plan.
    function withProto(own: NodeJS.ProcessEnv, proto: NodeJS.ProcessEnv): NodeJS.ProcessEnv {
        return Object.assign(Object.create(proto), own) as NodeJS.ProcessEnv;
    }

    it('finds a variable that lives on the prototype', () => {
        expect(envValue(withProto({}, { Path: 'C:\\right' }), 'PATH', WIN)).toBe('C:\\right');
    });

    it('keeps a prototype variable when folding the environment', () => {
        expect(canonicalWindowsEnv(withProto({ OWN: 'a' }, { INHERITED: 'b' }))).toEqual({
            INHERITED: 'b',
            OWN: 'a',
        });
    });

    it('lets an own key win over the same name on the prototype', () => {
        expect(envValue(withProto({ Path: 'own' }, { Path: 'proto' }), 'PATH', WIN)).toBe('own');
    });
});
