let _logger = null;
let _debug = false;
export function initLogger(logger, debug) {
    _logger = logger;
    _debug = debug;
}
export const log = {
    info: (msg) => _logger?.info(`[local-memory] ${msg}`),
    warn: (msg) => _logger?.warn(`[local-memory] ${msg}`),
    error: (msg, err) => {
        const errStr = err instanceof Error ? err.message : String(err ?? "");
        _logger?.error(`[local-memory] ${msg}${errStr ? `: ${errStr}` : ""}`);
    },
    debug: (msg) => {
        if (_debug)
            _logger?.info(`[local-memory:debug] ${msg}`);
    },
    debugRequest: (op, data) => {
        if (_debug)
            _logger?.info(`[local-memory:debug] ${op} request: ${JSON.stringify(data)}`);
    },
    debugResponse: (op, data) => {
        if (_debug)
            _logger?.info(`[local-memory:debug] ${op} response: ${JSON.stringify(data)}`);
    },
};
