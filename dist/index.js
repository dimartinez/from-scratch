#!/usr/bin/env node
import { parseArgs, getHelpText, getSubcommandHelpText, getInvalidSubcommandMessage } from './cli.js';
import { readState, hasIncompleteSync } from './state/state.js';
import { runInit } from './commands/init.js';
import { runUpdate } from './commands/update.js';
async function main() {
    const args = process.argv.slice(2);
    const parsed = parseArgs(args);
    const state = await readState();
    if (state && hasIncompleteSync(state)) {
        console.log('Detecté una sincronización anterior interrumpida. Voy a reanudarla.');
        const result = await runUpdate();
        process.exit(result.exitCode);
        return;
    }
    if (parsed.invalidSubcommand) {
        console.error(getInvalidSubcommandMessage(parsed.invalidSubcommand));
        process.exit(1);
        return;
    }
    if (!parsed.subcommand || parsed.showHelp) {
        if (!parsed.subcommand) {
            console.log(getHelpText());
            process.exit(0);
            return;
        }
        console.log(getSubcommandHelpText(parsed.subcommand));
        process.exit(0);
        return;
    }
    if (parsed.subcommand === 'init') {
        const result = await runInit({ force: parsed.force });
        process.exit(result.exitCode);
        return;
    }
    if (parsed.subcommand === 'update') {
        const result = await runUpdate({ force: parsed.force });
        process.exit(result.exitCode);
        return;
    }
}
main().catch((err) => {
    console.error('Error inesperado:', err);
    process.exit(1);
});
//# sourceMappingURL=index.js.map