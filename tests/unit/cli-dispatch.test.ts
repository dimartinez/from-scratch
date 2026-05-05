import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { parseArgs, type ParsedArgs } from '../../src/cli.js';

describe('CLI argument parsing', () => {
  it('recognizes "init" as the init subcommand', () => {
    const result = parseArgs(['init']);
    expect(result.subcommand).toBe('init');
  });

  it('recognizes "update" as the update subcommand', () => {
    const result = parseArgs(['update']);
    expect(result.subcommand).toBe('update');
  });

  it('returns help=true when no arguments are provided', () => {
    const result = parseArgs([]);
    expect(result.showHelp).toBe(true);
    expect(result.subcommand).toBeUndefined();
  });

  it('returns help=true for --help flag', () => {
    const result = parseArgs(['--help']);
    expect(result.showHelp).toBe(true);
  });

  it('returns subcommandHelp for "init --help"', () => {
    const result = parseArgs(['init', '--help']);
    expect(result.subcommand).toBe('init');
    expect(result.showHelp).toBe(true);
  });

  it('returns subcommandHelp for "update --help"', () => {
    const result = parseArgs(['update', '--help']);
    expect(result.subcommand).toBe('update');
    expect(result.showHelp).toBe(true);
  });

  it('returns invalidSubcommand for unknown subcommands', () => {
    const result = parseArgs(['lalala']);
    expect(result.invalidSubcommand).toBe('lalala');
    expect(result.subcommand).toBeUndefined();
  });

  it('recognizes --force flag for init', () => {
    const result = parseArgs(['init', '--force']);
    expect(result.subcommand).toBe('init');
    expect(result.force).toBe(true);
  });

  it('recognizes --force flag for update', () => {
    const result = parseArgs(['update', '--force']);
    expect(result.subcommand).toBe('update');
    expect(result.force).toBe(true);
  });
});
