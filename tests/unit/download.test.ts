import { describe, it, expect, vi } from 'vitest';
import { downloadManifest, downloadFile, type Fetcher } from '../../src/sync/download.js';

function makeFetcher(responses: Record<string, { ok: boolean; status: number; body: string }>): Fetcher {
  return {
    fetch: async (url: string) => {
      const key = Object.keys(responses).find((k) => url.includes(k));
      if (!key) throw new Error('NETWORK_ERROR');
      const r = responses[key];
      return { ok: r.ok, status: r.status, text: async () => r.body };
    },
  };
}

describe('downloadManifest', () => {
  it('fetches and parses the manifest JSON', async () => {
    const fetcher = makeFetcher({
      'catalog.json': {
        ok: true,
        status: 200,
        body: JSON.stringify({ version: '1.0.0', requires_binary: '0.1.0', entries: [] }),
      },
    });
    const result = await downloadManifest(fetcher);
    expect(result).toMatchObject({ version: '1.0.0' });
  });

  it('throws NETWORK_ERROR when fetch fails', async () => {
    const fetcher: Fetcher = { fetch: async () => { throw new Error('network'); } };
    await expect(downloadManifest(fetcher)).rejects.toThrow('NETWORK_ERROR');
  });

  it('throws NETWORK_ERROR on non-ok response', async () => {
    const fetcher = makeFetcher({
      'catalog.json': { ok: false, status: 503, body: '' },
    });
    await expect(downloadManifest(fetcher)).rejects.toThrow('NETWORK_ERROR');
  });

  it('throws MANIFEST_PARSE_ERROR on invalid JSON', async () => {
    const fetcher = makeFetcher({
      'catalog.json': { ok: true, status: 200, body: 'not json {{{' },
    });
    await expect(downloadManifest(fetcher)).rejects.toThrow('MANIFEST_PARSE_ERROR');
  });
});

describe('downloadFile', () => {
  it('downloads multiple files (happy path)', async () => {
    const fetcher = makeFetcher({
      'new-project.md': { ok: true, status: 200, body: '---\ndescription: test\n---\nHello' },
      'java.md': { ok: true, status: 200, body: '---\nname: Java\n---' },
    });

    const file1 = await downloadFile('commands/new-project.md', fetcher);
    const file2 = await downloadFile('stacks/java.md', fetcher);

    expect(file1).toContain('description: test');
    expect(file2).toContain('name: Java');
  });

  it('throws FILE_NOT_FOUND (with source info) when file returns 404', async () => {
    const fetcher = makeFetcher({
      'missing.md': { ok: false, status: 404, body: '' },
    });
    const error = await downloadFile('commands/missing.md', fetcher).catch((e) => e);
    expect(error.message).toBe('FILE_NOT_FOUND');
    expect(error.source).toBe('commands/missing.md');
  });

  it('does not write anything to disk on 404', async () => {
    const fetcher = makeFetcher({
      'missing.md': { ok: false, status: 404, body: '' },
    });
    await expect(downloadFile('commands/missing.md', fetcher)).rejects.toThrow('FILE_NOT_FOUND');
  });
});
