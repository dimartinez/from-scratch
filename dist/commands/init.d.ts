import { type Fetcher } from '../sync/download.js';
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
export declare function runInit(options?: InitOptions): Promise<InitResult>;
//# sourceMappingURL=init.d.ts.map