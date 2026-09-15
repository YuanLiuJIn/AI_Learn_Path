import { describe, expect, it } from 'vitest';
import { extractJson, parseJsonLoose, tail, truncate, tryParseJson } from './json.ts';

describe('tryParseJson', () => {
    it('parses valid json and returns null for invalid', () => {
        expect(tryParseJson('{"a":1}')).toEqual({ a: 1 });
        expect(tryParseJson('nope')).toBeNull();
    });
});

describe('parseJsonLoose', () => {
    it('parses direct json', () => {
        expect(parseJsonLoose(' {"a":1} ')).toEqual({ a: 1 });
    });

    it('digs the outermost object out of surrounding noise', () => {
        expect(parseJsonLoose('log line\n{"a":1}\ntrailing')).toEqual({ a: 1 });
    });

    it('does not unwrap markdown fences', () => {
        // The fence's braces still get brace-scanned, but the leading ```json is
        // noise the loose parser is not asked to strip; the slice still works.
        expect(parseJsonLoose('```json\n{"a":1}\n```')).toEqual({ a: 1 });
    });

    it('returns null when nothing parses', () => {
        expect(parseJsonLoose('no json here')).toBeNull();
    });
});

describe('extractJson', () => {
    it('parses direct json', () => {
        expect(extractJson(' {"a":1} ')).toEqual({ a: 1 });
    });

    it('unwraps fenced blocks', () => {
        expect(extractJson('noise\n```json\n{"a":1}\n```\nmore')).toEqual({ a: 1 });
    });

    it('brace-scans as a last resort', () => {
        expect(extractJson('The result is {"a":1} thanks')).toEqual({ a: 1 });
    });

    it('returns null when nothing parses', () => {
        expect(extractJson('no json here')).toBeNull();
    });
});

describe('truncate', () => {
    it('clips past the limit and appends an ellipsis', () => {
        expect(truncate('abcdef', 3)).toBe('abc...');
        expect(truncate('ab', 3)).toBe('ab');
    });
});

describe('tolerant extraction when the model closes early (#45)', () => {
    // The exact shape qwen3-vl-plus produces intermittently on the openai
    // route: the top-level object closes after `semantics`, then the model
    // keeps writing the fields it still owed, then a stray quote. Slicing
    // from the first brace to the last swallows the fragment and fails, and
    // the read died as "non-JSON output", which looks the same as truncation.
    const doubleClosed =
        '{"summary":"heatmap","ocr":{"full_text":"a"},"layout":{"regions":[]},' +
        '"semantics":{"scene":"chart"}},"visual":{"palette":["#fff"]},"uncertainty":[]}"';

    it('recovers the object in front of the stray close', () => {
        const parsed = extractJson(doubleClosed) as Record<string, unknown>;
        expect(parsed).not.toBeNull();
        expect(parsed.summary).toBe('heatmap');
        expect(parsed.semantics).toEqual({ scene: 'chart' });
        // The fields after the early close are genuinely not in the object,
        // so the schema check names them instead of the parse failing.
        expect(parsed.visual).toBeUndefined();
    });

    it('does not mistake braces inside strings for structure', () => {
        const parsed = extractJson('{"summary":"a } b { c","ocr":{"full_text":"}"}}') as Record<
            string,
            unknown
        >;
        expect(parsed.summary).toBe('a } b { c');
    });

    it('handles an escaped quote before a brace', () => {
        const parsed = extractJson('{"summary":"say \\"hi\\" }","n":1}') as Record<string, unknown>;
        expect(parsed.summary).toBe('say "hi" }');
        expect(parsed.n).toBe(1);
    });

    it('keeps the largest object when noise carries its own', () => {
        const parsed = extractJson('{"log":"starting"}\n{"summary":"real","ocr":{}}') as Record<
            string,
            unknown
        >;
        expect(parsed.summary).toBe('real');
    });

    it('still returns null when nothing balanced parses', () => {
        expect(extractJson('no json here')).toBeNull();
        expect(extractJson('{"broken": ')).toBeNull();
    });
});

describe('tail', () => {
    it('shows the end, which is where a malformed answer went wrong', () => {
        expect(tail('abcdef', 3)).toBe('...def');
        expect(tail('ab', 3)).toBe('ab');
    });
});
