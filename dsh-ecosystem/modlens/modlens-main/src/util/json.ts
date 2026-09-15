// Shared JSON helpers. Every provider needs the same three moves: parse JSON
// without throwing, dig a JSON object out of chatty output, and truncate a long
// blob for an error message. They used to be copy-pasted into each provider,
// which drifted the moment one copy was touched.

/** Parse JSON, returning null instead of throwing. */
export function tryParseJson(text: string): unknown | null {
    try {
        return JSON.parse(text);
    } catch {
        return null;
    }
}

/** Parse user-supplied JSON under a named origin, or explain why not. */
export function parseJsonOrExplain(raw: string, origin: string): unknown {
    try {
        return JSON.parse(raw);
    } catch (error) {
        throw new Error(`${origin} is not valid JSON: ${(error as Error).message}`);
    }
}

/**
 * Parse JSON, first as-is, then from the outermost {...} slice. Enough for CLIs
 * that wrap their JSON envelope in a line of log noise, but not markdown fences.
 */
export function parseJsonLoose(text: string): unknown | null {
    const trimmed = text.trim();
    const direct = tryParseJson(trimmed);
    if (direct !== null) {
        return direct;
    }
    return parseBraceSlice(trimmed);
}

/**
 * Best-effort JSON extraction for APIs without enforced structured output: tries
 * a direct parse, then a ```json fenced block, then the outermost {...} slice.
 */
export function extractJson(text: string): unknown | null {
    const trimmed = text.trim();

    const direct = tryParseJson(trimmed);
    if (direct !== null) {
        return direct;
    }

    const fenced = /```(?:json)?\s*([\s\S]*?)```/i.exec(trimmed);
    if (fenced) {
        const parsed = tryParseJson(fenced[1].trim());
        if (parsed !== null) {
            return parsed;
        }
    }

    return parseBraceSlice(trimmed);
}

function parseBraceSlice(trimmed: string): unknown | null {
    const first = trimmed.indexOf('{');
    const last = trimmed.lastIndexOf('}');
    if (first >= 0 && last > first) {
        const whole = tryParseJson(trimmed.slice(first, last + 1));
        if (whole !== null) {
            return whole;
        }
    }
    return parseLongestBalancedObject(trimmed);
}

/**
 * The largest `{...}` in the text that is balanced on its own and parses.
 *
 * The first-brace-to-last-brace slice above cannot survive a model that closes
 * the object early and keeps writing, which is what qwen3-vl does intermittently
 * on the openai route (issue #45): `{"summary":...,"semantics":{...}},"visual":
 * {...}}` has a real object in front of a stray fragment, and slicing to the
 * last brace swallows the fragment and fails. Reading the braces with the string
 * literals accounted for finds the object instead. It is the recoverable prefix,
 * so the schema check gets to name the fields that are actually missing rather
 * than the read dying as "non-JSON output", which is indistinguishable from a
 * truncation.
 *
 * Largest rather than first, because chatty output can put a small envelope in
 * front of the answer, and the answer is the bigger of the two. A heuristic,
 * not a proof: a model that closes the object early and keeps writing can
 * leave a tail fragment bigger than the real prefix, and then the wrong span
 * wins and the schema check names fields the model did produce. Both readings
 * fail the read either way; this only decides which fields the error names.
 */
function parseLongestBalancedObject(text: string): unknown | null {
    const spans: Array<[number, number]> = [];
    let depth = 0;
    let start = -1;
    let inString = false;
    let escaped = false;
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (inString) {
            // An escape consumes whatever follows, so a `\"` does not close the
            // string and a `\\` does not escape the quote after it.
            if (escaped) {
                escaped = false;
            } else if (char === '\\') {
                escaped = true;
            } else if (char === '"') {
                inString = false;
            }
            continue;
        }
        if (char === '"') {
            inString = true;
        } else if (char === '{') {
            if (depth === 0) {
                start = i;
            }
            depth++;
        } else if (char === '}') {
            if (depth > 0) {
                depth--;
                if (depth === 0 && start >= 0) {
                    spans.push([start, i + 1]);
                    start = -1;
                }
            }
            // A close with nothing open is the stray one. Ignoring it rather
            // than resetting keeps the objects found so far.
        }
    }
    // Longest first: the first one that parses is the best candidate, and a
    // balanced span can still fail on its contents (a trailing comma, a
    // half-written number), so parsing is what decides.
    for (const [from, to] of spans.sort((a, b) => b[1] - b[0] - (a[1] - a[0]))) {
        const parsed = tryParseJson(text.slice(from, to));
        if (parsed !== null) {
            return parsed;
        }
    }
    return null;
}

/** Shorten a blob for an error message, appending an ellipsis when clipped. */
export function truncate(text: string, max = 300): string {
    return text.length > max ? `${text.slice(0, max)}...` : text;
}

/**
 * The END of a blob, for errors about how output finished. `truncate` shows the
 * opening, which for a malformed answer is the part that was fine: whether it
 * was cut off mid-token or closed early and rambled shows up at the tail.
 */
export function tail(text: string, max = 300): string {
    return text.length > max ? `...${text.slice(-max)}` : text;
}
