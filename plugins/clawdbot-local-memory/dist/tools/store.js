import { Type } from "@sinclair/typebox";
import { stringEnum } from "clawdbot/plugin-sdk";
import { MEMORY_CATEGORIES, detectCategory } from "../memory.js";
import { log } from "../logger.js";
export function registerStoreTool(api, client, _cfg) {
    api.registerTool({
        name: "local_memory_store",
        label: "Memory Store",
        description: "Save important information to long-term memory.",
        parameters: Type.Object({
            text: Type.String({ description: "Information to remember" }),
            category: Type.Optional(stringEnum(MEMORY_CATEGORIES)),
        }),
        async execute(_toolCallId, params) {
            const category = params.category ?? detectCategory(params.text);
            log.debug(`store tool: category="${category}"`);
            await client.addMemory(params.text, category, "tool");
            const preview = params.text.length > 80
                ? `${params.text.slice(0, 80)}…`
                : params.text;
            return {
                content: [{ type: "text", text: `Stored: "${preview}"` }],
            };
        },
    }, { name: "local_memory_store" });
}
