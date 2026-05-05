import { homedir } from 'os';
import { join } from 'path';
import { promises as fs } from 'fs';

export interface StateFile {
  last_sync_started_at: string | null;
  last_sync_completed_at: string | null;
  installed_files: string[];
  catalog_version: string;
  binary_version: string;
}

export function getStateFilePath(): string {
  return join(homedir(), '.claude', 'from-scratch', '.state.json');
}

export async function readState(): Promise<StateFile | null> {
  try {
    const content = await fs.readFile(getStateFilePath(), 'utf8');
    return JSON.parse(content) as StateFile;
  } catch {
    return null;
  }
}

export async function writeState(state: StateFile): Promise<void> {
  const path = getStateFilePath();
  const dir = join(path, '..');
  await fs.mkdir(dir, { recursive: true });
  const tmpPath = `${path}.tmp`;
  await fs.writeFile(tmpPath, JSON.stringify(state, null, 2), 'utf8');
  await fs.rename(tmpPath, path);
}

export function hasIncompleteSync(state: StateFile): boolean {
  if (!state.last_sync_started_at) return false;
  if (!state.last_sync_completed_at) return true;
  return new Date(state.last_sync_started_at) > new Date(state.last_sync_completed_at);
}

export function isInstalled(state: StateFile | null): boolean {
  if (!state) return false;
  return state.installed_files.length > 0;
}
