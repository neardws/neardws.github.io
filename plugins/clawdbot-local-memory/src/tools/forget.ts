import { Type } from "@sinclair/typebox";
import type { ClawdbotPluginApi } from "clawdbot/plugin-sdk";
import type { LocalMemoryClient } from "../client.js";
import type { LocalMemoryConfig } from "../config.js";
import { log } from "../logger.js";

export function registerForgetTool(
  api: ClawdbotPluginApi,
  client: LocalMemoryClient,
  _cfg: LocalMemoryConfig
): void {
  api.registerTool(
    {
      name: "local_memory_forget",
      label: "Memory Forget",
      description: "Forget/delete a specific memory by query.",
      parameters: Type.Object({
        query: Type.String({ description: "Describe the memory to forget" }),
      }),
      async execute(
        _toolCallId: string,
        params: { query: string }
      ) {
        log.debug(`forget tool: query="${params.query}"`);
        const result = await client.forgetByQuery(params.query);
        return {
          content: [{ type: "text" as const, text: result.message }],
        };
      },
    },
    { name: "local_memory_forget" }
  );
}
