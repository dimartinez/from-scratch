import { describe, it, expect } from 'vitest';
import {
  getHelpText,
  getSubcommandHelpText,
  getInvalidSubcommandMessage,
} from '../../src/cli.js';

describe('Help text', () => {
  it('--help includes at least one concrete usage example', () => {
    const help = getHelpText();
    expect(help).toMatch(/from-scratch init/);
    expect(help).toMatch(/from-scratch update/);
  });

  it('--help lists available subcommands', () => {
    const help = getHelpText();
    expect(help).toContain('init');
    expect(help).toContain('update');
  });

  it('"init --help" includes a concrete example of init usage', () => {
    const help = getSubcommandHelpText('init');
    expect(help).toMatch(/from-scratch init/);
  });

  it('"update --help" includes a concrete example of update usage', () => {
    const help = getSubcommandHelpText('update');
    expect(help).toMatch(/from-scratch update/);
  });
});

describe('Invalid subcommand message', () => {
  it('names the received subcommand', () => {
    const msg = getInvalidSubcommandMessage('lalala');
    expect(msg).toContain('lalala');
  });

  it('lists valid subcommands', () => {
    const msg = getInvalidSubcommandMessage('lalala');
    expect(msg).toContain('init');
    expect(msg).toContain('update');
  });

  it('suggests --help', () => {
    const msg = getInvalidSubcommandMessage('lalala');
    expect(msg).toContain('--help');
  });
});
