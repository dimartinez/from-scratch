import { describe, it, expect } from 'vitest';
import { formatSummary, formatDiff, containsEmojis, formatError, formatWarning } from '../../src/ui/output.js';

describe('formatSummary', () => {
  it('includes installed, updated, and unchanged counts', () => {
    const out = formatSummary({ installed: 3, updated: 1, unchanged: 12, nextStep: 'reiniciá Claude Code' });
    expect(out).toContain('Instalados: 3');
    expect(out).toContain('Actualizados: 1');
    expect(out).toContain('Sin cambios: 12');
  });

  it('includes a non-empty "Proximo paso"', () => {
    const out = formatSummary({ installed: 0, updated: 0, unchanged: 0, nextStep: 'reiniciá Claude Code' });
    expect(out).toContain('Proximo paso:');
    expect(out).toContain('reiniciá Claude Code');
  });

  it('does not contain emojis', () => {
    const out = formatSummary({ installed: 1, updated: 0, unchanged: 5, nextStep: 'reiniciá Claude Code' });
    expect(containsEmojis(out)).toBe(false);
  });
});

describe('formatDiff', () => {
  it('shows + prefix for new files', () => {
    const out = formatDiff([{ category: '+', relativePath: 'commands/foo.md' }], 0);
    expect(out).toContain('+ commands/foo.md');
  });

  it('shows ~ prefix for modified files', () => {
    const out = formatDiff([{ category: '~', relativePath: 'commands/foo.md' }], 0);
    expect(out).toContain('~ commands/foo.md');
  });

  it('shows - prefix for deleted files', () => {
    const out = formatDiff([{ category: '-', relativePath: 'commands/old.md' }], 0);
    expect(out).toContain('- commands/old.md');
  });

  it('shows unchanged files as aggregate count, not one-by-one', () => {
    const out = formatDiff([], 5);
    expect(out).toContain('5 archivos sin cambios');
    expect(out).not.toMatch(/= commands/);
  });
});

describe('No emojis in output', () => {
  it('containsEmojis returns false for plain text', () => {
    expect(containsEmojis('Instalados: 3\nProximo paso: reiniciá Claude Code')).toBe(false);
  });

  it('containsEmojis returns true for text with emojis', () => {
    expect(containsEmojis('Done! 🎉')).toBe(true);
  });
});

describe('Error and warning formatting', () => {
  it('errors have "Error:" prefix', () => {
    const out = formatError('something went wrong');
    expect(out).toContain('Error:');
  });

  it('warnings have "Aviso:" prefix', () => {
    const out = formatWarning('non-blocking issue');
    expect(out).toContain('Aviso:');
  });
});
