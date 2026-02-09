import type { ClawdbotPluginApi } from "clawdbot/plugin-sdk";
import { parseConfig } from "./config.js";
declare const _default: {
    id: string;
    name: string;
    description: string;
    kind: "memory";
    configSchema: {
        parse: typeof parseConfig;
    };
    register(api: ClawdbotPluginApi): void;
};
export default _default;
