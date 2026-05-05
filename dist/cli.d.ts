export type Subcommand = 'init' | 'update';
export interface ParsedArgs {
    subcommand?: Subcommand;
    showHelp?: boolean;
    force?: boolean;
    invalidSubcommand?: string;
}
export declare function parseArgs(args: string[]): ParsedArgs;
export declare function getHelpText(): string;
export declare function getSubcommandHelpText(subcommand: Subcommand): string;
export declare function getInvalidSubcommandMessage(received: string): string;
//# sourceMappingURL=cli.d.ts.map