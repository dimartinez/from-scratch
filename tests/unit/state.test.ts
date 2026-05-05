import { describe, it, expect } from 'vitest';
import { hasIncompleteSync, isInstalled, type StateFile } from '../../src/state/state.js';

function makeState(overrides: Partial<StateFile> = {}): StateFile {
  return {
    last_sync_started_at: null,
    last_sync_completed_at: null,
    installed_files: [],
    catalog_version: '0.1.0',
    binary_version: '0.1.0',
    ...overrides,
  };
}

describe('hasIncompleteSync', () => {
  it('returns false when both timestamps are null', () => {
    expect(hasIncompleteSync(makeState())).toBe(false);
  });

  it('returns true when started but completed is null', () => {
    expect(
      hasIncompleteSync(makeState({ last_sync_started_at: '2024-01-01T10:00:00Z' }))
    ).toBe(true);
  });

  it('returns false when completed is after started', () => {
    expect(
      hasIncompleteSync(
        makeState({
          last_sync_started_at: '2024-01-01T10:00:00Z',
          last_sync_completed_at: '2024-01-01T10:01:00Z',
        })
      )
    ).toBe(false);
  });

  it('returns true when started is after completed (interrupted mid-sync)', () => {
    expect(
      hasIncompleteSync(
        makeState({
          last_sync_started_at: '2024-01-01T11:00:00Z',
          last_sync_completed_at: '2024-01-01T10:00:00Z',
        })
      )
    ).toBe(true);
  });
});

describe('isInstalled', () => {
  it('returns false for null state', () => {
    expect(isInstalled(null)).toBe(false);
  });

  it('returns false when installed_files is empty', () => {
    expect(isInstalled(makeState({ installed_files: [] }))).toBe(false);
  });

  it('returns true when installed_files has entries', () => {
    expect(isInstalled(makeState({ installed_files: ['commands/new-project.md'] }))).toBe(true);
  });
});

describe('state file structure', () => {
  it('state includes all required fields', () => {
    const state = makeState({
      last_sync_started_at: '2024-01-01T10:00:00Z',
      last_sync_completed_at: '2024-01-01T10:01:00Z',
      installed_files: ['commands/new-project.md'],
      catalog_version: '1.0.0',
      binary_version: '0.1.0',
    });
    expect(state).toHaveProperty('last_sync_started_at');
    expect(state).toHaveProperty('last_sync_completed_at');
    expect(state).toHaveProperty('installed_files');
    expect(state).toHaveProperty('catalog_version');
    expect(state).toHaveProperty('binary_version');
  });
});
