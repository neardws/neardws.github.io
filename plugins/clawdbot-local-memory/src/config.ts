export type LocalMemoryConfig = {
  autoRecall: boolean;
  autoCapture: boolean;
  maxRecallResults: number;
  profileFrequency: number;
  extractionModel: string;
  debug: boolean;
};

const ALLOWED_KEYS = [
  "autoRecall",
  "autoCapture", 
  "maxRecallResults",
  "profileFrequency",
  "extractionModel",
  "debug",
];

export function parseConfig(raw: unknown): LocalMemoryConfig {
  const cfg =
    raw && typeof raw === "object" && !Array.isArray(raw)
      ? (raw as Record<string, unknown>)
      : {};

  // Check for unknown keys
  const unknown = Object.keys(cfg).filter((k) => !ALLOWED_KEYS.includes(k));
  if (unknown.length > 0) {
    throw new Error(`local-memory config has unknown keys: ${unknown.join(", ")}`);
  }

  return {
    autoRecall: (cfg.autoRecall as boolean) ?? true,
    autoCapture: (cfg.autoCapture as boolean) ?? true,
    maxRecallResults: (cfg.maxRecallResults as number) ?? 10,
    profileFrequency: (cfg.profileFrequency as number) ?? 50,
    extractionModel: (cfg.extractionModel as string) ?? "auto",
    debug: (cfg.debug as boolean) ?? false,
  };
}

export const localMemoryConfigSchema = {
  parse: parseConfig,
};
