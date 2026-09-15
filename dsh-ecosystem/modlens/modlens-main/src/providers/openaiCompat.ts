// OpenAI-compatible provider: works with any /chat/completions endpoint that
// accepts image_url content (DashScope qwen-vl, OpenAI, GLM, ...). No portable
// schema enforcement across vendors, so the schema rides in the prompt and the
// response goes through tolerant JSON extraction.

import { assertNoRetiredEndpointBinding } from '../config.ts';
import { readLocalImageBase64 } from '../imageInput.ts';
import { apiFetch } from '../net/proxy.ts';
import { buildVisionPrompt, JSON_TEMPLATE_INSTRUCTION } from '../prompt.ts';
import { missingSchemaFields, normalizeVisionResult, visionResponseFormat } from '../schema.ts';
import { mergeExtraBody } from '../util/extraBody.ts';
import { extractJson, tail, truncate } from '../util/json.ts';
import { redactSecrets } from '../util/redact.ts';
import type {
    BuildProviderInvocationOptions,
    ProviderParsedOutput,
    VisionProvider,
} from './index.ts';

type OpenaiSettings = BuildProviderInvocationOptions['settings'];

/**
 * Whether the request actually carried the schema modlens derives.
 * `structuredOutput` asks for it, and a `response_format` the caller put in
 * `extraBody` replaces it outright, so both decide what a mismatched answer
 * means. Read from one place so the request and the error cannot disagree.
 */
function derivedSchemaSent(settings: OpenaiSettings): boolean {
    return (
        Boolean(settings?.structuredOutput) && settings?.extraBody?.response_format === undefined
    );
}

/**
 * What to change when the answer arrived whole and is still unusable. Which
 * knob applies is a property of the request that went out, not of the way the
 * output disappointed, so both failure branches ask this one question.
 */
function requestShapeAdvice(settings: OpenaiSettings): string {
    if (settings?.extraBody?.response_format !== undefined) {
        return 'The response_format in your extraBody replaces the schema modlens derives, so yours decides the shape here. Check it against the contract, or drop it to hand enforcement back to modlens.';
    }
    if (!derivedSchemaSent(settings)) {
        return 'The gateway was never asked to enforce the shape, so this is the model free-handing it. Ask the gateway instead: modlens config set openai.structuredOutput true.';
    }
    return 'The gateway was asked to enforce the shape and answered with this anyway. Retry, or switch to gemini-api / anthropic for enforced schemas.';
}

/**
 * The declared response type claims finish_reason is a string, but it arrives
 * from JSON: null is the streaming-chunk spelling of the field and compat
 * gateways that reuse one response model send it in non-streaming answers too.
 * Anything that is not a string is treated as the field being absent, since
 * quoting a null through redaction crashed the very diagnosis it was part of.
 */
function stringOrAbsent(value: unknown): string | undefined {
    return typeof value === 'string' ? value : undefined;
}

/**
 * Unusable output has several causes that look alike, and each has a different
 * knob. Naming only one of them sent a user off an endpoint that a single
 * config line would have fixed, after concluding the model could not do it
 * (issue #59). Truncation outranks everything, because a cut-off answer
 * explains missing fields whatever the request asked for. Only `stop` says
 * outright that the answer finished; an absent reason is read the same way
 * only because some gateways omit the field.
 *
 * `whenFinished` is the one part that differs between the two branches: what
 * was wrong with output that did arrive complete.
 */
function unusableOutputAdvice(
    finishReason: string | undefined,
    settings: OpenaiSettings,
    quoteReason: (reason: string) => string,
    whenFinished: string,
): string {
    if (finishReason === 'length') {
        return 'The answer was cut off (finish_reason=length), so this is a length limit rather than a shape problem. Raise it, e.g. modlens config set openai.extraBody \'{"max_tokens":4096}\'.';
    }
    if (finishReason !== undefined && finishReason !== 'stop') {
        return `The gateway ended the answer with finish_reason=${quoteReason(finishReason)}, so it may be incomplete for a reason of its own. Check what that reason means for this endpoint before changing the request.`;
    }
    return `${whenFinished} ${requestShapeAdvice(settings)}`;
}

export async function executeOpenaiCompat(
    options: BuildProviderInvocationOptions,
): Promise<ProviderParsedOutput> {
    assertNoRetiredEndpointBinding('openai', options.settings ?? {});
    const apiKey = options.settings?.apiKey;
    // No default on purpose. Defaulting to official OpenAI would take a key
    // meant for another vendor, and the image beside it, and send both to
    // OpenAI, which is the same fault issue #42 fixed pointed the other way:
    // a pairing the user never configured.
    const baseUrl = options.settings?.baseUrl?.replace(/\/$/, '');
    const model = options.model || options.settings?.model;

    if (!apiKey || !baseUrl || !model) {
        throw new Error(
            'openai provider needs baseUrl, apiKey, and model: modlens config set openai.baseUrl <url>, modlens config set openai.apiKey (a hidden prompt), modlens config set openai.model <name>. There is no default endpoint (official OpenAI is https://api.openai.com/v1). OPENAI_BASE_URL and OPENAI_API_KEY still supply this provider on their own, but only while the config file names no openai entry, since 3.17.0 takes a provider whole from one source; no variable carries the model, so an environment-only setup passes -m <name>.',
        );
    }

    const imageUrl =
        options.imageKind === 'remote'
            ? options.imageSource
            : toDataUrl(readLocalImageBase64(options.imageSource));

    const prompt = `${buildVisionPrompt({
        imageSource: options.imageSource,
        imageKind: 'inline',
        extraPrompt: options.extraPrompt,
    })}

${JSON_TEMPLATE_INSTRUCTION}`;

    const startedAt = Date.now();
    const response = await apiFetch(
        `${baseUrl}/chat/completions`,
        {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                mergeExtraBody(
                    {
                        model,
                        // Asked for, never assumed: a gateway without
                        // structured-output support answers 400 for a field
                        // it does not know (issue #37). A response_format the
                        // caller supplied wins outright rather than being
                        // merged into ours, since the two describe the same
                        // thing and a blend of them describes neither.
                        ...(derivedSchemaSent(options.settings)
                            ? { response_format: visionResponseFormat() }
                            : {}),
                        messages: [
                            {
                                role: 'user',
                                content: [
                                    { type: 'image_url', image_url: { url: imageUrl } },
                                    { type: 'text', text: prompt },
                                ],
                            },
                        ],
                    },
                    options.settings?.extraBody,
                    ['model', 'messages', 'stream'],
                    'openai',
                ),
            ),
            signal: AbortSignal.timeout(options.timeoutMs),
        },
        options.settings?.proxy,
    );

    // Everything the gateway wrote goes through here before it is quoted into
    // an error. Errors travel into terminals, CI logs, agent transcripts and
    // failover warnings, and the gateway controls its own response, so a
    // private endpoint is as quotable back at us as the key is. One helper
    // rather than a call at each site: the leak that reached review was one
    // path fixed and another missed.
    // Redact first, clip second. Clipping first leaves a half-written endpoint
    // that exact matching can no longer find, and a plain https URL carries
    // nothing for the shape rules to catch, so a boundary landing inside the
    // hostname published it.
    const quote = (shown: string, clip: (text: string) => string = truncate): string =>
        clip(redactSecrets(shown, [apiKey, baseUrl]));

    if (!response.ok) {
        const body = await response.text();
        throw new Error(`OpenAI-compatible API error ${response.status}: ${quote(body)}`);
    }

    const payload = (await response.json()) as {
        choices?: Array<{ message?: { content?: string }; finish_reason?: string }>;
        usage?: unknown;
    };

    const text = payload.choices?.[0]?.message?.content;
    if (!text) {
        throw new Error('OpenAI-compatible API returned no message content.');
    }

    const rawResult = extractJson(text);
    if (rawResult === null) {
        // Why it failed decides what the user should do, and the causes used
        // to look identical (issue #45). The tail is where the damage is, so
        // the message ends with it rather than with the opening summary.
        const advice = unusableOutputAdvice(
            stringOrAbsent(payload.choices?.[0]?.finish_reason),
            options.settings,
            (reason) => quote(reason, (clipped) => truncate(clipped, 80)),
            'The answer ended normally but no complete JSON object could be read from it.',
        );
        throw new Error(
            `OpenAI-compatible API returned non-JSON output. ${advice} Output ended with: ${quote(text, tail)}`,
        );
    }
    // No portable server-side schema enforcement on this route, so verify the
    // shape instead of silently returning something that only looks right.
    // Checking only top-level keys still let {"ocr":{}} through, so the model
    // received an empty shell that looked like evidence.
    // null on an optional field means the same as leaving it out, so it is
    // dropped before the check rather than failing the read (issue #37).
    const result = normalizeVisionResult(rawResult);
    const missing = missingSchemaFields(result);
    if (missing.length > 0) {
        const advice = unusableOutputAdvice(
            stringOrAbsent(payload.choices?.[0]?.finish_reason),
            options.settings,
            (reason) => quote(reason, (clipped) => truncate(clipped, 80)),
            'The answer ended normally and parsed, but not into the contract.',
        );
        throw new Error(
            `OpenAI-compatible API returned JSON that does not match the vision schema (wrong or missing: ${missing.join(', ')}). ${advice} Got: ${quote(text)}`,
        );
    }

    return {
        result,
        meta: {
            conversationId: null,
            durationSeconds: (Date.now() - startedAt) / 1000,
            usage: payload.usage ?? null,
        },
    };
}

function toDataUrl(image: { data: string; mimeType: string }): string {
    return `data:${image.mimeType};base64,${image.data}`;
}

export const openaiCompatProvider: VisionProvider = {
    name: 'openai',
    defaultModel: '',
    execute: executeOpenaiCompat,
};
