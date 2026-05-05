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
import { readState, writeState, isInstalled } from '../state/state.js';
import {
  errorUnknownKind,
  errorFrontmatterInvalid,
  errorNameConflict,
} from '../errors.js';
import { formatSummary, formatError } from '../ui/output.js';

export interface InitOptions {
  force?: boolean;
  fetcher?: Fetcher;
  claudeDir?: string;
  confirmFn?: (question: string) => Promise<boolean>;
  logFn?: (msg: string) => void;
}

export interface InitResult {
  exitCode: number;
  output: string[];
}

export async function runInit(options: InitOptions = {}): Promise<InitResult> {
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

  const getClaudeDir = () => claudeDir ?? join(process.env.HOME ?? '~', '.claude');

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

    if (isInstalled(state) && !force) {
      log('Detecté una instalación previa. Para sincronizar cambios usá: from-scratch update');
      return { exitCode: 0, output };
    }

    log('Buscando catálogo en GitHub...');
    let rawManifest: unknown;
    try {
      rawManifest = await downloadManifest(fetcher);
    } catch (e: unknown) {
      const err = e as Error;
      if (err.message === 'NETWORK_ERROR') {
        log(formatError('No pude alcanzar GitHub para descargar el catálogo.\nCausa probable: sin conexión, o GitHub bloqueado en tu red.'));
        return { exitCode: 1, output };
      }
      if (err.message === 'MANIFEST_PARSE_ERROR') {
        log(formatError('El catálogo descargado tiene un formato que no entiendo.\nCausa probable: el binario está desactualizado.\nProbá: `npm i -g github:dimartinez/from-scratch`'));
        return { exitCode: 1, output };
      }
      throw e;
    }

    let manifest;
    try {
      manifest = parseManifest(rawManifest);
    } catch {
      log(formatError('El catálogo descargado tiene un formato que no entiendo.\nCausa probable: el binario está desactualizado.\nProbá: `npm i -g github:dimartinez/from-scratch`'));
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
    const fileContents = new Map<string, string>();
    for (const entry of manifest.entries) {
      let content: string;
      try {
        content = await downloadFile(entry.source, fetcher);
      } catch (e: unknown) {
        const err = e as Error & { source?: string };
        log(formatError(`No pude descargar ${err.source ?? entry.source} del catálogo.`));
        return { exitCode: 1, output };
      }
      fileContents.set(entry.source, content);
    }

    const byDestination: Record<string, string[]> = {};
    const installPlan: Array<{ entry: (typeof manifest.entries)[0]; dest: string; relPath: string; content: string }> = [];

    for (const entry of manifest.entries) {
      const kind = entry.kind as KnownKind;
      const dest = (claudeDir
        ? join(claudeDir, kind === 'command' ? 'commands' : 'from-scratch/stacks', entry.source.split('/').pop()!)
        : getDestinationPath(kind, entry.source));
      const relPath = getRelativePath(kind, entry.source);
      const content = fileContents.get(entry.source)!;

      const destLabel = kind === 'command' ? '~/.claude/commands/' : '~/.claude/from-scratch/stacks/';
      if (!byDestination[destLabel]) byDestination[destLabel] = [];
      byDestination[destLabel].push(entry.source.split('/').pop()!);

      installPlan.push({ entry, dest, relPath, content });
    }

    log(`\nCatálogo v${manifest.version} — archivos a instalar:`);
    for (const [dest, files] of Object.entries(byDestination)) {
      log(`  ${dest}`);
      for (const f of files) log(`    ${f}`);
    }
    log(`\nTotal: ${installPlan.length} archivos`);

    if (force && isInstalled(state)) {
      log('\nModo --force: los siguientes archivos serán sobreescritos (con backup):');
      for (const item of installPlan) {
        try {
          await fs.access(item.dest);
          log(`  ~ ${item.relPath}`);
        } catch {}
      }
    }

    const confirmed = await confirmFn('¿Instalar el catálogo en ~/.claude/?');
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
    for (const item of installPlan) {
      if (item.entry.kind === 'command' && !validateFrontmatter(item.content)) {
        log(formatError(errorFrontmatterInvalid(item.entry.source.split('/').pop()!)));
        return { exitCode: 1, output };
      }

      let existsLocally = false;
      try {
        await fs.access(item.dest);
        existsLocally = true;
      } catch {}

      if (existsLocally && !currentState.installed_files.includes(item.relPath)) {
        if (!force) {
          log(formatError(errorNameConflict(item.entry.source.split('/').pop()!)));
          return { exitCode: 1, output };
        }
        await createBackup(item.dest);
      }

      const tmpPath = `${item.dest}.tmp`;
      tmpFiles.push(tmpPath);
      await writeFileAtomic(item.dest, item.content);
      tmpFiles.splice(tmpFiles.indexOf(tmpPath), 1);

      if (!currentState.installed_files.includes(item.relPath)) {
        currentState.installed_files.push(item.relPath);
      }
      installed++;
    }

    currentState.catalog_version = manifest.version;
    currentState.binary_version = getBinaryVersion();
    currentState.last_sync_completed_at = new Date().toISOString();
    await writeState(currentState as any);

    log(formatSummary({
      installed,
      updated: 0,
      unchanged: 0,
      nextStep: 'Reiniciá Claude Code y probá /new-project. Cuando quieras traer novedades del catálogo, corré: from-scratch update',
    }));

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
