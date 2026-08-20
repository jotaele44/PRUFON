import { describe, it, expect } from 'vitest';

import {
  confidenceTone,
  hasCoords,
  hasSourceUrl,
  locString,
  sourceFamilyMeta,
  sourceLabel,
  sourceUrl,
  tierHex,
} from '@/lib/ovnis-format';

// sourceUrl is the function worth most of this file. Everything else here is a
// lookup table with a fallback; sourceUrl decides whether a value from the
// ledger becomes a live href in the user's browser, and it is the only place in
// this frontend that makes that decision.

describe('sourceUrl', () => {
  const url = (source_url) => sourceUrl({ source_url });

  it('accepts an ordinary https link', () => {
    expect(url('https://www.faa.gov/foia/123')).toBe('https://www.faa.gov/foia/123');
  });

  it('accepts http as well as https', () => {
    expect(url('http://archive.example.gov/doc')).toBe('http://archive.example.gov/doc');
  });

  it('rejects every scheme outside the http(s) allowlist', () => {
    // This is an allowlist, not a blocklist, and that is the point: a value that
    // reaches an href attribute executes in the user's browser if the scheme
    // lets it. Anything unrecognised must return null and render as plain text.
    expect(url('javascript:alert(1)')).toBeNull();
    expect(url('data:text/html,<script>alert(1)</script>')).toBeNull();
    expect(url('vbscript:msgbox(1)')).toBeNull();
    expect(url('file:///etc/passwd')).toBeNull();
    expect(url('mailto:tips@example.gov')).toBeNull();
    expect(url('ftp://files.example.gov/report.pdf')).toBeNull();
  });

  it('is not fooled by case or leading whitespace in the scheme', () => {
    // `new URL` lowercases the protocol and tolerates surrounding whitespace, so
    // these normalise to javascript: rather than failing to parse.
    expect(url('JavaScript:alert(1)')).toBeNull();
    expect(url('  javascript:alert(1)  ')).toBeNull();
  });

  it('rejects citation text that is not a URL at all', () => {
    // The documented reason this function exists: some legacy rows store a
    // citation in source_url. It stays visible via sourceLabel, but must not
    // become a link.
    expect(url('El Mundo, 4 March 1975, p. 3')).toBeNull();
    expect(url('NUFORC case file (unnumbered)')).toBeNull();
  });

  it('rejects a scheme with nothing after it', () => {
    // Note what actually rejects this: `new URL('http://')` throws, so the catch
    // returns null. The `&& parsed.hostname` clause in sourceUrl does not fire —
    // http: and https: are WHATWG "special" schemes, and the parser requires a
    // non-empty host for those, so every hostless form throws rather than
    // parsing. That clause is unreachable defensive redundancy; no test here
    // claims to cover it, because no input can reach it.
    expect(url('http://')).toBeNull();
    expect(url('https://')).toBeNull();
  });

  it('rejects empty, whitespace-only and non-string values', () => {
    expect(url('')).toBeNull();
    expect(url('   ')).toBeNull();
    expect(url(undefined)).toBeNull();
    expect(url(null)).toBeNull();
    expect(url(42)).toBeNull();
    expect(sourceUrl(undefined)).toBeNull();
    expect(sourceUrl({})).toBeNull();
  });

  it('returns the trimmed value, not the raw one', () => {
    expect(url('  https://example.gov/a  ')).toBe('https://example.gov/a');
  });

  it('hasSourceUrl agrees with sourceUrl on every case', () => {
    for (const raw of ['https://a.gov', 'javascript:alert(1)', '', 'not a url', undefined]) {
      expect(hasSourceUrl({ source_url: raw })).toBe(sourceUrl({ source_url: raw }) !== null);
    }
  });
});

describe('sourceLabel', () => {
  it('prefers the citation when there is one', () => {
    expect(sourceLabel({ source_citation: '  El Mundo, 1975  ', source_family: 'FAA' }))
      .toBe('El Mundo, 1975');
  });

  it('falls back through family, then raw url, then source', () => {
    expect(sourceLabel({ source_family: 'FAA', source_url: 'https://a.gov' })).toBe('FAA');
    expect(sourceLabel({ source_url: 'https://a.gov' })).toBe('https://a.gov');
    expect(sourceLabel({ source: 'field notes' })).toBe('field notes');
  });

  it('treats the "none" family as absent rather than printing it', () => {
    // 'none' is a sentinel in the ledger, not a source name. Printing it would
    // label the row with a word that looks like an answer.
    expect(sourceLabel({ source_family: 'none', source: 'field notes' })).toBe('field notes');
  });

  it('always returns something rather than an empty label', () => {
    expect(sourceLabel({})).toBe('Source not supplied');
    expect(sourceLabel(undefined)).toBe('Source not supplied');
    expect(sourceLabel({ source_citation: '   ' })).toBe('Source not supplied');
  });

  it('still labels a row whose url was rejected as a link', () => {
    // The pairing that matters: sourceUrl returns null, so the value renders as
    // text — and sourceLabel is what supplies that text.
    const c = { source_url: 'javascript:alert(1)' };
    expect(sourceUrl(c)).toBeNull();
    expect(sourceLabel(c)).toBe('javascript:alert(1)');
  });
});

describe('sourceFamilyMeta', () => {
  it('returns null for an absent or sentinel family', () => {
    expect(sourceFamilyMeta(undefined)).toBeNull();
    expect(sourceFamilyMeta('')).toBeNull();
    expect(sourceFamilyMeta('none')).toBeNull();
  });

  it('classifies military branches distinctly from civil agencies', () => {
    expect(sourceFamilyMeta('USAF').badge).not.toBe(sourceFamilyMeta('FAA').badge);
    expect(sourceFamilyMeta('USAF').rowTint).not.toBe(sourceFamilyMeta('FAA').rowTint);
  });

  it.each(['USAF', 'usaf', 'Navy', 'US Army', 'USCG', 'Military police'])(
    'treats %s as military',
    (family) => {
      expect(sourceFamilyMeta(family).badge).toBe(sourceFamilyMeta('USAF').badge);
    },
  );

  it.each(['FAA', 'AARO', 'PR Police/FURA'])('treats %s as civil', (family) => {
    expect(sourceFamilyMeta(family).badge).toBe(sourceFamilyMeta('FAA').badge);
  });

  it('classifies a compound family as military if any part is', () => {
    // The regex is a substring test, so "FAA; USAF" matches. That is the
    // conservative reading — a record involving the Air Force is flagged as such
    // even when a civil agency is listed first.
    expect(sourceFamilyMeta('FAA; USAF').badge).toBe(sourceFamilyMeta('USAF').badge);
  });

  it('echoes the family as its own label', () => {
    expect(sourceFamilyMeta('PR Police/FURA').label).toBe('PR Police/FURA');
  });
});

describe('locString and hasCoords', () => {
  it('prefers the nested string, then the flat one, then the municipality', () => {
    expect(locString({ location: { string: 'Cabo Rojo, PR' }, location_string: 'x' }))
      .toBe('Cabo Rojo, PR');
    expect(locString({ location_string: 'Lajas' })).toBe('Lajas');
    expect(locString({ location: { municipality: 'Ponce' } })).toBe('Ponce');
  });

  it('renders an em dash rather than blank when there is no location', () => {
    expect(locString({})).toBe('—');
    expect(locString({ location: {} })).toBe('—');
  });

  it('treats a zero coordinate as present', () => {
    // `!= null`, not truthiness. Latitude 0 is the equator and longitude 0 is
    // the prime meridian — both real. A `!l.lat` check would mark such a case as
    // having no coordinates and hide it from the map.
    expect(hasCoords({ location: { lat: 0, lon: 0 } })).toBe(true);
  });

  it('requires both coordinates', () => {
    expect(hasCoords({ location: { lat: 18.2 } })).toBe(false);
    expect(hasCoords({ location: { lon: -66.5 } })).toBe(false);
    expect(hasCoords({ location: {} })).toBe(false);
    expect(hasCoords({})).toBe(false);
  });
});

describe('tier and confidence lookups', () => {
  it('gives each evidence tier its own colour', () => {
    const hexes = ['T1', 'T2', 'T3', 'T4'].map(tierHex);

    expect(new Set(hexes).size).toBe(4);
  });

  it('keeps every confidence band distinct', () => {
    const bands = ['high', 'medium-high', 'medium', 'low-medium', 'low'];

    expect(new Set(bands.map(confidenceTone)).size).toBe(bands.length);
  });

  it('does not let high and low confidence look the same', () => {
    expect(confidenceTone('high')).not.toBe(confidenceTone('low'));
  });

  it('falls back to slate for values it does not recognise', () => {
    expect(tierHex('T9')).toBe(tierHex(undefined));
    expect(confidenceTone('unrated')).toContain('slate');
  });
});

describe('inherited keys do not leak through the lookup tables', () => {
  // Every helper here indexes a plain object literal with a server-supplied key.
  // A bare `MAP[key] ?? fallback` resolves these five strings through
  // Object.prototype to something truthy, so the fallback never fires and the
  // caller gets an object where it expected a class string — which clsx then
  // drops entirely, because the prototype has no own enumerable keys, so the
  // element loses its styling rather than degrading to slate.
  //
  // Cosmetic in this repo. Fixed because the identical pattern was a live crash
  // in aguayluz-pr, where the key came from the URL rather than from data.
  const INHERITED = ['__proto__', 'constructor', 'toString', 'valueOf', 'hasOwnProperty'];

  it.each(INHERITED)('tierHex(%s) falls back to the slate hex', (key) => {
    expect(tierHex(key)).toBe('#64748b');
  });

  it.each(INHERITED)('confidenceTone(%s) falls back to the slate badge', (key) => {
    expect(typeof confidenceTone(key)).toBe('string');
    expect(confidenceTone(key)).toBe(confidenceTone('unrated'));
  });

  it.each(INHERITED)('the bare index this replaced does NOT fall back for %s', (key) => {
    // The premise, pinned. If this starts failing, JavaScript changed and the
    // lookup() indirection stops earning its place.
    const MAP = { real: 'value' };
    expect(MAP[key] ?? 'fallback').not.toBe('fallback');
  });
});
