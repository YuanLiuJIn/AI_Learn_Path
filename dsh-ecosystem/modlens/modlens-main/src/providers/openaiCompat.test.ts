import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { executeOpenaiCompat } from './openaiCompat.ts';

// A full instance of the contract: the shape check now requires every field,
// because a gateway returning half of it is not a usable vision result.
const structured = {
    summary: 'ok',
    ocr: { full_text: '', lines: [] },
    layout: { regions: [] },
    semantics: { scene: '', intent: '', entities: [], relations: [] },
    visual: { dominant_colors: [], style: '', notes: [] },
    uncertainty: [],
};
let tmpImage: string;

beforeAll(() => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'modlens-oai-'));
    tmpImage = path.join(dir, 'x.png');
    fs.writeFileSync(tmpImage, Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
});

afterEach(() => {
    vi.unstubAllGlobals();
});

const settings = { apiKey: 'sk-x', baseUrl: 'https://gw.example.com/v1', model: 'qwen3.6-27b' };

describe('executeOpenaiCompat', () => {
    it('refuses to run without an endpoint rather than assuming OpenAI (#42)', async () => {
        // Defaulting here would take a key meant for another vendor, and the
        // image beside it, and send both to OpenAI. The error names the
        // setting and the binding that used to supply it.
        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: { apiKey: 'k', model: 'm' },
            }),
        ).rejects.toThrow(/baseUrl.*OPENAI_BASE_URL/s);
    });

    it('sends a template-instance prompt, not a raw json schema', async () => {
        const calls: Array<{ init: RequestInit }> = [];
        vi.stubGlobal('fetch', async (_url: string, init: RequestInit) => {
            calls.push({ init });
            return new Response(
                JSON.stringify({ choices: [{ message: { content: JSON.stringify(structured) } }] }),
                { status: 200 },
            );
        });

        await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings,
        });

        const body = JSON.parse(String(calls[0].init.body));
        const text = body.messages[0].content.find((b: { type: string }) => b.type === 'text').text;
        expect(text).toContain('Fill this exact structure');
        expect(text).not.toContain('"type":"object"');
    });

    it('redacts the api key and token shapes out of gateway error bodies', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    'unauthorized: key sk-x rejected (sent Authorization: Bearer sk-proj-abc123DEF456ghi789)',
                    { status: 401 },
                ),
        );
        const error = await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: { ...settings, apiKey: 'sk-x-full-key-value' },
        }).catch((e: Error) => e.message);
        expect(error).toContain('401');
        expect(error).not.toContain('sk-proj-abc123DEF456ghi789');
        expect(error).not.toContain('sk-x-full-key-value');
        expect(error).toContain('[redacted]');
    });

    it('merges extraBody into the request and guards the fields it needs', async () => {
        const calls: Array<{ init: RequestInit }> = [];
        vi.stubGlobal('fetch', async (_url: string, init: RequestInit) => {
            calls.push({ init });
            return new Response(
                JSON.stringify({ choices: [{ message: { content: JSON.stringify(structured) } }] }),
                { status: 200 },
            );
        });

        await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: { ...settings, extraBody: { thinking: { type: 'disabled' } } },
        });

        const body = JSON.parse(String(calls[0].init.body));
        expect(body.thinking).toEqual({ type: 'disabled' });
        expect(body.messages[0].content).toHaveLength(2);

        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: { ...settings, extraBody: { messages: [] } },
            }),
        ).rejects.toThrow('cannot override "messages"');
    });

    it('extracts fenced JSON from lax gateways', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({
                        choices: [
                            {
                                message: {
                                    content: `\`\`\`json\n${JSON.stringify(structured)}\n\`\`\``,
                                },
                            },
                        ],
                        usage: { total_tokens: 5 },
                    }),
                    { status: 200 },
                ),
        );

        const parsed = await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings,
        });
        expect(parsed.result).toEqual(structured);
    });

    it('fails loudly when the gateway returns schema-shaped or wrong JSON', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({
                        choices: [{ message: { content: '{"type":"object","properties":{}}' } }],
                    }),
                    { status: 200 },
                ),
        );

        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings,
            }),
        ).rejects.toThrow('does not match the vision schema');
    });
});

describe('structured output (#37)', () => {
    const capture = () => {
        const calls: Array<{ init: RequestInit }> = [];
        vi.stubGlobal('fetch', async (_url: string, init: RequestInit) => {
            calls.push({ init });
            return new Response(
                JSON.stringify({ choices: [{ message: { content: JSON.stringify(structured) } }] }),
                { status: 200 },
            );
        });
        return calls;
    };

    it('asks the gateway to enforce the contract only when told to', async () => {
        const calls = capture();
        await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: { ...settings, structuredOutput: true },
        });
        const body = JSON.parse(String(calls[0].init.body));
        expect(body.response_format.type).toBe('json_schema');
        expect(body.response_format.json_schema.strict).toBe(true);
        // The derived strict form, not the contract verbatim: the gateway
        // rejects a schema with optional properties.
        const schema = body.response_format.json_schema.schema;
        expect(schema.additionalProperties).toBe(false);
        expect(schema.properties.visual.properties.notes.anyOf[1]).toEqual({ type: 'null' });
    });

    it('sends nothing extra by default, since a gateway can 400 on it', async () => {
        const calls = capture();
        await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings,
        });
        expect(JSON.parse(String(calls[0].init.body))).not.toHaveProperty('response_format');
    });

    it('lets extraBody override the derived schema', async () => {
        // Someone with a gateway that wants a different shape keeps the
        // escape hatch they already had.
        const calls = capture();
        await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: {
                ...settings,
                structuredOutput: true,
                extraBody: { response_format: { type: 'json_object' } },
            },
        });
        expect(JSON.parse(String(calls[0].init.body)).response_format).toEqual({
            type: 'json_object',
        });
    });
});

describe('empty optionals on the openai route (#37)', () => {
    it('drops them at its own parse boundary', async () => {
        const quiet = {
            ...structured,
            ocr: { full_text: '', lines: [{ text: 'a', language: null }] },
            semantics: {
                scene: '',
                intent: null,
                entities: [{ name: 'e', type: 't', evidence: null }],
                relations: null,
            },
            visual: { dominant_colors: null, style: null, notes: null },
        };
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({ choices: [{ message: { content: JSON.stringify(quiet) } }] }),
                    { status: 200 },
                ),
        );
        const outcome = await executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings,
        });
        expect(JSON.stringify(outcome.result)).not.toContain('null');
        const result = outcome.result as {
            ocr: { lines: Array<Record<string, unknown>> };
            semantics: Record<string, unknown>;
            visual: Record<string, unknown>;
        };
        const entity = (result.semantics.entities as Array<Record<string, unknown>>)[0];
        for (const [holder, field] of [
            [result.ocr.lines[0], 'language'],
            [result.semantics, 'intent'],
            [result.semantics, 'relations'],
            [entity, 'evidence'],
            [result.visual, 'dominant_colors'],
            [result.visual, 'style'],
            [result.visual, 'notes'],
        ] as Array<[Record<string, unknown>, string]>) {
            expect(field in holder, `${field} survived`).toBe(false);
        }
        expect(result.ocr.lines[0].text).toBe('a');
        expect(entity.name).toBe('e');
    });
});

describe('schema shape enforcement', () => {
    it('rejects a partial result that used to pass the token check', async () => {
        // {"summary":"x","ocr":null} satisfied the old check and reached the model
        // as if it were evidence.
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({
                ok: true,
                json: async () => ({
                    choices: [
                        { message: { content: JSON.stringify({ summary: 'x', ocr: null }) } },
                    ],
                }),
            })),
        );
        await expect(
            executeOpenaiCompat({
                imageSource: 'https://example.com/a.png',
                imageKind: 'remote',
                timeoutMs: 1000,
                settings: { apiKey: 'k', baseUrl: 'https://api.example.com', model: 'm' },
            }),
        ).rejects.toThrow(/does not match the vision schema \(wrong or missing: ocr, layout/);
    });
});

describe('quoted gateway output is redacted, and finish_reason is not guessed (#45)', () => {
    const secretSettings = {
        apiKey: 'sk-proj-gate8-secret-1234567890',
        baseUrl: 'https://private-gateway.example.internal/v1',
        model: 'qwen3-vl-plus',
    };

    /** A 200 whose content the gateway wrote, ending in what it received. */
    function stubEcho(content: string, finishReason?: string) {
        vi.stubGlobal('fetch', async () => {
            return new Response(
                JSON.stringify({
                    choices: [
                        {
                            message: { content },
                            ...(finishReason ? { finish_reason: finishReason } : {}),
                        },
                    ],
                }),
                { status: 200 },
            );
        });
    }

    const echoTail = `not json at all apiKey=${secretSettings.apiKey} endpoint=${secretSettings.baseUrl}`;

    it('keeps the key and the endpoint out of the parse-failure message', async () => {
        // The message now shows the END of the output, so a gateway echoing
        // the headers it received puts them exactly where we quote.
        stubEcho(echoTail, 'stop');
        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: secretSettings,
            }),
        ).rejects.toThrow(
            expect.objectContaining({
                message: expect.not.stringContaining(secretSettings.apiKey),
            }),
        );

        stubEcho(echoTail, 'stop');
        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: secretSettings,
            }),
        ).rejects.toThrow(
            expect.objectContaining({
                message: expect.not.stringContaining('private-gateway.example.internal'),
            }),
        );
    });

    it('keeps them out of the schema-mismatch message too', async () => {
        // Same output, one fix short: quoting one error and not the other
        // just moves the leak.
        stubEcho(`{"summary":"x"} trailing ${secretSettings.apiKey}`, 'stop');
        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: secretSettings,
            }),
        ).rejects.toThrow(
            expect.objectContaining({
                message: expect.not.stringContaining(secretSettings.apiKey),
            }),
        );
    });

    it('names the token limit when the answer was cut off', async () => {
        stubEcho('{"summary":"half', 'length');
        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: secretSettings,
            }),
        ).rejects.toThrow(/finish_reason=length.*max_tokens/s);
    });

    it('does not call a filtered answer a normal one', async () => {
        // content_filter is the gateway saying it stopped early. Calling that
        // "ended normally" sends people to tune structured output instead.
        stubEcho('refused', 'content_filter');
        const run = executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: secretSettings,
        });
        await expect(run).rejects.toThrow(/finish_reason=content_filter/);
        await expect(run).rejects.not.toThrow(/ended normally/);
    });

    it('still points a genuinely complete answer at structuredOutput', async () => {
        stubEcho('sorry, I cannot do that', 'stop');
        await expect(
            executeOpenaiCompat({
                imageSource: tmpImage,
                imageKind: 'local',
                timeoutMs: 5000,
                settings: secretSettings,
            }),
        ).rejects.toThrow(/ended normally.*structuredOutput/s);
    });
});

describe('the private endpoint stays out of every gateway error (#45)', () => {
    const secretSettings = {
        apiKey: 'sk-proj-gate9-secret-1234567890',
        baseUrl: 'https://private-gateway.example.internal/v1',
        model: 'qwen3-vl-plus',
    };

    async function messageOf(promise: Promise<unknown>): Promise<string> {
        try {
            await promise;
        } catch (error) {
            return (error as Error).message;
        }
        throw new Error('expected a rejection');
    }

    const run = () =>
        executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: secretSettings,
        });

    it('redacts it out of a non-2xx body, which only masked the key before', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    `gateway rejected endpoint=${secretSettings.baseUrl} key=${secretSettings.apiKey}`,
                    { status: 500 },
                ),
        );
        const message = await messageOf(run());
        expect(message).toContain('error 500');
        expect(message).not.toContain('private-gateway.example.internal');
        expect(message).not.toContain(secretSettings.apiKey);
    });

    it('redacts it out of a finish_reason the gateway invented', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({
                        choices: [
                            {
                                message: { content: 'nope' },
                                finish_reason: `blocked_by_${secretSettings.baseUrl}`,
                            },
                        ],
                    }),
                    { status: 200 },
                ),
        );
        const message = await messageOf(run());
        expect(message).not.toContain('private-gateway.example.internal');
    });
});

describe('redaction runs before the message is clipped (#45)', () => {
    // The endpoint is redacted by exact match, and a plain https URL matches
    // none of the token shapes, so clipping through the middle of it first
    // left the hostname in the message with nothing left to match.
    const secretSettings = {
        apiKey: 'sk-proj-gate10-secret-1234567890',
        baseUrl: 'https://private-gateway.example.internal/v1/tenant-42',
        model: 'qwen3-vl-plus',
    };

    async function messageOf(promise: Promise<unknown>): Promise<string> {
        try {
            await promise;
        } catch (error) {
            return (error as Error).message;
        }
        throw new Error('expected a rejection');
    }

    const run = () =>
        executeOpenaiCompat({
            imageSource: tmpImage,
            imageKind: 'local',
            timeoutMs: 5000,
            settings: secretSettings,
        });

    // 251 + 'endpoint=' puts the URL at offset 260, so truncate's 300-char
    // cut lands 40 characters in: past the hostname, before the end. The
    // whole URL is no longer present for an exact match to find.
    function straddling(): string {
        return `${'x'.repeat(251)}endpoint=${secretSettings.baseUrl} tail`;
    }

    it('keeps it out of a non-2xx body clipped mid-hostname', async () => {
        vi.stubGlobal('fetch', async () => new Response(straddling(), { status: 500 }));
        const message = await messageOf(run());
        expect(message).not.toContain('private-gateway');
    });

    it('keeps it out of the schema-mismatch quote', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({
                        choices: [{ message: { content: `{"summary":"x"} ${straddling()}` } }],
                    }),
                    { status: 200 },
                ),
        );
        const message = await messageOf(run());
        expect(message).not.toContain('private-gateway');
    });

    it('keeps it out of the tail quote', async () => {
        // tail() shows the END, so the endpoint has to survive that boundary.
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({
                        choices: [
                            {
                                // tail() cuts the FRONT, and 250 of padding
                                // puts the cut inside `https://`, leaving the
                                // hostname and everything after it visible.
                                message: {
                                    content: `no json ${secretSettings.baseUrl}${'y'.repeat(250)}`,
                                },
                                finish_reason: 'stop',
                            },
                        ],
                    }),
                    { status: 200 },
                ),
        );
        const message = await messageOf(run());
        expect(message).not.toContain('private-gateway');
    });

    it('keeps it out of a long invented finish_reason', async () => {
        vi.stubGlobal(
            'fetch',
            async () =>
                new Response(
                    JSON.stringify({
                        choices: [
                            {
                                message: { content: 'nope' },
                                finish_reason: `${'blocked_'.repeat(4)}${secretSettings.baseUrl}${'z'.repeat(60)}`,
                            },
                        ],
                    }),
                    { status: 200 },
                ),
        );
        const message = await messageOf(run());
        expect(message).not.toContain('private-gateway');
    });
});

describe('a mismatched shape names the knob that applies (#59)', () => {
    // The advice on this path used to be "Retry, or switch to gemini-api /
    // anthropic", which sends someone off an endpoint that one config line
    // would have fixed. That is what happened on Kimi Code: the reader blamed
    // the model. The sibling branch sixteen lines above already named
    // structuredOutput, added for #45 and never carried across.

    /** A 200 whose content parses but does not fit the contract. */
    function stubHalfAnswer(finishReason?: string) {
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({
                ok: true,
                json: async () => ({
                    choices: [
                        {
                            message: { content: JSON.stringify({ summary: 'x' }) },
                            ...(finishReason ? { finish_reason: finishReason } : {}),
                        },
                    ],
                }),
            })),
        );
    }

    async function messageFrom(extra: Record<string, unknown>): Promise<string> {
        try {
            await executeOpenaiCompat({
                imageSource: 'https://example.com/a.png',
                imageKind: 'remote',
                timeoutMs: 1000,
                settings: { ...settings, ...extra },
            });
        } catch (error) {
            return (error as Error).message;
        }
        throw new Error('expected a rejection');
    }

    it('points an unenforced answer at structuredOutput, not at another provider', async () => {
        stubHalfAnswer('stop');

        const message = await messageFrom({});

        expect(message).toContain('does not match the vision schema');
        expect(message).toContain('modlens config set openai.structuredOutput true');
        expect(message).not.toContain('switch to gemini-api');
    });

    it('keeps the old advice once the gateway was asked and answered badly anyway', async () => {
        stubHalfAnswer('stop');

        const message = await messageFrom({ structuredOutput: true });

        expect(message).toContain('switch to gemini-api');
        // Telling someone to set an option they already set is the fastest way
        // to lose them.
        expect(message).not.toContain('structuredOutput true');
    });

    it('blames the response_format the caller supplied, since it replaces ours', async () => {
        stubHalfAnswer('stop');

        const message = await messageFrom({
            structuredOutput: true,
            extraBody: { response_format: { type: 'json_object' } },
        });

        expect(message).toContain('extraBody');
        // Enabling a setting that is already on, and overridden anyway, fixes
        // nothing here.
        expect(message).not.toContain('structuredOutput true');
    });

    it('never tells someone to enable what is already enabled, on either branch', async () => {
        // The sibling branch, for output that does not parse at all, kept
        // recommending structuredOutput unconditionally. Fixing one advice path
        // and leaving the other giving impossible advice is the same defect.
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({
                ok: true,
                json: async () => ({
                    choices: [{ message: { content: 'not json' }, finish_reason: 'stop' }],
                }),
            })),
        );

        const message = await messageFrom({ structuredOutput: true });

        expect(message).toContain('non-JSON output');
        expect(message).not.toContain('structuredOutput true');
    });

    it('names a gateway that stopped for its own reason, and blames no knob', async () => {
        // content_filter is not a shape problem and not a limit, and it can
        // arrive alongside an override, where both schema knobs are red
        // herrings.
        stubHalfAnswer('content_filter');

        const message = await messageFrom({
            structuredOutput: true,
            extraBody: { response_format: { type: 'json_object' } },
        });

        expect(message).toContain('finish_reason=content_filter');
        expect(message).not.toContain('structuredOutput true');
        expect(message).not.toContain('extraBody replaces');
    });

    it('treats a null finish_reason as absent instead of crashing the diagnosis', async () => {
        // null is the streaming-chunk spelling of the field, and compat
        // gateways that reuse one response model for both modes send it in
        // non-streaming responses too. It used to fall into the quoted-reason
        // branch, where redaction called .split on it, so the very error this
        // advice exists for surfaced as a TypeError instead.
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({
                ok: true,
                json: async () => ({
                    choices: [
                        {
                            message: { content: JSON.stringify({ summary: 'x' }) },
                            finish_reason: null,
                        },
                    ],
                }),
            })),
        );

        const message = await messageFrom({});

        expect(message).toContain('does not match the vision schema');
        expect(message).toContain('modlens config set openai.structuredOutput true');
    });

    it('treats a non-string finish_reason as absent on the non-JSON branch too', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({
                ok: true,
                json: async () => ({
                    choices: [{ message: { content: 'not json' }, finish_reason: null }],
                }),
            })),
        );

        const message = await messageFrom({});

        expect(message).toContain('non-JSON output');
        expect(message).toContain('modlens config set openai.structuredOutput true');
    });

    it('calls a truncated answer truncated rather than a schema problem', async () => {
        // A cut-off answer can still be parseable JSON, so it lands here rather
        // than on the non-JSON path that already handles finish_reason.
        stubHalfAnswer('length');

        const message = await messageFrom({});

        expect(message).toContain('finish_reason=length');
        expect(message).not.toContain('structuredOutput true');
    });
});
