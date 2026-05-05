export declare const KNOWN_KINDS: readonly ["command", "stack"];
export type KnownKind = (typeof KNOWN_KINDS)[number];
export interface ManifestEntry {
    kind: string;
    source: string;
}
export interface Manifest {
    version: string;
    requires_binary: string;
    entries: ManifestEntry[];
}
export declare function parseManifest(raw: unknown): Manifest;
export declare function validateKinds(manifest: Manifest): {
    unknownKind: string;
} | null;
//# sourceMappingURL=manifest.d.ts.map