import yaml from 'js-yaml';
import { errorStackInvalid } from '../errors.js';
const REQUIRED_FIELDS = ['name', 'description', 'template_url'];
export function parseStack(content, fileName) {
    if (!content.startsWith('---')) {
        throw new Error(errorStackInvalid(fileName, 'frontmatter'));
    }
    const end = content.indexOf('---', 3);
    if (end === -1) {
        throw new Error(errorStackInvalid(fileName, 'frontmatter'));
    }
    const frontmatterText = content.slice(3, end).trim();
    let parsed;
    try {
        parsed = yaml.load(frontmatterText);
    }
    catch {
        throw new Error(errorStackInvalid(fileName, 'frontmatter (YAML inválido)'));
    }
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error(errorStackInvalid(fileName, 'frontmatter'));
    }
    const obj = parsed;
    for (const field of REQUIRED_FIELDS) {
        if (typeof obj[field] !== 'string' || !obj[field].trim()) {
            throw new Error(errorStackInvalid(fileName, field));
        }
    }
    return {
        name: obj.name,
        description: obj.description,
        template_url: obj.template_url,
    };
}
//# sourceMappingURL=stack.js.map