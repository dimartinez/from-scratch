import { describe, it, expect } from 'vitest';
import { getBinaryVersion } from '../../src/version.js';

describe('getBinaryVersion', () => {
  it('returns a semver-like string from package.json', () => {
    const version = getBinaryVersion();
    expect(typeof version).toBe('string');
    expect(version).toMatch(/^\d+\.\d+\.\d+/);
  });
});
