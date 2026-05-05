#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'fs';
import { chmodSync } from 'fs';

const entrypoint = './dist/index.js';
const content = readFileSync(entrypoint, 'utf8');

if (!content.startsWith('#!/usr/bin/env node')) {
  writeFileSync(entrypoint, `#!/usr/bin/env node\n${content}`);
}

chmodSync(entrypoint, 0o755);
