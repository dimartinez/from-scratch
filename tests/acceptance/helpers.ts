import { promises as fs } from 'fs';
import { join } from 'path';
import os from 'os';

export async function createTempClaudeDir(): Promise<string> {
  const tmpDir = await fs.mkdtemp(join(os.tmpdir(), 'from-scratch-test-'));
  const claudeDir = join(tmpDir, '.claude');
  await fs.mkdir(claudeDir, { recursive: true });
  return claudeDir;
}

export async function cleanupTempDir(claudeDir: string): Promise<void> {
  await fs.rm(join(claudeDir, '..'), { recursive: true, force: true });
}

export const mockCatalogManifest = {
  version: '0.1.0',
  requires_binary: '0.1.0',
  entries: [
    { kind: 'command', source: 'commands/new-project.md' },
    { kind: 'stack', source: 'stacks/java.md' },
  ],
};

export const mockCatalogFiles: Record<string, string> = {
  'commands/new-project.md': '---\ndescription: Crea un nuevo proyecto\n---\nPrompt body here',
  'stacks/java.md': '---\nname: Java (Despegar)\ndescription: Microservicio Java\ntemplate_url: github.com/despegar/java-template\n---',
};
