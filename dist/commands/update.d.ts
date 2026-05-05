import { type Fetcher } from '../sync/download.js';
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
export declare function runUpdate(options?: UpdateOptions): Promise<UpdateResult>;
//# sourceMappingURL=update.d.ts.map