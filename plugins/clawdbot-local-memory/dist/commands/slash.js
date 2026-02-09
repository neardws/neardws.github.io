export function registerCommands(api, client, _cfg) {
    // /remember command
    api.registerCommand({
        name: "remember",
        description: "Save something to memory",
        acceptsArgs: true,
        handler: async (ctx) => {
            const text = ctx.args?.trim();
            if (!text) {
                return { text: "Usage: /remember <text to remember>" };
            }
            await client.addMemory(text, undefined, "command");
            return { text: `✓ Remembered: "${text.slice(0, 50)}${text.length > 50 ? '…' : ''}"` };
        },
    });
    // /recall command
    api.registerCommand({
        name: "recall",
        description: "Search your memories",
        acceptsArgs: true,
        handler: async (ctx) => {
            const query = ctx.args?.trim();
            if (!query) {
                return { text: "Usage: /recall <search query>" };
            }
            const results = await client.search(query, 5);
            if (results.length === 0) {
                return { text: "No matching memories found." };
            }
            const lines = results.map((r, i) => {
                const pct = r.similarity ? ` (${Math.round(r.similarity * 100)}%)` : "";
                return `${i + 1}. ${r.content}${pct}`;
            });
            return { text: `Found ${results.length} memories:\n\n${lines.join("\n")}` };
        },
    });
}
