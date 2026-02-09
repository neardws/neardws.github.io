import type { ClawdbotPluginApi } from "clawdbot/plugin-sdk";
import type { LocalMemoryClient } from "../client.js";
import type { LocalMemoryConfig } from "../config.js";

export function registerCli(
  api: ClawdbotPluginApi,
  client: LocalMemoryClient,
  _cfg: LocalMemoryConfig
): void {
  api.registerCli((ctx) => {
    const cmd = ctx.program
      .command("local-memory")
      .description("Local memory management");

    cmd
      .command("search <query>")
      .description("Search memories")
      .option("-l, --limit <n>", "Max results", "5")
      .action(async (query: string, opts: { limit: string }) => {
        const results = await client.search(query, parseInt(opts.limit));
        if (results.length === 0) {
          console.log("No memories found.");
          return;
        }
        for (const r of results) {
          const pct = r.similarity ? ` (${Math.round(r.similarity * 100)}%)` : "";
          console.log(`- ${r.content}${pct}`);
        }
      });

    cmd
      .command("profile")
      .description("View user profile")
      .action(async () => {
        const profile = await client.getProfile();
        if (profile.static.length === 0 && profile.dynamic.length === 0) {
          console.log("No profile data yet.");
          return;
        }
        if (profile.static.length > 0) {
          console.log("## Persistent Facts");
          profile.static.forEach(f => console.log(`- ${f}`));
        }
        if (profile.dynamic.length > 0) {
          console.log("\n## Recent Context");
          profile.dynamic.forEach(f => console.log(`- ${f}`));
        }
      });

    cmd
      .command("stats")
      .description("Show memory statistics")
      .action(async () => {
        const count = await client.getMemoryCount();
        const profile = await client.getProfile();
        console.log(`Memories: ${count}`);
        console.log(`Profile: ${profile.static.length} static, ${profile.dynamic.length} dynamic`);
      });

    cmd
      .command("wipe")
      .description("Delete all memories (destructive)")
      .option("-y, --yes", "Skip confirmation")
      .action(async (opts: { yes?: boolean }) => {
        if (!opts.yes) {
          console.log("This will delete ALL memories. Use --yes to confirm.");
          return;
        }
        const result = await client.wipeAll();
        console.log(`Deleted ${result.deletedCount} memories.`);
      });
  });
}
