const VALID_SUBCOMMANDS = ['init', 'update'];
export function parseArgs(args) {
    if (args.length === 0) {
        return { showHelp: true };
    }
    if (args[0] === '--help') {
        return { showHelp: true };
    }
    const subcommand = args[0];
    const rest = args.slice(1);
    const showHelp = rest.includes('--help');
    const force = rest.includes('--force');
    if (!VALID_SUBCOMMANDS.includes(subcommand)) {
        return { invalidSubcommand: subcommand };
    }
    return {
        subcommand: subcommand,
        showHelp: showHelp || undefined,
        force: force || undefined,
    };
}
export function getHelpText() {
    return `from-scratch - Instala y actualiza comandos de Claude Code

Uso:
  from-scratch init      Primera instalación del catálogo en ~/.claude/
  from-scratch update    Re-sincroniza el catálogo con la versión más reciente

Ejemplos:
  from-scratch init
  from-scratch update
  from-scratch init --force

Opciones:
  --help     Muestra esta ayuda
  --force    Sobrescribe archivos existentes (con backup automático)

Para ayuda de un subcomando:
  from-scratch <subcomando> --help`;
}
export function getSubcommandHelpText(subcommand) {
    if (subcommand === 'init') {
        return `from-scratch init - Primera instalación del catálogo en ~/.claude/

Uso:
  from-scratch init [--force]

Ejemplos:
  from-scratch init
  from-scratch init --force

Opciones:
  --force    Sobrescribe archivos existentes (con backup automático)
  --help     Muestra esta ayuda

Qué hace:
  Descarga el catálogo desde GitHub y copia los archivos a ~/.claude/.
  Luego podés usar /new-project en Claude Code.`;
    }
    return `from-scratch update - Re-sincroniza el catálogo con la versión más reciente

Uso:
  from-scratch update [--force]

Ejemplos:
  from-scratch update
  from-scratch update --force

Opciones:
  --force    Aplica cambios incluso ante conflictos (con backup automático)
  --help     Muestra esta ayuda

Qué hace:
  Compara el catálogo remoto con tu copia local y aplica los cambios.`;
}
export function getInvalidSubcommandMessage(received) {
    return `No conozco el subcomando "${received}". Subcomandos disponibles: ${VALID_SUBCOMMANDS.join(', ')}. Probá: from-scratch --help`;
}
//# sourceMappingURL=cli.js.map