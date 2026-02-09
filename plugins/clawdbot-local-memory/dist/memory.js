export const MEMORY_CATEGORIES = [
    "preference",
    "fact",
    "decision",
    "entity",
    "context",
    "other",
];
export function detectCategory(text) {
    const lower = text.toLowerCase();
    if (/prefer|like|love|hate|want|favorite/i.test(lower))
        return "preference";
    if (/decided|will use|going with|chose/i.test(lower))
        return "decision";
    if (/\+\d{10,}|@[\w.-]+\.\w+|is called|named/i.test(lower))
        return "entity";
    if (/recently|today|yesterday|just now|earlier/i.test(lower))
        return "context";
    if (/is|are|has|have|works|lives/i.test(lower))
        return "fact";
    return "other";
}
