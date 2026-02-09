import { LocalMemoryClient } from "./client.js";
import { parseConfig, localMemoryConfigSchema } from "./config.js";
import { initLogger } from "./logger.js";
import { buildRecallHandler } from "./hooks/recall.js";
import { buildCaptureHandler } from "./hooks/capture.js";
import { registerStoreTool } from "./tools/store.js";
import { registerSearchTool } from "./tools/search.js";
import { registerForgetTool } from "./tools/forget.js";
import { registerProfileTool } from "./tools/profile.js";
import { registerCommands } from "./commands/slash.js";
import { registerCli } from "./commands/cli.js";
export default {
    id: "clawdbot-local-memory",
    name: "Local Memory",
    description: "Supermemory-style local memory system",
    kind: "memory",
    configSchema: localMemoryConfigSchema,
    register(api) {
        const cfg = parseConfig(api.pluginConfig);
        initLogger(api.logger, cfg.debug);
        // Get workspace directory
        const workspaceDir = api.runtime.workspaceDir ?? process.cwd();
        const client = new LocalMemoryClient(workspaceDir);
        // Register tools
        registerStoreTool(api, client, cfg);
        registerSearchTool(api, client, cfg);
        registerForgetTool(api, client, cfg);
        registerProfileTool(api, client, cfg);
        // Register hooks
        if (cfg.autoRecall) {
            const recallHandler = buildRecallHandler(client, cfg);
            api.on("before_agent_start", (event, _ctx) => recallHandler(event));
        }
        if (cfg.autoCapture) {
            const captureHandler = buildCaptureHandler(client, cfg);
            api.on("agent_end", (event, _ctx) => captureHandler(event));
        }
        // Register commands
        registerCommands(api, client, cfg);
        registerCli(api, client, cfg);
        // Register service
        api.registerService({
            id: "clawdbot-local-memory",
            start: () => {
                api.logger.info("local-memory: started");
            },
            stop: () => {
                api.logger.info("local-memory: stopped");
            },
        });
    },
};
