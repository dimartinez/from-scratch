import { describe, it, expect } from 'vitest';
import { parseStack } from '../../src/catalog/stack.js';
import { readFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const validStackContent = `---
name: Java (Despegar)
description: Microservicio Java estándar Despegar
template_url: github.com/despegar/java-template
---
`;

describe('parseStack', () => {
  it('parses a valid stack and returns the three required fields', () => {
    const stack = parseStack(validStackContent, 'java.md');
    expect(stack.name).toBe('Java (Despegar)');
    expect(stack.description).toBe('Microservicio Java estándar Despegar');
    expect(stack.template_url).toBe('github.com/despegar/java-template');
  });

  it('throws when "name" field is missing', () => {
    const content = `---
description: Some description
template_url: github.com/org/repo
---`;
    expect(() => parseStack(content, 'bad.md')).toThrow(/nombre.*name|stack.*formato|campo/i);
  });

  it('throws when "description" field is missing', () => {
    const content = `---
name: My Stack
template_url: github.com/org/repo
---`;
    expect(() => parseStack(content, 'bad.md')).toThrow();
  });

  it('throws when "template_url" field is missing', () => {
    const content = `---
name: My Stack
description: A stack
---`;
    expect(() => parseStack(content, 'bad.md')).toThrow();
  });

  it('throws for malformed YAML frontmatter', () => {
    const content = `---
: invalid yaml {{{
---`;
    expect(() => parseStack(content, 'bad.md')).toThrow();
  });

  it('throws for content without frontmatter', () => {
    expect(() => parseStack('just plain text', 'bad.md')).toThrow();
  });
});

describe('catalog/stacks/java.md', () => {
  it('parses correctly and returns expected fields', () => {
    const javaStackPath = join(__dirname, '../../catalog/stacks/java.md');
    const content = readFileSync(javaStackPath, 'utf8');
    const stack = parseStack(content, 'java.md');
    expect(stack.name).toBe('Java (Despegar)');
    expect(stack.description).toBe('Microservicio Java estándar Despegar');
    expect(stack.template_url).toBe('github.com/despegar/java-template');
  });
});
