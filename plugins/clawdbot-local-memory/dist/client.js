import fs from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { log } from "./logger.js";
import { detectCategory } from "./memory.js";
const MEMORY_FILE = "local-memory.json";
const PROFILE_FILE = "local-profile.json";
// Vector embedding service config
const EMBEDDING_API_URL = "http://localhost:8001";
const EMBEDDING_API_KEY = "WIXL-QFV8oCpLU0ZHBkyx-mt-otVL2kUq9eNlLoP5_0";
const COLLECTION_NAME = "local_memory";
async function embeddingFetch(endpoint, method, body) {
    return fetch(`${EMBEDDING_API_URL}${endpoint}`, {
        method,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${EMBEDDING_API_KEY}`,
        },
        body: body ? JSON.stringify(body) : undefined,
    });
}
export class LocalMemoryClient {
    workspaceDir;
    memories = [];
    profile = { static: [], dynamic: [] };
    loaded = false;
    embeddingAvailable = null;
    constructor(workspaceDir) {
        this.workspaceDir = workspaceDir;
    }
    async checkEmbeddingService() {
        if (this.embeddingAvailable !== null)
            return this.embeddingAvailable;
        try {
            const resp = await embeddingFetch("/collections", "GET");
            this.embeddingAvailable = resp.ok;
            if (this.embeddingAvailable) {
                // Ensure collection exists
                await this.ensureCollection();
            }
            log.debug(`embedding service available: ${this.embeddingAvailable}`);
        }
        catch {
            this.embeddingAvailable = false;
            log.debug("embedding service unavailable, using keyword fallback");
        }
        return this.embeddingAvailable;
    }
    async ensureCollection() {
        try {
            await embeddingFetch("/collections", "POST", { name: COLLECTION_NAME });
        }
        catch {
            // Collection may already exist, ignore error
        }
    }
    get memoryPath() {
        return path.join(this.workspaceDir, ".clawdbot", MEMORY_FILE);
    }
    get profilePath() {
        return path.join(this.workspaceDir, ".clawdbot", PROFILE_FILE);
    }
    async ensureLoaded() {
        if (this.loaded)
            return;
        await this.load();
        this.loaded = true;
    }
    async load() {
        try {
            const dir = path.dirname(this.memoryPath);
            await fs.mkdir(dir, { recursive: true });
            const memData = await fs.readFile(this.memoryPath, "utf-8").catch(() => "[]");
            this.memories = JSON.parse(memData);
            const profData = await fs.readFile(this.profilePath, "utf-8").catch(() => '{"static":[],"dynamic":[]}');
            this.profile = JSON.parse(profData);
            log.debug(`loaded ${this.memories.length} memories, profile: ${this.profile.static.length} static, ${this.profile.dynamic.length} dynamic`);
        }
        catch (err) {
            log.error("failed to load memory", err);
            this.memories = [];
            this.profile = { static: [], dynamic: [] };
        }
    }
    async save() {
        try {
            const dir = path.dirname(this.memoryPath);
            await fs.mkdir(dir, { recursive: true });
            await fs.writeFile(this.memoryPath, JSON.stringify(this.memories, null, 2));
            await fs.writeFile(this.profilePath, JSON.stringify(this.profile, null, 2));
        }
        catch (err) {
            log.error("failed to save memory", err);
        }
    }
    async addMemory(content, category, source = "conversation", metadata) {
        await this.ensureLoaded();
        const entry = {
            id: randomUUID(),
            content: content.trim(),
            category: category ?? detectCategory(content),
            timestamp: new Date().toISOString(),
            source,
            metadata,
        };
        this.memories.push(entry);
        await this.save();
        // Add to vector database
        if (await this.checkEmbeddingService()) {
            try {
                await embeddingFetch("/documents", "POST", {
                    collection: COLLECTION_NAME,
                    documents: [entry.content],
                    ids: [entry.id],
                    metadatas: [{
                            category: entry.category,
                            timestamp: entry.timestamp,
                            source: entry.source,
                            ...entry.metadata,
                        }],
                });
                log.debug(`added to vector db: ${entry.id}`);
            }
            catch (err) {
                log.error("failed to add to vector db", err);
            }
        }
        log.debug(`added memory: ${entry.id} (${entry.category})`);
        return { id: entry.id };
    }
    async search(query, limit = 5) {
        await this.ensureLoaded();
        // Try semantic search first
        if (await this.checkEmbeddingService()) {
            try {
                const resp = await embeddingFetch("/query", "POST", {
                    collection: COLLECTION_NAME,
                    query,
                    n_results: limit,
                });
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.ids?.length > 0) {
                        const results = [];
                        for (let i = 0; i < data.ids.length; i++) {
                            const id = data.ids[i];
                            const distance = data.distances[i];
                            // Convert distance to similarity (lower distance = higher similarity)
                            const similarity = Math.max(0, 1 - distance);
                            // Find full memory entry from local storage
                            const memory = this.memories.find(m => m.id === id);
                            if (memory) {
                                results.push({
                                    id: memory.id,
                                    content: memory.content,
                                    category: memory.category,
                                    similarity,
                                    timestamp: memory.timestamp,
                                });
                            }
                        }
                        log.debug(`semantic search returned ${results.length} results`);
                        return results;
                    }
                }
            }
            catch (err) {
                log.error("semantic search failed, falling back to keyword", err);
            }
        }
        // Fallback to keyword matching
        return this.keywordSearch(query, limit);
    }
    keywordSearch(query, limit) {
        const queryLower = query.toLowerCase();
        const queryWords = queryLower.split(/\s+/).filter(w => w.length > 2);
        // Simple keyword matching with scoring
        const scored = this.memories.map(m => {
            const contentLower = m.content.toLowerCase();
            let score = 0;
            // Exact phrase match
            if (contentLower.includes(queryLower))
                score += 0.5;
            // Word matches
            for (const word of queryWords) {
                if (contentLower.includes(word))
                    score += 0.2;
            }
            // Recency boost (newer = higher)
            const age = Date.now() - new Date(m.timestamp).getTime();
            const dayAge = age / (1000 * 60 * 60 * 24);
            score += Math.max(0, 0.1 * (1 - dayAge / 30)); // Boost for last 30 days
            return { ...m, similarity: Math.min(score, 1) };
        });
        return scored
            .filter(m => m.similarity > 0)
            .sort((a, b) => b.similarity - a.similarity)
            .slice(0, limit)
            .map(m => ({
            id: m.id,
            content: m.content,
            category: m.category,
            similarity: m.similarity,
            timestamp: m.timestamp,
        }));
    }
    async deleteMemory(id) {
        await this.ensureLoaded();
        const idx = this.memories.findIndex(m => m.id === id);
        if (idx === -1)
            return false;
        this.memories.splice(idx, 1);
        await this.save();
        // Delete from vector database
        if (await this.checkEmbeddingService()) {
            try {
                await embeddingFetch("/documents", "DELETE", {
                    collection: COLLECTION_NAME,
                    ids: [id],
                });
                log.debug(`deleted from vector db: ${id}`);
            }
            catch (err) {
                log.error("failed to delete from vector db", err);
            }
        }
        log.debug(`deleted memory: ${id}`);
        return true;
    }
    async forgetByQuery(query) {
        // Use semantic search to find the most relevant memory to forget
        const results = await this.search(query, 1);
        if (results.length === 0) {
            return { success: false, message: "No matching memory found." };
        }
        const target = results[0];
        await this.deleteMemory(target.id);
        const preview = target.content.length > 80
            ? `${target.content.slice(0, 80)}…`
            : target.content;
        return { success: true, message: `Forgot: "${preview}" (similarity: ${target.similarity?.toFixed(2) ?? 'N/A'})` };
    }
    async getProfile() {
        await this.ensureLoaded();
        // Auto-generate profile from memories if empty
        if (this.profile.static.length === 0 && this.profile.dynamic.length === 0) {
            return this.generateProfileFromMemories();
        }
        return { ...this.profile };
    }
    generateProfileFromMemories() {
        const now = Date.now();
        const oneWeekMs = 7 * 24 * 60 * 60 * 1000;
        const staticFacts = [];
        const dynamicFacts = [];
        for (const m of this.memories) {
            const age = now - new Date(m.timestamp).getTime();
            const isRecent = age < oneWeekMs;
            // Categorize into static vs dynamic
            if (m.category === "fact" || m.category === "entity") {
                staticFacts.push(m.content);
            }
            else if (m.category === "preference" || m.category === "decision") {
                // Preferences/decisions are static (persistent)
                staticFacts.push(`[${m.category}] ${m.content}`);
            }
            else if (isRecent) {
                // Recent context/other goes to dynamic
                dynamicFacts.push(m.content);
            }
        }
        return { static: staticFacts, dynamic: dynamicFacts };
    }
    async updateProfile(staticFacts, dynamicFacts) {
        await this.ensureLoaded();
        this.profile.static = staticFacts;
        this.profile.dynamic = dynamicFacts;
        await this.save();
        log.debug(`updated profile: ${staticFacts.length} static, ${dynamicFacts.length} dynamic`);
    }
    async addToProfile(fact, isStatic) {
        await this.ensureLoaded();
        const arr = isStatic ? this.profile.static : this.profile.dynamic;
        if (!arr.includes(fact)) {
            arr.push(fact);
            await this.save();
        }
    }
    async getMemoryCount() {
        await this.ensureLoaded();
        return this.memories.length;
    }
    async wipeAll() {
        await this.ensureLoaded();
        const count = this.memories.length;
        const ids = this.memories.map(m => m.id);
        this.memories = [];
        this.profile = { static: [], dynamic: [] };
        await this.save();
        // Delete all from vector database
        if (ids.length > 0 && await this.checkEmbeddingService()) {
            try {
                await embeddingFetch("/documents", "DELETE", {
                    collection: COLLECTION_NAME,
                    ids,
                });
                log.debug(`wiped ${ids.length} from vector db`);
            }
            catch (err) {
                log.error("failed to wipe vector db", err);
            }
        }
        log.info(`wiped all memories: ${count} deleted`);
        return { deletedCount: count };
    }
    // Sync existing JSON memories to vector database (for migration)
    async syncToVectorDb() {
        await this.ensureLoaded();
        if (!(await this.checkEmbeddingService())) {
            return { synced: 0, failed: this.memories.length };
        }
        let synced = 0;
        let failed = 0;
        // Batch upload in chunks of 100
        const chunkSize = 100;
        for (let i = 0; i < this.memories.length; i += chunkSize) {
            const chunk = this.memories.slice(i, i + chunkSize);
            try {
                await embeddingFetch("/documents", "POST", {
                    collection: COLLECTION_NAME,
                    documents: chunk.map(m => m.content),
                    ids: chunk.map(m => m.id),
                    metadatas: chunk.map(m => ({
                        category: m.category,
                        timestamp: m.timestamp,
                        source: m.source,
                        ...m.metadata,
                    })),
                });
                synced += chunk.length;
            }
            catch (err) {
                log.error(`failed to sync chunk at ${i}`, err);
                failed += chunk.length;
            }
        }
        log.info(`synced ${synced} memories to vector db, ${failed} failed`);
        return { synced, failed };
    }
}
