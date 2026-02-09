import type { PluginLogger } from "clawdbot/plugin-sdk";

let _logger: PluginLogger | null = null;
let _debug = false;

export function initLogger(logger: PluginLogger, debug: boolean): void {
  _logger = logger;
  _debug = debug;
}

export const log = {
  info: (msg: string) => _logger?.info(`[local-memory] ${msg}`),
  warn: (msg: string) => _logger?.warn(`[local-memory] ${msg}`),
  error: (msg: string, err?: unknown) => {
    const errStr = err instanceof Error ? err.message : String(err ?? "");
    _logger?.error(`[local-memory] ${msg}${errStr ? `: ${errStr}` : ""}`);
  },
  debug: (msg: string) => {
    if (_debug) _logger?.info(`[local-memory:debug] ${msg}`);
  },
  debugRequest: (op: string, data: Record<string, unknown>) => {
    if (_debug) _logger?.info(`[local-memory:debug] ${op} request: ${JSON.stringify(data)}`);
  },
  debugResponse: (op: string, data: Record<string, unknown>) => {
    if (_debug) _logger?.info(`[local-memory:debug] ${op} response: ${JSON.stringify(data)}`);
  },
};
