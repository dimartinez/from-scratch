import { getRelativePath } from './copy.js';
import { promises as fs } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
async function readLocalFile(relativePath) {
    try {
        return await fs.readFile(join(homedir(), '.claude', relativePath), 'utf8');
    }
    catch {
        return null;
    }
}
export async function calculateDiff(manifestEntries, remoteContents, installedFiles, force = false) {
    const entries = [];
    const processedPaths = new Set();
    for (const entry of manifestEntries) {
        const kind = entry.kind;
        const relativePath = getRelativePath(kind, entry.source);
        processedPaths.add(relativePath);
        const remoteContent = remoteContents.get(entry.source);
        if (remoteContent === undefined)
            continue;
        const localContent = await readLocalFile(relativePath);
        if (localContent === null) {
            entries.push({ category: '+', relativePath, entry });
        }
        else if (installedFiles.includes(relativePath)) {
            if (localContent === remoteContent) {
                entries.push({ category: '=', relativePath, entry });
            }
            else {
                entries.push({ category: '~', relativePath, entry });
            }
        }
        else {
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
//# sourceMappingURL=diff.js.map