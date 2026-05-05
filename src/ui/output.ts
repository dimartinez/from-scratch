export interface SummaryBlock {
  installed: number;
  updated: number;
  unchanged: number;
  nextStep: string;
}

export function formatSummary(summary: SummaryBlock): string {
  const lines = [
    'Resumen',
    `  Instalados: ${summary.installed}`,
    `  Actualizados: ${summary.updated}`,
    `  Sin cambios: ${summary.unchanged}`,
    `Proximo paso: ${summary.nextStep}`,
  ];
  return lines.join('\n');
}

export function formatDiff(
  entries: Array<{ category: string; relativePath: string }>,
  unchangedCount: number
): string {
  const lines: string[] = [];
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

export function containsEmojis(text: string): boolean {
  return EMOJI_PATTERN.test(text);
}

export function formatError(message: string): string {
  return `\x1b[31mError:\x1b[0m ${message}`;
}

export function formatWarning(message: string): string {
  return `\x1b[33mAviso:\x1b[0m ${message}`;
}
