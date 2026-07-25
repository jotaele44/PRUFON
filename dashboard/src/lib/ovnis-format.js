// OVNIS display helpers. Evidence tier T1 (strongest) → T4 (weakest).

const TIER_HEX = { T1: '#38bdf8', T2: '#818cf8', T3: '#a78bfa', T4: '#64748b' }
export const tierHex = (t) => TIER_HEX[t] ?? '#64748b'

const CONFIDENCE_TONE = {
  high: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  'medium-high': 'bg-teal-500/15 text-teal-300 border-teal-500/30',
  medium: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  'low-medium': 'bg-orange-500/15 text-orange-300 border-orange-500/30',
  low: 'bg-red-500/15 text-red-300 border-red-500/30',
}
export const confidenceTone = (c) =>
  CONFIDENCE_TONE[c] ?? 'bg-slate-500/15 text-slate-300 border-slate-500/30'

export function locString(c) {
  const l = c.location || {}
  return l.string || c.location_string || l.municipality || '—'
}
export const hasCoords = (c) => {
  const l = c.location || {}
  return l.lat != null && l.lon != null
}

// Return only browser-safe web links. Some legacy rows store citation text in
// source_url; those values remain visible but must not be rendered as hrefs.
export function sourceUrl(c) {
  const raw = c?.source_url
  if (typeof raw !== 'string' || !raw.trim()) return null

  const value = raw.trim()
  try {
    const parsed = new URL(value)
    return ['http:', 'https:'].includes(parsed.protocol) && parsed.hostname ? value : null
  } catch {
    return null
  }
}

export const hasSourceUrl = (c) => sourceUrl(c) !== null

export function sourceLabel(c) {
  const citation = typeof c?.source_citation === 'string' ? c.source_citation.trim() : ''
  const family = c?.source_family && c.source_family !== 'none' ? c.source_family : ''
  const raw = typeof c?.source_url === 'string' ? c.source_url.trim() : ''
  return citation || family || raw || c?.source || 'Source not supplied'
}

// Federal/military agency involvement (source_family), e.g. "USAF", "AARO", "FAA;
// PR Police/FURA", "none". Ported from the reference HTML mockup's source-pill /
// FOIA-row-highlight styling, adapted to this field since the ledger has no
// NUFORC/CIA-style source taxonomy.
export function sourceFamilyMeta(family) {
  if (!family || family === 'none') return null
  const military = /military|usaf|navy|army|uscg/i.test(family)
  return {
    label: family,
    badge: military
      ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
      : 'bg-sky-500/15 text-sky-300 border-sky-500/30',
    rowTint: military ? 'bg-amber-500/5' : 'bg-sky-500/5',
  }
}
