import { describe, it, expect } from 'vitest';
import { checkVersionHandshake } from '../../src/catalog/handshake.js';
import { getBinaryVersion } from '../../src/version.js';

describe('getBinaryVersion', () => {
  it('returns the version from package.json as a string', () => {
    const version = getBinaryVersion();
    expect(typeof version).toBe('string');
    expect(version).toMatch(/^\d+\.\d+\.\d+/);
  });
});

describe('checkVersionHandshake', () => {
  it('passes silently when binary version >= required (binary sufficient)', () => {
    const result = checkVersionHandshake('1.2.0', '1.0.0');
    expect(result.ok).toBe(true);
    expect(result.errorMessage).toBeUndefined();
  });

  it('passes when binary version equals the required version exactly (edge case)', () => {
    const result = checkVersionHandshake('1.0.0', '1.0.0');
    expect(result.ok).toBe(true);
  });

  it('fails when binary version < required (binary insufficient)', () => {
    const result = checkVersionHandshake('0.9.0', '1.0.0');
    expect(result.ok).toBe(false);
    expect(result.errorMessage).toBeDefined();
  });

  it('failure message includes the current version', () => {
    const result = checkVersionHandshake('0.9.0', '1.0.0');
    expect(result.errorMessage).toContain('0.9.0');
  });

  it('failure message includes the required version', () => {
    const result = checkVersionHandshake('0.9.0', '1.0.0');
    expect(result.errorMessage).toContain('1.0.0');
  });

  it('failure message includes the upgrade command', () => {
    const result = checkVersionHandshake('0.9.0', '1.0.0');
    expect(result.errorMessage).toContain('npm i -g github:dimartinez/from-scratch');
  });
});
