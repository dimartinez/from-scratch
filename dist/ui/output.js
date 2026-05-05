export function formatSummary(summary) {
    const lines = [
        'Resumen',
        `  Instalados: ${summary.installed}`,
        `  Actualizados: ${summary.updated}`,
        `  Sin cambios: ${summary.unchanged}`,
        `Proximo paso: ${summary.nextStep}`,
    ];
    return lines.join('\n');
}
export function formatDiff(entries, unchangedCount) {
    const lines = [];
    for (const entry of entries) {
        if (entry.category !== '=') {
            lines.push(`${entry.category} ${entry.relativePath}`);
        }
    }
    if (unchangedCount > 0) {
        lines.push(`(${unchangedCount} archivos sin cambios)`);
    }
    return lines.join('\n');
}
const EMOJI_PATTERN = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u;
export function containsEmojis(text) {
    return EMOJI_PATTERN.test(text);
}
export function formatError(message) {
    return `\x1b[31mError:\x1b[0m ${message}`;
}
export function formatWarning(message) {
    return `\x1b[33mAviso:\x1b[0m ${message}`;
}
//# sourceMappingURL=output.js.map