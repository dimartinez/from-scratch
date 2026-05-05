import { homedir } from 'os';
import { join } from 'path';
import { promises as fs } from 'fs';
export function getStateFilePath() {
    return join(homedir(), '.claude', 'from-scratch', '.state.json');
}
export async function readState() {
    try {
        const content = await fs.readFile(getStateFilePath(), 'utf8');
        return JSON.parse(content);
    }
    catch {
        return null;
    }
}
export async function writeState(state) {
    const path = getStateFilePath();
    const dir = join(path, '..');
    await fs.mkdir(dir, { recursive: true });
    const tmpPath = `${path}.tmp`;
    await fs.writeFile(tmpPath, JSON.stringify(state, null, 2), 'utf8');
    await fs.rename(tmpPath, path);
}
export function hasIncompleteSync(state) {
    if (!state.last_sync_started_at)
        return false;
    if (!state.last_sync_completed_at)
        return true;
    return new Date(state.last_sync_started_at) > new Date(state.last_sync_completed_at);
}
export function isInstalled(state) {
    if (!state)
        return false;
    return state.installed_files.length > 0;
}
//# sourceMappingURL=state.js.map