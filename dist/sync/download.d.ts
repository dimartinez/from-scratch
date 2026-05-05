export interface Fetcher {
    fetch(url: string): Promise<{
        ok: boolean;
        status: number;
        text(): Promise<string>;
    }>;
}
export declare const defaultFetcher: Fetcher;
export declare function downloadManifest(fetcher?: Fetcher): Promise<unknown>;
export declare function downloadFile(source: string, fetcher?: Fetcher): Promise<string>;
//# sourceMappingURL=download.d.ts.map