import { promises as fs } from 'fs';
import { join } from 'path';
import { downloadManifest, downloadFile, type Fetcher } from '../sync/download.js';
import { parseManifest, validateKinds } from '../catalog/manifest.js';
import type { KnownKind } from '../catalog/manifest.js';
import { checkVersionHandshake } from '../catalog/handshake.js';
import { getBinaryVersion } from '../version.js';
import {
  getDestinationPath,
  getRelativePath,
  validateFrontmatter,
  writeFileAtomic,
  createBackup,
} from '../sync/copy.js';
import { calculateDiff } from '../sync/diff.js';
import { readState, writeState } from '../state/state.js';
import {
  errorUnknownKind,
  errorFrontmatterInvalid,
  errorNameConflict,
} from '../errors.js';
import { formatSummary, formatDiff, formatError, formatWarning } from '../ui/output.js';

export interface UpdateOptions {
  force?: boolean;
  fetcher?: Fetcher;
  claudeDir?: string;
  confirmFn?: (question: string) => Promise<boolean>;
  logFn?: (msg: string) => void;
}

export interface UpdateResult {
  exitCode: number;
  output: string[];
}

export async function runUpdate(options: UpdateOptions = {}): Promise<UpdateResult> {
  const {
    force = false,
    fetcher,
    claudeDir,
    confirmFn = defaultConfirm,
    logFn = console.log,
  } = options;

  const output: string[] = [];
  const log = (msg: string) => {
    output.push(msg);
    logFn(msg);
  };

  const effectiveClaudeDir = claudeDir ?? join(process.env.HOME ?? '~', '.claude');

  const tmpFiles: string[] = [];
  const sigintHandler = async () => {
    for (const tmp of tmpFiles) {
      try { await fs.unlink(tmp); } catch {}
    }
    log('Cancelado. No se modificó ningún archivo de tu catálogo.');
    process.exit(130);
  };
  process.on('SIGINT', sigintHandler);

  try {
    const state = await readState();
    const installedFiles = state?.installed_files ?? [];

    log('Buscando catálogo en GitHub...');
    let rawManifest: unknown;
    try {
      rawManifest = await downloadManifest(fetcher);
    } catch (e: unknown) {
      const err = e as Error;
      if (err.message === 'NETWORK_ERROR') {
        log(formatError('No pude alcanzar GitHub para descargar el catálogo.'));
        return { exitCode: 1, output };
      }
      throw e;
    }

    let manifest;
    try {
      manifest = parseManifest(rawManifest);
    } catch {
      log(formatError('El catálogo descargado tiene un formato que no entiendo.'));
      return { exitCode: 1, output };
    }

    log(`Catálogo encontrado (v${manifest.version}, ${manifest.entries.length} archivos).`);

    const unknownKind = validateKinds(manifest);
    if (unknownKind) {
      log(formatError(errorUnknownKind(unknownKind.unknownKind)));
      return { exitCode: 1, output };
    }

    const handshake = checkVersionHandshake(getBinaryVersion(), manifest.requires_binary);
    if (!handshake.ok) {
      log(formatError(handshake.errorMessage!));
      return { exitCode: 1, output };
    }

    log('Descargando archivos...');
    const remoteContents = new Map<string, string>();
    for (const entry of manifest.entries) {
      try {
        const content = await downloadFile(entry.source, fetcher);
        remoteContents.set(entry.source, content);
      } catch (e: unknown) {
        const err = e as Error & { source?: string };
        log(formatError(`No pude descargar ${err.source ?? entry.source}.`));
        return { exitCode: 1, output };
      }
    }

    log('Comparando con tu copia local...');

    const overriddenReadFile = async (path: string): Promise<string> => {
      return fs.readFile(path, 'utf8');
    };

    const diffEntries: Array<{ category: string; relativePath: string; entry?: (typeof manifest.entries)[0] }> = [];
    let unchangedCount = 0;

    for (const entry of manifest.entries) {
      const kind = entry.kind as KnownKind;
      const relPath = getRelativePath(kind, entry.source);
      const destPath = join(effectiveClaudeDir, relPath);
      const remoteContent = remoteContents.get(entry.source)!;

      let localContent: string | null = null;
      try {
        localContent = await fs.readFile(destPath, 'utf8');
      } catch {}

      if (localContent === null) {
        diffEntries.push({ category: '+', relativePath: relPath, entry });
      } else if (installedFiles.includes(relPath)) {
        if (localContent === remoteContent) {
          diffEntries.push({ category: '=', relativePath: relPath, entry });
          unchangedCount++;
        } else {
          diffEntries.push({ category: '~', relativePath: relPath, entry });
        }
      } else {
        diffEntries.push({ category: '!', relativePath: relPath, entry });
      }
    }

    for (const installedPath of installedFiles) {
      const stillInManifest = manifest.entries.some(
        (e) => getRelativePath(e.kind as KnownKind, e.source) === installedPath
      );
      if (!stillInManifest) {
        const fullPath = join(effectiveClaudeDir, installedPath);
        let localContent: string | null = null;
        try {
          localContent = await fs.readFile(fullPath, 'utf8');
        } catch {}

        if (localContent !== null) {
          diffEntries.push({ category: '-', relativePath: installedPath });
        }
      }
    }

    const hasChanges = diffEntries.some((e) => e.category !== '=');

    if (!hasChanges) {
      log(`Tu catálogo está al día (v${manifest.version}).`);
      log('Volvé a correr update cuando quieras revisar si hay novedades.');
      return { exitCode: 0, output };
    }

    log('\nCambios pendientes:');
    log(formatDiff(diffEntries, unchangedCount));

    const confirmed = await confirmFn('¿Aplicar estos cambios?');
    if (!confirmed) {
      log('Cancelado. No se modificó ningún archivo de tu catálogo.');
      return { exitCode: 0, output };
    }

    const currentState = state ?? {
      last_sync_started_at: null,
      last_sync_completed_at: null,
      installed_files: [] as string[],
      catalog_version: '',
      binary_version: getBinaryVersion(),
    };

    currentState.last_sync_started_at = new Date().toISOString();
    currentState.last_sync_completed_at = null;
    await writeState(currentState as any);

    let installed = 0;
    let updated = 0;
    const newInstalledFiles = [...installedFiles];

    for (const diffEntry of diffEntries) {
      if (diffEntry.category === '=') continue;
      if (diffEntry.category === '!' && !force) {
        log(formatWarning(`Conflicto en ${diffEntry.relativePath} — omitido (usá --force para sobreescribir).`));
        continue;
      }

      if (diffEntry.category === '-') {
        const fullPath = join(effectiveClaudeDir, diffEntry.relativePath);
        try {
          await fs.unlink(fullPath);
          const idx = newInstalledFiles.indexOf(diffEntry.relativePath);
          if (idx >= 0) newInstalledFiles.splice(idx, 1);
        } catch {}
        continue;
      }

      const entry = diffEntry.entry!;
      const kind = entry.kind as KnownKind;
      const destPath = join(effectiveClaudeDir, diffEntry.relativePath);
      const content = remoteContents.get(entry.source)!;

      if (kind === 'command' && !validateFrontmatter(content)) {
        log(formatError(errorFrontmatterInvalid(entry.source.split('/').pop()!)));
        continue;
      }

      if (diffEntry.category === '!') {
        await createBackup(destPath);
      }

      const tmpPath = `${destPath}.tmp`;
      tmpFiles.push(tmpPath);
      await writeFileAtomic(destPath, content);
      tmpFiles.splice(tmpFiles.indexOf(tmpPath), 1);

      if (diffEntry.category === '+') {
        if (!newInstalledFiles.includes(diffEntry.relativePath)) {
          newInstalledFiles.push(diffEntry.relativePath);
        }
        installed++;
      } else {
        updated++;
      }
    }

    currentState.installed_files = newInstalledFiles;
    currentState.catalog_version = manifest.version;
    currentState.binary_version = getBinaryVersion();
    currentState.last_sync_completed_at = new Date().toISOString();
    await writeState(currentState as any);

    const nextStep = (installed + updated) > 0
      ? 'Reiniciá Claude Code para que tome los cambios.'
      : 'Tu catálogo está al día.';

    log(formatSummary({ installed, updated, unchanged: unchangedCount, nextStep }));

    return { exitCode: 0, output };
  } finally {
    process.removeListener('SIGINT', sigintHandler);
  }
}

async function defaultConfirm(question: string): Promise<boolean> {
  const { confirm } = await import('@clack/prompts');
  const result = await confirm({ message: question, initialValue: true });
  return result === true;
}
