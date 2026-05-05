import type { ManifestEntry } from '../catalog/manifest.js';
export type DiffCategory = '+' | '~' | '=' | '-' | '!';
export interface DiffEntry {
    category: DiffCategory;
    relativePath: string;
    entry?: ManifestEntry;
}
export interface DiffResult {
    entries: DiffEntry[];
    hasChanges: boolean;
}
export declare function calculateDiff(manifestEntries: ManifestEntry[], remoteContents: Map<string, string>, installedFiles: string[], force?: boolean): Promise<DiffResult>;
//# sourceMappingURL=diff.d.ts.map