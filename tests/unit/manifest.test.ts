import { describe, it, expect } from 'vitest';
import { parseManifest, validateKinds, KNOWN_KINDS } from '../../src/catalog/manifest.js';

describe('Manifest schema', () => {
  const validManifest = {
    version: '1.0.0',
    requires_binary: '0.1.0',
    entries: [
      { kind: 'command', source: 'commands/new-project.md' },
      { kind: 'stack', source: 'stacks/java.md' },
    ],
  };

  it('parses a valid manifest', () => {
    const manifest = parseManifest(validManifest);
    expect(manifest.version).toBe('1.0.0');
    expect(manifest.entries).toHaveLength(2);
  });

  it('every entry has a kind field (string)', () => {
    const manifest = parseManifest(validManifest);
    for (const entry of manifest.entries) {
      expect(typeof entry.kind).toBe('string');
    }
  });

  it('recognized kinds in v1 are exactly "command" and "stack"', () => {
    expect(KNOWN_KINDS).toContain('command');
    expect(KNOWN_KINDS).toContain('stack');
    expect(KNOWN_KINDS).toHaveLength(2);
  });

  it('rejects manifest missing required fields', () => {
    expect(() => parseManifest({ entries: [] })).toThrow('MANIFEST_PARSE_ERROR');
    expect(() => parseManifest(null)).toThrow('MANIFEST_PARSE_ERROR');
    expect(() => parseManifest('not an object')).toThrow('MANIFEST_PARSE_ERROR');
  });

  it('rejects entries missing kind or source', () => {
    expect(() =>
      parseManifest({ ...validManifest, entries: [{ source: 'foo.md' }] })
    ).toThrow('MANIFEST_PARSE_ERROR');
  });

  describe('validateKinds', () => {
    it('returns null when all kinds are known', () => {
      const manifest = parseManifest(validManifest);
      expect(validateKinds(manifest)).toBeNull();
    });

    it('returns the unknown kind when an entry has an unrecognized kind', () => {
      const manifest = parseManifest({
        ...validManifest,
        entries: [...validManifest.entries, { kind: 'skill', source: 'skills/foo.md' }],
      });
      const result = validateKinds(manifest);
      expect(result).not.toBeNull();
      expect(result!.unknownKind).toBe('skill');
    });
  });
});
