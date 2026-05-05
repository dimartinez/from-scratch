export interface SummaryBlock {
    installed: number;
    updated: number;
    unchanged: number;
    nextStep: string;
}
export declare function formatSummary(summary: SummaryBlock): string;
export declare function formatDiff(entries: Array<{
    category: string;
    relativePath: string;
}>, unchangedCount: number): string;
export declare function containsEmojis(text: string): boolean;
export declare function formatError(message: string): string;
export declare function formatWarning(message: string): string;
//# sourceMappingURL=output.d.ts.map