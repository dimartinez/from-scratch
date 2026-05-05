import { describe, it, expect } from 'vitest';
import { getDestinationPath, getRelativePath, validateFrontmatter } from '../../src/sync/copy.js';
import { homedir } from 'os';
import { join } from 'path';

describe('getDestinationPath', () => {
  const claudeDir = join(homedir(), '.claude');

  it('maps kind:command to ~/.claude/commands/', () => {
    const dest = getDestinationPath('command', 'commands/new-project.md');
    expect(dest).toBe(join(claudeDir, 'commands', 'new-project.md'));
  });

  it('maps kind:stack to ~/.claude/from-scratch/stacks/', () => {
    const dest = getDestinationPath('stack', 'stacks/java.md');
    expect(dest).toBe(join(claudeDir, 'from-scratch', 'stacks', 'java.md'));
  });
});

describe('getRelativePath', () => {
  it('returns relative path for command', () => {
    expect(getRelativePath('command', 'commands/new-project.md')).toBe('commands/new-project.md');
  });

  it('returns relative path for stack', () => {
    expect(getRelativePath('stack', 'stacks/java.md')).toBe('from-scratch/stacks/java.md');
  });
});

describe('validateFrontmatter', () => {
  it('returns true for valid YAML frontmatter', () => {
    const content = '---\ndescription: A test command\n---\nBody here';
    expect(validateFrontmatter(content)).toBe(true);
  });

  it('returns false for invalid YAML syntax in frontmatter', () => {
    const content = '---\n: invalid: yaml: here\n---\nBody';
    expect(validateFrontmatter(content)).toBe(false);
  });

  it('returns false when frontmatter is missing', () => {
    const content = 'Just plain text without frontmatter';
    expect(validateFrontmatter(content)).toBe(false);
  });

  it('returns false when closing --- is absent', () => {
    const content = '---\ndescription: test\nno closing delimiter';
    expect(validateFrontmatter(content)).toBe(false);
  });
});
