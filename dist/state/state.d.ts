export interface StateFile {
    last_sync_started_at: string | null;
    last_sync_completed_at: string | null;
    installed_files: string[];
    catalog_version: string;
    binary_version: string;
}
export declare function getStateFilePath(): string;
export declare function readState(): Promise<StateFile | null>;
export declare function writeState(state: StateFile): Promise<void>;
export declare function hasIncompleteSync(state: StateFile): boolean;
export declare function isInstalled(state: StateFile | null): boolean;
//# sourceMappingURL=state.d.ts.map