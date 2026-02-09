export type MemoryEntry = {
    id: string;
    content: string;
    category: MemoryCategory;
    timestamp: string;
    source: string;
    metadata?: Record<string, unknown>;
};
export type ProfileResult = {
    static: string[];
    dynamic: string[];
};
export declare const MEMORY_CATEGORIES: readonly ["preference", "fact", "decision", "entity", "context", "other"];
export type MemoryCategory = (typeof MEMORY_CATEGORIES)[number];
export declare function detectCategory(text: string): MemoryCategory;
