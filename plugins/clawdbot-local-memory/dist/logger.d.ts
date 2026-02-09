import type { PluginLogger } from "clawdbot/plugin-sdk";
export declare function initLogger(logger: PluginLogger, debug: boolean): void;
export declare const log: {
    info: (msg: string) => any;
    warn: (msg: string) => any;
    error: (msg: string, err?: unknown) => void;
    debug: (msg: string) => void;
    debugRequest: (op: string, data: Record<string, unknown>) => void;
    debugResponse: (op: string, data: Record<string, unknown>) => void;
};
