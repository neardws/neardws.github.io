import { log } from "../logger.js";
function formatRelativeTime(isoTimestamp) {
    try {
        const dt = new Date(isoTimestamp);
        const now = new Date();
        const seconds = (now.getTime() - dt.getTime()) / 1000;
        const minutes = seconds / 60;
        const hours = seconds / 3600;
        const days = seconds / 86400;
        if (minutes < 30)
            return "just now";
        if (minutes < 60)
            return `${Math.floor(minutes)}mins ago`;
        if (hours < 24)
            return `${Math.floor(hours)}hrs ago`;
        if (days < 7)
            return `${Math.floor(days)}d ago`;
        const month = dt.toLocaleString("en", { month: "short" });
        if (dt.getFullYear() === now.getFullYear()) {
            return `${dt.getDate()} ${month}`;
        }
        return `${dt.getDate()} ${month}, ${dt.getFullYear()}`;
    }
    catch {
        return "";
    }
}
function countUserTurns(messages) {
    let count = 0;
    for (const msg of messages) {
        if (msg && typeof msg === "object" &&
            msg.role === "user") {
            count++;
        }
    }
    return count;
}
function formatContext(staticFacts, dynamicFacts, searchResults, maxResults) {
    const statics = staticFacts.slice(0, maxResults);
    const dynamics = dynamicFacts.slice(0, maxResults);
    const search = searchResults.slice(0, maxResults);
    if (statics.length === 0 && dynamics.length === 0 && search.length === 0) {
        return null;
    }
    const sections = [];
    if (statics.length > 0) {
        sections.push("## User Profile (Persistent)\n" +
            statics.map((f) => `- ${f}`).join("\n"));
    }
    if (dynamics.length > 0) {
        sections.push(`## Recent Context\n${dynamics.map((f) => `- ${f}`).join("\n")}`);
    }
    if (search.length > 0) {
        const lines = search.map((r) => {
            const timeStr = r.timestamp ? formatRelativeTime(r.timestamp) : "";
            const pct = r.similarity != null ? `[${Math.round(r.similarity * 100)}%]` : "";
            const prefix = timeStr ? `[${timeStr}]` : "";
            return `- ${prefix} ${r.content} ${pct}`.trim();
        });
        sections.push(`## Relevant Memories (with relevance %)\n${lines.join("\n")}`);
    }
    const intro = "The following is recalled context about the user. Reference it only when relevant.";
    const disclaimer = "Use these memories naturally when relevant — don't force them into every response.";
    return `<local-memory-context>\n${intro}\n\n${sections.join("\n\n")}\n\n${disclaimer}\n</local-memory-context>`;
}
export function buildRecallHandler(client, cfg) {
    return async (event) => {
        const prompt = event.prompt;
        if (!prompt || prompt.length < 5)
            return;
        const messages = Array.isArray(event.messages) ? event.messages : [];
        const turn = countUserTurns(messages);
        const includeProfile = turn <= 1 || turn % cfg.profileFrequency === 0;
        log.debug(`recalling for turn ${turn} (profile: ${includeProfile})`);
        try {
            // Search for relevant memories
            const searchResults = await client.search(prompt, cfg.maxRecallResults);
            // Get profile if needed
            const profile = includeProfile ? await client.getProfile() : { static: [], dynamic: [] };
            const context = formatContext(profile.static, profile.dynamic, searchResults, cfg.maxRecallResults);
            if (!context) {
                log.debug("no memory data to inject");
                return;
            }
            log.debug(`injecting context (${context.length} chars, turn ${turn})`);
            return { prependContext: context };
        }
        catch (err) {
            log.error("recall failed", err);
            return;
        }
    };
}
