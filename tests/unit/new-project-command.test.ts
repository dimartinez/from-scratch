import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import yaml from 'js-yaml';

const __dirname = dirname(fileURLToPath(import.meta.url));
const commandPath = join(__dirname, '../../catalog/commands/new-project.md');

function getCommandContent() {
  return readFileSync(commandPath, 'utf8');
}

function parseFrontmatter(content: string): Record<string, unknown> {
  if (!content.startsWith('---')) throw new Error('No frontmatter');
  const end = content.indexOf('---', 3);
  if (end === -1) throw new Error('Unclosed frontmatter');
  return yaml.load(content.slice(3, end).trim()) as Record<string, unknown>;
}

function getBody(content: string): string {
  const end = content.indexOf('---', 3);
  return content.slice(end + 3).trim();
}

describe('catalog/commands/new-project.md — frontmatter (task 7.1)', () => {
  it('has parseable YAML frontmatter', () => {
    const content = getCommandContent();
    expect(() => parseFrontmatter(content)).not.toThrow();
  });

  it('has a "description" field in frontmatter', () => {
    const fm = parseFrontmatter(getCommandContent());
    expect(typeof fm.description).toBe('string');
    expect((fm.description as string).trim().length).toBeGreaterThan(0);
  });

  it('description fits in a single line', () => {
    const fm = parseFrontmatter(getCommandContent());
    expect((fm.description as string)).not.toContain('\n');
  });
});

describe('catalog/commands/new-project.md — prompt body (task 7.2)', () => {
  it('declares a role for Claude to adopt', () => {
    const body = getBody(getCommandContent());
    expect(body.toLowerCase()).toMatch(/rol|actúa|eres|desarrollador|senior/i);
  });

  it('declares the final objective (project ready to use)', () => {
    const body = getBody(getCommandContent());
    expect(body.toLowerCase()).toMatch(/proyecto|listo|crear|result/i);
  });

  it('includes explicit constraints (no ambiguity, no inventing steps)', () => {
    const body = getBody(getCommandContent());
    expect(body.toLowerCase()).toMatch(/ambigüedad|pregunta|readme|no invent/i);
  });

  it('does NOT contain imperative numbered steps that script the model rigidly', () => {
    const body = getBody(getCommandContent());
    const numberedStepsPattern = /^(\d+\.\s+.+\n?){5,}/m;
    expect(body).not.toMatch(numberedStepsPattern);
  });
});

describe('catalog/commands/new-project.md — stack reading (task 7.3)', () => {
  it('instructs Claude to read stacks from ~/.claude/from-scratch/stacks/', () => {
    const body = getBody(getCommandContent());
    expect(body).toContain('~/.claude/from-scratch/stacks/');
  });

  it('instructs Claude to present name + description to the user', () => {
    const body = getBody(getCommandContent());
    expect(body.toLowerCase()).toMatch(/nombre|descripción|description|name/i);
  });
});
