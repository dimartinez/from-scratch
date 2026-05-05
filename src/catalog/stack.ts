import yaml from 'js-yaml';
import { errorStackInvalid } from '../errors.js';

export interface Stack {
  name: string;
  description: string;
  template_url: string;
}

const REQUIRED_FIELDS = ['name', 'description', 'template_url'] as const;

export function parseStack(content: string, fileName: string): Stack {
  if (!content.startsWith('---')) {
    throw new Error(errorStackInvalid(fileName, 'frontmatter'));
  }

  const end = content.indexOf('---', 3);
  if (end === -1) {
    throw new Error(errorStackInvalid(fileName, 'frontmatter'));
  }

  const frontmatterText = content.slice(3, end).trim();
  let parsed: unknown;
  try {
    parsed = yaml.load(frontmatterText);
  } catch {
    throw new Error(errorStackInvalid(fileName, 'frontmatter (YAML inválido)'));
  }

  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(errorStackInvalid(fileName, 'frontmatter'));
  }

  const obj = parsed as Record<string, unknown>;

  for (const field of REQUIRED_FIELDS) {
    if (typeof obj[field] !== 'string' || !(obj[field] as string).trim()) {
      throw new Error(errorStackInvalid(fileName, field));
    }
  }

  return {
    name: obj.name as string,
    description: obj.description as string,
    template_url: obj.template_url as string,
  };
}
