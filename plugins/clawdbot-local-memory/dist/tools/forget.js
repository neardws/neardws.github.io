import { Type } from "@sinclair/typebox";
import { log } from "../logger.js";
export function registerForgetTool(api, client, _cfg) {
    api.registerTool({
        name: "local_memory_forget",
        label: "Memory Forget",
        description: "Forget/delete a specific memory by query.",
        parameters: Type.Object({
            query: Type.String({ description: "Describe the memory to forget" }),
        }),
        async execute(_toolCallId, params) {
            log.debug(`forget tool: query="${params.query}"`);
            const result = await client.forgetByQuery(params.query);
            return {
                content: [{ type: "text", text: result.message }],
            };
        },
    }, { name: "local_memory_forget" });
}
