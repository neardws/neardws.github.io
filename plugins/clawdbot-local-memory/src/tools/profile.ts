import { Type } from "@sinclair/typebox";
import type { ClawdbotPluginApi } from "clawdbot/plugin-sdk";
import type { LocalMemoryClient } from "../client.js";
import type { LocalMemoryConfig } from "../config.js";
import { log } from "../logger.js";

export function registerProfileTool(
  api: ClawdbotPluginApi,
  client: LocalMemoryClient,
  _cfg: LocalMemoryConfig
): void {
  api.registerTool(
    {
      name: "local_memory_profile",
      label: "User Profile",
      description: "Get user profile - persistent facts and recent context.",
      parameters: Type.Object({}),
      async execute(_toolCallId: string) {
        log.debug("profile tool called");
        const profile = await client.getProfile();

        if (profile.static.length === 0 && profile.dynamic.length === 0) {
          return {
            content: [
              { type: "text" as const, text: "No profile information yet." },
            ],
          };
        }

        const sections: string[] = [];
        if (profile.static.length > 0) {
          sections.push(
            "## Persistent Facts\n" +
            profile.static.map((f) => `- ${f}`).join("\n")
          );
        }
        if (profile.dynamic.length > 0) {
          sections.push(
            "## Recent Context\n" +
            profile.dynamic.map((f) => `- ${f}`).join("\n")
          );
        }

        return {
          content: [{ type: "text" as const, text: sections.join("\n\n") }],
        };
      },
    },
    { name: "local_memory_profile" }
  );
}
