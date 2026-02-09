import { type MemoryCategory, type ProfileResult } from "./memory.js";
export type SearchResult = {
    id: string;
    content: string;
    category: MemoryCategory;
    similarity?: number;
    timestamp: string;
};
export declare class LocalMemoryClient {
    private workspaceDir;
    private memories;
    private profile;
    private loaded;
    private embeddingAvailable;
    constructor(workspaceDir: string);
    private checkEmbeddingService;
    private ensureCollection;
    private get memoryPath();
    private get profilePath();
    ensureLoaded(): Promise<void>;
    private load;
    private save;
    addMemory(content: string, category?: MemoryCategory, source?: string, metadata?: Record<string, unknown>): Promise<{
        id: string;
    }>;
    search(query: string, limit?: number): Promise<SearchResult[]>;
    private keywordSearch;
    deleteMemory(id: string): Promise<boolean>;
    forgetByQuery(query: string): Promise<{
        success: boolean;
        message: string;
    }>;
    getProfile(): Promise<ProfileResult>;
    private generateProfileFromMemories;
    updateProfile(staticFacts: string[], dynamicFacts: string[]): Promise<void>;
    addToProfile(fact: string, isStatic: boolean): Promise<void>;
    getMemoryCount(): Promise<number>;
    wipeAll(): Promise<{
        deletedCount: number;
    }>;
    syncToVectorDb(): Promise<{
        synced: number;
        failed: number;
    }>;
}
