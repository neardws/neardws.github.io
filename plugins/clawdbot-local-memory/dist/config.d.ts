export type LocalMemoryConfig = {
    autoRecall: boolean;
    autoCapture: boolean;
    maxRecallResults: number;
    profileFrequency: number;
    extractionModel: string;
    debug: boolean;
};
export declare function parseConfig(raw: unknown): LocalMemoryConfig;
export declare const localMemoryConfigSchema: {
    parse: typeof parseConfig;
};
