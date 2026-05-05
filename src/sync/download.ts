const GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/dimartinez/from-scratch/main';
const CATALOG_MANIFEST_URL = `${GITHUB_RAW_BASE}/catalog/catalog.json`;

export interface Fetcher {
  fetch(url: string): Promise<{ ok: boolean; status: number; text(): Promise<string> }>;
}

export const defaultFetcher: Fetcher = {
  fetch: (url) => fetch(url),
};

export async function downloadManifest(fetcher: Fetcher = defaultFetcher): Promise<unknown> {
  let response: Awaited<ReturnType<Fetcher['fetch']>>;
  try {
    response = await fetcher.fetch(CATALOG_MANIFEST_URL);
  } catch {
    throw new Error('NETWORK_ERROR');
  }

  if (!response.ok) {
    throw new Error('NETWORK_ERROR');
  }

  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    throw new Error('MANIFEST_PARSE_ERROR');
  }
}

export async function downloadFile(
  source: string,
  fetcher: Fetcher = defaultFetcher
): Promise<string> {
  const url = `${GITHUB_RAW_BASE}/catalog/${source}`;
  let response: Awaited<ReturnType<Fetcher['fetch']>>;
  try {
    response = await fetcher.fetch(url);
  } catch {
    throw new Error('NETWORK_ERROR');
  }

  if (response.status === 404) {
    throw Object.assign(new Error('FILE_NOT_FOUND'), { source, status: 404 });
  }

  if (!response.ok) {
    throw Object.assign(new Error('NETWORK_ERROR'), { source, status: response.status });
  }

  return response.text();
}
