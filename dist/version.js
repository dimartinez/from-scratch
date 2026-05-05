import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
const require = createRequire(import.meta.url);
const __dirname = dirname(fileURLToPath(import.meta.url));
export function getBinaryVersion() {
    const pkg = require(join(__dirname, '..', 'package.json'));
    return pkg.version;
}
//# sourceMappingURL=version.js.map