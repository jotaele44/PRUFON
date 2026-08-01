import { describe, it, expect } from 'vitest';

import { bandHex, bandMeta, fmtDate, statusMeta, tierBadge } from '@/lib/format';

describe('bandMeta', () => {
  it('resolves the seed vocabulary', () => {
    expect(bandMeta('hi').label).toBe('High');
    expect(bandMeta('med').label).toBe('Medium');
    expect(bandMeta('lo').label).toBe('Low');
  });

  it('accepts the long-form aliases as the same bands', () => {
    // Two vocabularies reach this function — the seed writes hi/med/lo, other
    // sources write high/medium/low. They must not resolve to different colours,
    // or the same severity renders two ways depending on provenance.
    expect(bandMeta('high')).toEqual(bandMeta('hi'));
    expect(bandMeta('medium')).toEqual(bandMeta('med'));
    expect(bandMeta('low')).toEqual(bandMeta('lo'));
  });

  it('keeps the three bands visually distinct', () => {
    expect(new Set(['hi', 'med', 'lo'].map(bandHex)).size).toBe(3);
  });

  it('echoes an unknown band as its own label rather than hiding it', () => {
    expect(bandMeta('catastrophic').label).toBe('catastrophic');
    expect(bandMeta('catastrophic').hex).toBe('#64748b');
  });

  it('renders an em dash when there is no band at all', () => {
    expect(bandMeta(undefined).label).toBe('—');
  });
});

describe('tierBadge', () => {
  it('gives each tier its own styling', () => {
    expect(new Set(['T1', 'T2', 'T3', 'T4'].map(tierBadge)).size).toBe(4);
  });

  it('falls back to the weakest tier, not to a neutral grey', () => {
    // An unrecognised tier reads as T4 — the weakest — rather than as something
    // outside the scale. That is the cautious direction for evidence strength.
    expect(tierBadge('T9')).toBe(tierBadge('T4'));
    expect(tierBadge(undefined)).toBe(tierBadge('T4'));
  });
});

describe('statusMeta', () => {
  it.each([
    ['online', 'Online'],
    ['partial', 'Partial'],
    ['offline', 'Offline'],
  ])('labels %s as %s', (status, label) => {
    expect(statusMeta(status).label).toBe(label);
  });

  it('keeps the three known statuses on distinct dots', () => {
    expect(new Set(['online', 'partial', 'offline'].map((s) => statusMeta(s).dot)).size).toBe(3);
  });

  it('echoes an unknown status rather than claiming it is online', () => {
    expect(statusMeta('degraded').label).toBe('degraded');
    expect(statusMeta(undefined).label).toBe('Unknown');
    expect(statusMeta('degraded').dot).not.toBe(statusMeta('online').dot);
  });
});

describe('fmtDate', () => {
  it('renders an em dash for a missing value', () => {
    expect(fmtDate(null)).toBe('—');
    expect(fmtDate('')).toBe('—');
    expect(fmtDate(undefined)).toBe('—');
  });

  it('echoes an unparseable value rather than hiding it', () => {
    // The ledger carries historical dates of varying quality; showing the raw
    // value is more honest than "Invalid Date" or a blank.
    expect(fmtDate('circa 1975')).toBe('circa 1975');
    expect(fmtDate('1975-13-45')).toBe('1975-13-45');
  });

  it('normalises a datetime to UTC at minute precision', () => {
    expect(fmtDate('1975-03-04T22:15:00Z')).toBe('1975-03-04 22:15');
  });

  it('shifts an offset datetime into UTC, including across a day boundary', () => {
    // Puerto Rico is UTC-4, so a late-evening local sighting moves to the next
    // day in UTC. Worth pinning: this is the branch that changes the date.
    expect(fmtDate('1975-03-04T22:15:00-04:00')).toBe('1975-03-05 02:15');
  });

  it('leaves a date-only value untouched — it is sliced, never converted', () => {
    expect(fmtDate('1975-03-04')).toBe('1975-03-04');
  });

  it('does not zero-pad a loosely written date — proving the slice is a slice', () => {
    // A well-formed date survives toISOString() unchanged, so the assertion
    // above passes just as happily against an implementation that normalises the
    // date-only branch too. This one cannot: toISOString() always yields a
    // zero-padded ten-character date, in any timezone, so "1975-3-4" is a result
    // only a genuine string slice can produce.
    expect(fmtDate('1975-3-4')).toBe('1975-3-4');
  });
});
