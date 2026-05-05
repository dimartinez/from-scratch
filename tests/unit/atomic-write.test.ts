import { describe, it, expect, vi, afterEach } from 'vitest';
import { writeFileAtomic } from '../../src/sync/copy.js';
import { promises as fs } from 'fs';
import { join } from 'path';
import os from 'os';

describe('writeFileAtomic (task 11.1, 11.2)', () => {
  let tmpDir: string;

  afterEach(async () => {
    if (tmpDir) await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('writes the file to its final destination (no .tmp left behind)', async () => {
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'atomic-test-'));
    const dest = join(tmpDir, 'result.md');
    await writeFileAtomic(dest, 'hello world');
    const content = await fs.readFile(dest, 'utf8');
    expect(content).toBe('hello world');
    await expect(fs.access(`${dest}.tmp`)).rejects.toThrow();
  });

  it('writes via .tmp first (rename to final path)', async () => {
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'atomic-test-'));
    const dest = join(tmpDir, 'subdir', 'file.md');

    const renameSpy = vi.spyOn(fs, 'rename');
    await writeFileAtomic(dest, 'content');

    expect(renameSpy).toHaveBeenCalledWith(`${dest}.tmp`, dest);
    renameSpy.mockRestore();
  });

  it('creates intermediate directories as needed', async () => {
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'atomic-test-'));
    const dest = join(tmpDir, 'a', 'b', 'c', 'file.md');
    await writeFileAtomic(dest, 'nested');
    const content = await fs.readFile(dest, 'utf8');
    expect(content).toBe('nested');
  });
});

describe('State file incomplete sync detection (task 11.7)', () => {
  it('hasIncompleteSync detects started > completed as interrupted', async () => {
    const { hasIncompleteSync } = await import('../../src/state/state.js');
    const state = {
      last_sync_started_at: '2024-01-01T11:00:00Z',
      last_sync_completed_at: '2024-01-01T10:00:00Z',
      installed_files: ['commands/new-project.md'],
      catalog_version: '0.1.0',
      binary_version: '0.1.0',
    };
    expect(hasIncompleteSync(state)).toBe(true);
  });
});
