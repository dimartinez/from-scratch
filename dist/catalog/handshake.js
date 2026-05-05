import semver from 'semver';
import { errorVersionHandshake } from '../errors.js';
export function checkVersionHandshake(binaryVersion, requiredVersion) {
    if (semver.gte(binaryVersion, requiredVersion)) {
        return { ok: true };
    }
    return {
        ok: false,
        errorMessage: errorVersionHandshake(binaryVersion, requiredVersion),
    };
}
//# sourceMappingURL=handshake.js.map