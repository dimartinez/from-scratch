import { homedir } from 'os';
import { join, dirname, basename } from 'path';
import { promises as fs } from 'fs';
import yaml from 'js-yaml';
export function getClaudeDir() {
    return join(homedir(), '.claude');
}
export function getDestinationPath(kind, source) {
    const claudeDir = getClaudeDir();
    const fileName = basename(source);
    if (kind === 'command') {
        return join(claudeDir, 'commands', fileName);
    }
    if (kind === 'stack') {
        return join(claudeDir, 'from-scratch', 'stacks', fileName);
    }
    throw new Error(`Unknown kind: ${kind}`);
}
export function getRelativePath(kind, source) {
    const fileName = basename(source);
    if (kind === 'command')
        return `commands/${fileName}`;
    if (kind === 'stack')
        return `from-scratch/stacks/${fileName}`;
    throw new Error(`Unknown kind: ${kind}`);
}
export function validateFrontmatter(content) {
    if (!content.startsWith('---'))
        return false;
    const end = content.indexOf('---', 3);
    if (end === -1)
        return false;
    const frontmatter = content.slice(3, end).trim();
    try {
        const parsed = yaml.load(frontmatter);
        return parsed !== null && typeof parsed === 'object';
    }
    catch {
        return false;
    }
}
export async function writeFileAtomic(destPath, content) {
    const tmpPath = `${destPath}.tmp`;
    await fs.mkdir(dirname(destPath), { recursive: true });
    await fs.writeFile(tmpPath, content, 'utf8');
    await fs.rename(tmpPath, destPath);
}
export async function createBackup(destPath) {
    const timestamp = Date.now();
    const backupPath = `${destPath}.bak.${timestamp}`;
    const content = await fs.readFile(destPath, 'utf8');
    await fs.writeFile(backupPath, content, 'utf8');
    return backupPath;
}
//# sourceMappingURL=copy.js.map