import type { LocalMemoryClient } from "../client.js";
import type { LocalMemoryConfig } from "../config.js";
export declare function buildCaptureHandler(client: LocalMemoryClient, cfg: LocalMemoryConfig): (event: Record<string, unknown>) => Promise<void>;
