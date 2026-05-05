import semver from 'semver';
import { errorVersionHandshake } from '../errors.js';

export interface HandshakeResult {
  ok: boolean;
  errorMessage?: string;
}

export function checkVersionHandshake(binaryVersion: string, requiredVersion: string): HandshakeResult {
  if (semver.gte(binaryVersion, requiredVersion)) {
    return { ok: true };
  }
  return {
    ok: false,
    errorMessage: errorVersionHandshake(binaryVersion, requiredVersion),
  };
}
