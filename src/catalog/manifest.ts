export const KNOWN_KINDS = ['command', 'stack'] as const;
export type KnownKind = (typeof KNOWN_KINDS)[number];

export interface ManifestEntry {
  kind: string;
  source: string;
}

export interface Manifest {
  version: string;
  requires_binary: string;
  entries: ManifestEntry[];
}

export function parseManifest(raw: unknown): Manifest {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error('MANIFEST_PARSE_ERROR');
  }
  const obj = raw as Record<string, unknown>;
  if (typeof obj.version !== 'string') throw new Error('MANIFEST_PARSE_ERROR');
  if (typeof obj.requires_binary !== 'string') throw new Error('MANIFEST_PARSE_ERROR');
  if (!Array.isArray(obj.entries)) throw new Error('MANIFEST_PARSE_ERROR');

  const entries: ManifestEntry[] = obj.entries.map((e: unknown) => {
    if (!e || typeof e !== 'object' || Array.isArray(e)) throw new Error('MANIFEST_PARSE_ERROR');
    const entry = e as Record<string, unknown>;
    if (typeof entry.kind !== 'string') throw new Error('MANIFEST_PARSE_ERROR');
    if (typeof entry.source !== 'string') throw new Error('MANIFEST_PARSE_ERROR');
    return { kind: entry.kind, source: entry.source };
  });

  return { version: obj.version, requires_binary: obj.requires_binary, entries };
}

export function validateKinds(manifest: Manifest): { unknownKind: string } | null {
  for (const entry of manifest.entries) {
    if (!(KNOWN_KINDS as readonly string[]).includes(entry.kind)) {
      return { unknownKind: entry.kind };
    }
  }
  return null;
}
