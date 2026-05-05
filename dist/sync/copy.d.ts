import type { KnownKind } from '../catalog/manifest.js';
export declare function getClaudeDir(): string;
export declare function getDestinationPath(kind: KnownKind, source: string): string;
export declare function getRelativePath(kind: KnownKind, source: string): string;
export declare function validateFrontmatter(content: string): boolean;
export declare function writeFileAtomic(destPath: string, content: string): Promise<void>;
export declare function createBackup(destPath: string): Promise<string>;
//# sourceMappingURL=copy.d.ts.map