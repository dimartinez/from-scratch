export const KNOWN_KINDS = ['command', 'stack'];
export function parseManifest(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
        throw new Error('MANIFEST_PARSE_ERROR');
    }
    const obj = raw;
    if (typeof obj.version !== 'string')
        throw new Error('MANIFEST_PARSE_ERROR');
    if (typeof obj.requires_binary !== 'string')
        throw new Error('MANIFEST_PARSE_ERROR');
    if (!Array.isArray(obj.entries))
        throw new Error('MANIFEST_PARSE_ERROR');
    const entries = obj.entries.map((e) => {
        if (!e || typeof e !== 'object' || Array.isArray(e))
            throw new Error('MANIFEST_PARSE_ERROR');
        const entry = e;
        if (typeof entry.kind !== 'string')
            throw new Error('MANIFEST_PARSE_ERROR');
        if (typeof entry.source !== 'string')
            throw new Error('MANIFEST_PARSE_ERROR');
        return { kind: entry.kind, source: entry.source };
    });
    return { version: obj.version, requires_binary: obj.requires_binary, entries };
}
export function validateKinds(manifest) {
    for (const entry of manifest.entries) {
        if (!KNOWN_KINDS.includes(entry.kind)) {
            return { unknownKind: entry.kind };
        }
    }
    return null;
}
//# sourceMappingURL=manifest.js.map