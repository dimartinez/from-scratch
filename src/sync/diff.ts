import type { ManifestEntry } from '../catalog/manifest.js';
import type { KnownKind } from '../catalog/manifest.js';
import { getRelativePath } from './copy.js';
import { promises as fs } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

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

async function readLocalFile(relativePath: string): Promise<string | null> {
  try {
    return await fs.readFile(join(homedir(), '.claude', relativePath), 'utf8');
  } catch {
    return null;
  }
}

export async function calculateDiff(
  manifestEntries: ManifestEntry[],
  remoteContents: Map<string, string>,
  installedFiles: string[],
  force: boolean = false
): Promise<DiffResult> {
  const entries: DiffEntry[] = [];
  const processedPaths = new Set<string>();

  for (const entry of manifestEntries) {
    const kind = entry.kind as KnownKind;
    const relativePath = getRelativePath(kind, entry.source);
    processedPaths.add(relativePath);

    const remoteContent = remoteContents.get(entry.source);
    if (remoteContent === undefined) continue;

    const localContent = await readLocalFile(relativePath);

    if (localContent === null) {
      entries.push({ category: '+', relativePath, entry });
    } else if (installedFiles.includes(relativePath)) {
      if (localContent === remoteContent) {
        entries.push({ category: '=', relativePath, entry });
      } else {
        entries.push({ category: '~', relativePath, entry });
      }
    } else {
      entries.push({ category: '!', relativePath, entry });
    }
  }

  for (const installedPath of installedFiles) {
    if (!processedPaths.has(installedPath)) {
      entries.push({ category: '-', relativePath: installedPath });
    }
  }

  const hasChanges = entries.some((e) => e.category !== '=');
  return { entries, hasChanges };
}
