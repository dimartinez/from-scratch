import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { join } from 'path';
import { promises as fs } from 'fs';
import os from 'os';
import { runUpdate } from '../../src/commands/update.js';
import type { Fetcher } from '../../src/sync/download.js';

vi.mock('../../src/state/state.js', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../src/state/state.js')>();
  let stateFile: Record<string, unknown> | null = null;
  return {
    ...original,
    readState: vi.fn(async () => stateFile),
    writeState: vi.fn(async (s: unknown) => { stateFile = s as Record<string, unknown>; }),
    isInstalled: vi.fn((s: unknown) => {
      if (!s) return false;
      const state = s as { installed_files: unknown[] };
      return Array.isArray(state.installed_files) && state.installed_files.length > 0;
    }),
    __setMockState: (s: unknown) => { stateFile = s as Record<string, unknown> | null; },
  };
});

import { readState, writeState } from '../../src/state/state.js';

const manifest = {
  version: '0.2.0',
  requires_binary: '0.1.0',
  entries: [
    { kind: 'command', source: 'commands/new-project.md' },
    { kind: 'stack', source: 'stacks/java.md' },
    { kind: 'stack', source: 'stacks/node.md' },
  ],
};

const remoteFiles: Record<string, string> = {
  'commands/new-project.md': '---\ndescription: New\n---\nNew content',
  'stacks/java.md': '---\nname: Java\ndescription: Updated\ntemplate_url: github.com/x/y\n---',
  'stacks/node.md': '---\nname: Node\ndescription: New stack\ntemplate_url: github.com/x/node\n---',
};

function makeFetcher(): Fetcher {
  return {
    fetch: async (url: string) => {
      if (url.includes('catalog.json')) {
        return { ok: true, status: 200, text: async () => JSON.stringify(manifest) };
      }
      for (const [key, body] of Object.entries(remoteFiles)) {
        if (url.includes(key)) {
          return { ok: true, status: 200, text: async () => body };
        }
      }
      return { ok: false, status: 404, text: async () => '' };
    },
  };
}

describe('update — no changes (6.6, 6.7)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-update-test-'));

    const cmdDir = join(tmpDir, 'commands');
    const stackDir = join(tmpDir, 'from-scratch', 'stacks');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.mkdir(stackDir, { recursive: true });
    await fs.writeFile(join(cmdDir, 'new-project.md'), remoteFiles['commands/new-project.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'java.md'), remoteFiles['stacks/java.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'node.md'), remoteFiles['stacks/node.md'], 'utf8');

    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: ['commands/new-project.md', 'from-scratch/stacks/java.md', 'from-scratch/stacks/node.md'],
      catalog_version: '0.2.0',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('prints "Tu catálogo está al día (vX.Y.Z)." and exits 0', async () => {
    const result = await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.exitCode).toBe(0);
    expect(result.output.join('\n')).toContain('Tu catálogo está al día');
    expect(result.output.join('\n')).toContain('0.2.0');
  });

  it('does not ask for confirmation when there are no changes', async () => {
    const confirmFn = vi.fn(async () => true);
    await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn,
      logFn: () => {},
    });
    expect(confirmFn).not.toHaveBeenCalled();
  });
});

describe('update — with changes (6.1-6.5, 6.10-6.13)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-update-changes-test-'));
    const cmdDir = join(tmpDir, 'commands');
    const stackDir = join(tmpDir, 'from-scratch', 'stacks');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.mkdir(stackDir, { recursive: true });

    await fs.writeFile(join(cmdDir, 'new-project.md'), 'OLD content', 'utf8');
    await fs.writeFile(join(stackDir, 'java.md'), remoteFiles['stacks/java.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'old-command.md'), 'to be removed', 'utf8');

    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: ['commands/new-project.md', 'from-scratch/stacks/java.md', 'from-scratch/stacks/old-command.md'],
      catalog_version: '0.1.0',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('diff output uses +, ~, - prefixes', async () => {
    const result = await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => false,
      logFn: () => {},
    });
    const combined = result.output.join('\n');
    expect(combined).toMatch(/[+~-]/);
  });

  it('unchanged files are shown as aggregate count, not individually', async () => {
    const result = await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => false,
      logFn: () => {},
    });
    const combined = result.output.join('\n');
    expect(combined).toMatch(/\d+ archivos sin cambios/);
  });

  it('asks for confirmation with "¿Aplicar estos cambios?"', async () => {
    const questions: string[] = [];
    await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async (q) => { questions.push(q); return false; },
      logFn: () => {},
    });
    expect(questions[0]).toContain('¿Aplicar estos cambios?');
  });

  it('applies changes when confirmed', async () => {
    await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const newContent = await fs.readFile(join(tmpDir, 'commands', 'new-project.md'), 'utf8');
    expect(newContent).toContain('New content');
  });

  it('summary includes counts and next step when changes applied', async () => {
    const result = await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const combined = result.output.join('\n');
    expect(combined).toContain('Proximo paso');
    expect(combined).toContain('Reiniciá Claude Code');
  });
});

describe('update — idempotence (6.8, 6.9)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-idempotent-test-'));
    const cmdDir = join(tmpDir, 'commands');
    const stackDir = join(tmpDir, 'from-scratch', 'stacks');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.mkdir(stackDir, { recursive: true });
    await fs.writeFile(join(cmdDir, 'new-project.md'), remoteFiles['commands/new-project.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'java.md'), remoteFiles['stacks/java.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'node.md'), remoteFiles['stacks/node.md'], 'utf8');

    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: '2024-01-01T10:00:00Z',
      last_sync_completed_at: '2024-01-01T10:01:00Z',
      installed_files: ['commands/new-project.md', 'from-scratch/stacks/java.md', 'from-scratch/stacks/node.md'],
      catalog_version: '0.2.0',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('second run without changes produces no change output and does not modify files', async () => {
    const r1 = await runUpdate({ fetcher: makeFetcher(), claudeDir: tmpDir, confirmFn: async () => true, logFn: () => {} });
    const r2 = await runUpdate({ fetcher: makeFetcher(), claudeDir: tmpDir, confirmFn: async () => true, logFn: () => {} });
    expect(r1.output.join('\n')).toContain('Tu catálogo está al día');
    expect(r2.output.join('\n')).toContain('Tu catálogo está al día');

    const writeCalls = vi.mocked(writeState).mock.calls;
    expect(writeCalls.length).toBe(0);
  });
});

describe('update — conflict handling (6.14-6.16)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-conflict-test-'));
    const cmdDir = join(tmpDir, 'commands');
    const stackDir = join(tmpDir, 'from-scratch', 'stacks');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.mkdir(stackDir, { recursive: true });

    await fs.writeFile(join(cmdDir, 'new-project.md'), 'USER custom content', 'utf8');
    await fs.writeFile(join(stackDir, 'java.md'), remoteFiles['stacks/java.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'node.md'), remoteFiles['stacks/node.md'], 'utf8');

    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: ['from-scratch/stacks/java.md', 'from-scratch/stacks/node.md'],
      catalog_version: '0.1.0',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('shows ! symbol for conflicts in diff without --force', async () => {
    const result = await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.output.join('\n')).toContain('!');
  });

  it('does not apply conflict files without --force', async () => {
    await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const content = await fs.readFile(join(tmpDir, 'commands', 'new-project.md'), 'utf8');
    expect(content).toBe('USER custom content');
  });

  it('--force creates backup and applies conflicting change', async () => {
    await runUpdate({
      force: true,
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const cmdDir = join(tmpDir, 'commands');
    const files = await fs.readdir(cmdDir);
    const bakFile = files.find((f) => f.includes('.bak.'));
    expect(bakFile).toBeDefined();

    const bakContent = await fs.readFile(join(cmdDir, bakFile!), 'utf8');
    expect(bakContent).toBe('USER custom content');

    const newContent = await fs.readFile(join(cmdDir, 'new-project.md'), 'utf8');
    expect(newContent).toContain('New content');
  });
});

describe('update — safe delete (6.17-6.19)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-delete-test-'));
    const cmdDir = join(tmpDir, 'commands');
    const stackDir = join(tmpDir, 'from-scratch', 'stacks');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.mkdir(stackDir, { recursive: true });
    await fs.writeFile(join(cmdDir, 'new-project.md'), remoteFiles['commands/new-project.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'java.md'), remoteFiles['stacks/java.md'], 'utf8');
    await fs.writeFile(join(stackDir, 'node.md'), remoteFiles['stacks/node.md'], 'utf8');
    await fs.writeFile(join(cmdDir, 'old-command.md'), 'old installed content', 'utf8');

    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: [
        'commands/new-project.md',
        'from-scratch/stacks/java.md',
        'from-scratch/stacks/node.md',
        'commands/old-command.md',
      ],
      catalog_version: '0.1.0',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('removes installed file that disappeared from catalog', async () => {
    await runUpdate({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    await expect(
      fs.access(join(tmpDir, 'commands', 'old-command.md'))
    ).rejects.toThrow();
  });
});
