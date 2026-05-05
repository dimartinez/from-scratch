import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { join } from 'path';
import { promises as fs } from 'fs';
import os from 'os';
import { runInit } from '../../src/commands/init.js';
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

import { readState, writeState, isInstalled } from '../../src/state/state.js';

const catalogManifest = {
  version: '0.1.0',
  requires_binary: '0.1.0',
  entries: [
    { kind: 'command', source: 'commands/new-project.md' },
    { kind: 'stack', source: 'stacks/java.md' },
  ],
};

const catalogFiles: Record<string, string> = {
  'commands/new-project.md': '---\ndescription: Crea un nuevo proyecto\n---\nPrompt body',
  'stacks/java.md': '---\nname: Java\ndescription: Microservicio Java\ntemplate_url: github.com/x/y\n---',
};

function makeFetcher(): Fetcher {
  return {
    fetch: async (url: string) => {
      if (url.includes('catalog.json')) {
        return { ok: true, status: 200, text: async () => JSON.stringify(catalogManifest) };
      }
      for (const [key, body] of Object.entries(catalogFiles)) {
        if (url.includes(key)) {
          return { ok: true, status: 200, text: async () => body };
        }
      }
      return { ok: false, status: 404, text: async () => '' };
    },
  };
}

describe('init — happy path (5.1, 5.2, 5.3, 5.4, 5.22)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    vi.mocked(isInstalled).mockReturnValue(false);
    vi.mocked(readState).mockResolvedValue(null);
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-init-test-'));
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('exits with code 0 when all phases succeed', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.exitCode).toBe(0);
  });

  it('output includes catalog version in the preview', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.output.join('\n')).toContain('0.1.0');
  });

  it('output includes a list of files to create grouped by destination', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const combined = result.output.join('\n');
    expect(combined).toContain('commands/');
    expect(combined).toContain('new-project.md');
  });

  it('asks the confirmation question with the exact required text', async () => {
    const questions: string[] = [];
    await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async (q) => { questions.push(q); return true; },
      logFn: () => {},
    });
    expect(questions[0]).toContain('¿Instalar el catálogo en ~/.claude/?');
  });

  it('writes files to correct destinations', async () => {
    await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const cmdPath = join(tmpDir, 'commands', 'new-project.md');
    const stackPath = join(tmpDir, 'from-scratch', 'stacks', 'java.md');
    const cmd = await fs.readFile(cmdPath, 'utf8');
    const stack = await fs.readFile(stackPath, 'utf8');
    expect(cmd).toContain('description: Crea un nuevo proyecto');
    expect(stack).toContain('name: Java');
  });

  it('updates state file with installed_files', async () => {
    await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(vi.mocked(writeState)).toHaveBeenCalled();
    const lastCall = vi.mocked(writeState).mock.calls.at(-1)![0];
    expect(lastCall.installed_files).toContain('commands/new-project.md');
  });

  it('final output includes "Proximo paso" with next step info', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    const combined = result.output.join('\n');
    expect(combined).toContain('Proximo paso');
    expect(combined).toContain('from-scratch update');
  });
});

describe('init — user rejects confirmation (5.7, 5.8)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    vi.mocked(isInstalled).mockReturnValue(false);
    vi.mocked(readState).mockResolvedValue(null);
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-init-test-'));
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('exits with code 0 and does not touch disk', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => false,
      logFn: () => {},
    });
    expect(result.exitCode).toBe(0);
    const cmdPath = join(tmpDir, 'commands', 'new-project.md');
    await expect(fs.access(cmdPath)).rejects.toThrow();
  });

  it('prints cancellation message', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => false,
      logFn: () => {},
    });
    expect(result.output.join('\n')).toContain('Cancelado');
  });
});

describe('init — existing installation (5.9, 5.10)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(isInstalled).mockReturnValue(true);
    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: '2024-01-01T10:00:00Z',
      last_sync_completed_at: '2024-01-01T10:01:00Z',
      installed_files: ['commands/new-project.md'],
      catalog_version: '0.1.0',
      binary_version: '0.1.0',
    });
  });

  it('does not write files and exits code 0', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: '/tmp/notouch',
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.exitCode).toBe(0);
    expect(vi.mocked(writeState)).not.toHaveBeenCalled();
  });

  it('suggests using "from-scratch update"', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: '/tmp/notouch',
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.output.join('\n')).toContain('from-scratch update');
  });
});

describe('init --force with existing installation and conflict (5.11-5.16)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-init-force-test-'));

    const cmdDir = join(tmpDir, 'commands');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.writeFile(join(cmdDir, 'new-project.md'), 'USER CONTENT — should be backed up', 'utf8');

    vi.mocked(isInstalled).mockReturnValue(true);
    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: [],
      catalog_version: '0.0.0',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('shows preview of what will be overwritten', async () => {
    const result = await runInit({
      force: true,
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => false,
      logFn: () => {},
    });
    const combined = result.output.join('\n');
    expect(combined).toMatch(/sobreescri|new-project/i);
  });

  it('creates a backup of the conflicting file when confirmed', async () => {
    await runInit({
      force: true,
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });

    const cmdDir = join(tmpDir, 'commands');
    const files = await fs.readdir(cmdDir);
    const bakFile = files.find((f) => f.includes('new-project.md.bak'));
    expect(bakFile).toBeDefined();

    const backupContent = await fs.readFile(join(cmdDir, bakFile!), 'utf8');
    expect(backupContent).toBe('USER CONTENT — should be backed up');
  });
});

describe('init — conflict without --force (5.13, 5.14)', () => {
  let tmpDir: string;

  beforeEach(async () => {
    vi.clearAllMocks();
    tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-conflict-test-'));
    const cmdDir = join(tmpDir, 'commands');
    await fs.mkdir(cmdDir, { recursive: true });
    await fs.writeFile(join(cmdDir, 'new-project.md'), 'user content', 'utf8');
    vi.mocked(isInstalled).mockReturnValue(false);
    vi.mocked(readState).mockResolvedValue({
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: [],
      catalog_version: '',
      binary_version: '0.1.0',
    });
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('stops with an error message and does not overwrite', async () => {
    const result = await runInit({
      fetcher: makeFetcher(),
      claudeDir: tmpDir,
      confirmFn: async () => true,
      logFn: () => {},
    });
    expect(result.exitCode).toBe(1);
    expect(result.output.join('\n')).toMatch(/conflicto|Error/i);

    const content = await fs.readFile(join(tmpDir, 'commands', 'new-project.md'), 'utf8');
    expect(content).toBe('user content');
  });
});
