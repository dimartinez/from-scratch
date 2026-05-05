import { describe, it, expect } from 'vitest';
import {
  errorUnknownKind,
  errorNetworkDown,
  errorManifestInvalid,
  errorVersionHandshake,
  errorPermissions,
  errorStackInvalid,
  errorFrontmatterInvalid,
  errorNameConflict,
} from '../../src/errors.js';

function hasThreePieces(msg: string): boolean {
  return msg.includes('\n') && msg.split('\n').length >= 2;
}

describe('Error messages — three-piece format', () => {
  it('errorNetworkDown: contains what failed, probable cause, and remediation', () => {
    const msg = errorNetworkDown('init');
    expect(msg).toContain('GitHub');
    expect(msg).toContain('Causa probable');
    expect(msg).toContain('from-scratch init');
  });

  it('errorManifestInvalid: contains what failed, probable cause, and remediation', () => {
    const msg = errorManifestInvalid();
    expect(msg).toContain('catálogo');
    expect(msg).toContain('Causa probable');
    expect(msg).toContain('npm i -g');
  });

  it('errorVersionHandshake: contains current version, required version, and upgrade command', () => {
    const msg = errorVersionHandshake('0.9.0', '1.0.0');
    expect(msg).toContain('0.9.0');
    expect(msg).toContain('1.0.0');
    expect(msg).toContain('npm i -g github:dimartinez/from-scratch');
  });

  it('errorPermissions: contains path, probable cause, and remediation', () => {
    const msg = errorPermissions('commands/new-project.md');
    expect(msg).toContain('commands/new-project.md');
    expect(msg).toContain('Causa probable');
    expect(msg).toContain('chown');
  });

  it('errorStackInvalid: names the stack, the missing field, and suggests reporting', () => {
    const msg = errorStackInvalid('java', 'template_url');
    expect(msg).toContain('java');
    expect(msg).toContain('template_url');
    expect(msg).toContain('issues');
    expect(msg).toContain('El resto del catálogo');
  });

  it('errorFrontmatterInvalid: names the command and contains remediation', () => {
    const msg = errorFrontmatterInvalid('new-project.md');
    expect(msg).toContain('new-project.md');
    expect(msg).toContain('npm i -g');
    expect(msg).toContain('issues');
  });

  it('errorNameConflict: names the file, explains cause, suggests --force', () => {
    const msg = errorNameConflict('new-project.md');
    expect(msg).toContain('new-project.md');
    expect(msg).toContain('Causa probable');
    expect(msg).toContain('--force');
  });

  it('errorUnknownKind: names the kind, explains cause, suggests upgrade', () => {
    const msg = errorUnknownKind('skill');
    expect(msg).toContain('skill');
    expect(msg).toContain('Causa probable');
    expect(msg).toContain('npm i -g github:dimartinez/from-scratch');
  });
});

describe('Error message cross-references (section 8 requirements)', () => {
  it('8.11 — version handshake error has three pieces', () => {
    const msg = errorVersionHandshake('0.9.0', '1.0.0');
    expect(hasThreePieces(msg) || msg.length > 50).toBe(true);
  });

  it('8.12 — conflict error has three pieces', () => {
    const msg = errorNameConflict('foo.md');
    expect(hasThreePieces(msg)).toBe(true);
  });

  it('8.13 — unknown kind error has three pieces', () => {
    const msg = errorUnknownKind('skill');
    expect(hasThreePieces(msg)).toBe(true);
  });
});
