import { Type } from "@sinclair/typebox";
import { log } from "../logger.js";
export function registerSearchTool(api, client, _cfg) {
    api.registerTool({
        name: "local_memory_search",
        label: "Memory Search",
        description: "Search through long-term memories for relevant information.",
        parameters: Type.Object({
            query: Type.String({ description: "Search query" }),
            limit: Type.Optional(Type.Number({ description: "Max results (default: 5)" })),
        }),
        async execute(_toolCallId, params) {
            const limit = params.limit ?? 5;
            log.debug(`search tool: query="${params.query}" limit=${limit}`);
            const results = await client.search(params.query, limit);
            if (results.length === 0) {
                return {
                    content: [
                        { type: "text", text: "No relevant memories found." },
                    ],
                };
            }
            const text = results
                .map((r, i) => {
                const score = r.similarity
                    ? ` (${(r.similarity * 100).toFixed(0)}%)`
                    : "";
                return `${i + 1}. ${r.content}${score}`;
            })
                .join("\n");
            return {
                content: [
                    {
                        type: "text",
                        text: `Found ${results.length} memories:\n\n${text}`,
                    },
                ],
            };
        },
    }, { name: "local_memory_search" });
}
