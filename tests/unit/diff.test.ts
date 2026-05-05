import { describe, it, expect, vi, beforeEach } from 'vitest';
import { calculateDiff } from '../../src/sync/diff.js';
import type { ManifestEntry } from '../../src/catalog/manifest.js';

vi.mock('fs', async (importOriginal) => {
  const original = await importOriginal<typeof import('fs')>();
  return {
    ...original,
    promises: {
      ...original.promises,
      readFile: vi.fn(),
    },
  };
});

import { promises as fs } from 'fs';

const entries: ManifestEntry[] = [
  { kind: 'command', source: 'commands/new-project.md' },
  { kind: 'stack', source: 'stacks/java.md' },
];

const remoteContents = new Map([
  ['commands/new-project.md', '---\ndescription: new\n---\nNew content'],
  ['stacks/java.md', '---\nname: Java\n---'],
]);

describe('calculateDiff', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('classifies a new file as + when not present locally', async () => {
    vi.mocked(fs.readFile).mockRejectedValue(new Error('ENOENT'));
    const result = await calculateDiff(entries, remoteContents, []);
    expect(result.entries.some((e) => e.category === '+' && e.relativePath === 'commands/new-project.md')).toBe(true);
  });

  it('classifies a modified file as ~ when local content differs', async () => {
    vi.mocked(fs.readFile).mockResolvedValue('old content' as never);
    const installed = ['commands/new-project.md', 'from-scratch/stacks/java.md'];
    const result = await calculateDiff(entries, remoteContents, installed);
    expect(result.entries.some((e) => e.category === '~')).toBe(true);
  });

  it('classifies an unchanged file as = when local matches remote', async () => {
    vi.mocked(fs.readFile).mockImplementation(async (path: unknown) => {
      if (String(path).includes('new-project')) return remoteContents.get('commands/new-project.md')!;
      return remoteContents.get('stacks/java.md')!;
    });
    const installed = ['commands/new-project.md', 'from-scratch/stacks/java.md'];
    const result = await calculateDiff(entries, remoteContents, installed);
    expect(result.entries.every((e) => e.category === '=')).toBe(true);
    expect(result.hasChanges).toBe(false);
  });

  it('classifies a removed file as - when it was installed but no longer in manifest', async () => {
    vi.mocked(fs.readFile).mockRejectedValue(new Error('ENOENT'));
    const installed = ['commands/old-command.md'];
    const singleEntry: ManifestEntry[] = [{ kind: 'command', source: 'commands/new-project.md' }];
    const remote = new Map([['commands/new-project.md', 'new content']]);
    const result = await calculateDiff(singleEntry, remote, installed);
    expect(result.entries.some((e) => e.category === '-' && e.relativePath === 'commands/old-command.md')).toBe(true);
  });

  it('classifies a conflict as ! when file exists but was not installed by from-scratch', async () => {
    vi.mocked(fs.readFile).mockResolvedValue('user content' as never);
    const result = await calculateDiff(entries, remoteContents, []);
    expect(result.entries.some((e) => e.category === '!')).toBe(true);
  });

  it('hasChanges is true when there are non-= entries', async () => {
    vi.mocked(fs.readFile).mockRejectedValue(new Error('ENOENT'));
    const result = await calculateDiff(entries, remoteContents, []);
    expect(result.hasChanges).toBe(true);
  });
});
