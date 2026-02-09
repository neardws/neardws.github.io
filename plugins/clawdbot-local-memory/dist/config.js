const ALLOWED_KEYS = [
    "autoRecall",
    "autoCapture",
    "maxRecallResults",
    "profileFrequency",
    "extractionModel",
    "debug",
];
export function parseConfig(raw) {
    const cfg = raw && typeof raw === "object" && !Array.isArray(raw)
        ? raw
        : {};
    // Check for unknown keys
    const unknown = Object.keys(cfg).filter((k) => !ALLOWED_KEYS.includes(k));
    if (unknown.length > 0) {
        throw new Error(`local-memory config has unknown keys: ${unknown.join(", ")}`);
    }
    return {
        autoRecall: cfg.autoRecall ?? true,
        autoCapture: cfg.autoCapture ?? true,
        maxRecallResults: cfg.maxRecallResults ?? 10,
        profileFrequency: cfg.profileFrequency ?? 50,
        extractionModel: cfg.extractionModel ?? "auto",
        debug: cfg.debug ?? false,
    };
}
export const localMemoryConfigSchema = {
    parse: parseConfig,
};
