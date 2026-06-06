# PRUFON Gap-Sweep Release — v2026-06-06 (Batches 1–9)

## Scope
Consolidated snapshot of the **PRUFON Gap-Sweep dispatch chain Batches 1–9**, covering all gap-sweep candidate cases identified beyond the v2026-06-01 master ledger of 470 canonical PRUAP cases.

This is **NOT** a master-ledger release — it is the curated set of NEW + POSSIBLE-DUPLICATE + MERGE candidates discovered by web-sourced and PDF-sourced sweeps, awaiting operator promotion into the canonical ledger.

## Files

| File | Size | Description |
|---|---|---|
| `PRUFON_GAP_SWEEP_candidates.csv` | 130 KB | 84 candidate rows × 37 columns (batch + 36-field PRUFON schema) |
| `PRUFON_GAP_SWEEP_DISPATCH_RESULT.md` | 102 KB | Full dispatch result document, §0–§19 + Appendix |
| `checksums.sha256` | 200 B | SHA256 checksums for both files |

## Batch composition

| Batch | Rows | Source family |
|---|---:|---|
| 1 | 11 | NUFORC + ufo-hunters.com + Black Vault (Tier-0/1/2 year sweep, 2026-05-20) |
| 2 | 9 | Tier-0 re-sweep + decade-pinning (2026-05-20) |
| 3 | 8 | Flap/cluster resolution + Wayback sweep (2026-05-20) |
| 4 | 4 | 2014/2015 itemization + ledger-defect corrections (2026-05-20) |
| 6 | 42 | 83-case PDF extraction NEW cases (2026-05-23) |
| 7 | 1 | Serial-reporter cluster re-sample (2026-05-23) |
| 8 | 3 | URECAT + gap-map source family sweep (2026-05-23) |
| 9 | 6 | Inexplicata year-by-year crawl, full 2008-2026 + 2005-2007 tail (2026-05-28 v1 + 2026-05-31 Chrome follow-up) |
| **Total** | **84** | |

## Schema verification (re-run 2026-05-31)

- Header columns: 37
- Total data rows: 84
- Rows with wrong column count: 0
- Unique `provisional_case_id` values: 84/84
- Rows missing `source_url`: 0
- `archived_url` populated: 80 of 84
  - 38 real Wayback HTTP snapshots
  - 42 intentional `n/a — local PDF/book source` (Batch 6)
  - 4 honest blanks (3 from Batches 1–4 prior + 1 Batch-9 Save-Page-Now hang)

## Source families closed by this release

- **Inexplicata (`inexplicata.blogspot.com`)**: EXHAUSTED. All 2,282 posts PR-keyword-scanned. The v2026-06-01 master ledger is comprehensive for 2006-Feb 2007 (Inexplicata's most-active PR-content era). Only 5 NEW cases promoted to Batch 9.
- **NUFORC**: Year-by-year reachable archive fully swept.
- **ufo-hunters.com**: NUFORC+MUFON mirror fully swept including 2014/2015 cluster decompositions.
- **The Black Vault**: PR holdings audited; only Mayagüez 2018 promoted.
- **The 6 uploaded PDFs** (jhs2-2, Bühler/Freixedo FSR, Jorge Martín, Phantoms & Monsters, Amaury Rivera, 1952 USAF Blue Book): 83 cases extracted, 42 NEW promoted to Batch 6.
- **URECAT**: PR entity catalogue swept; 3 promoted to Batch 8.

## Source families flagged BLOCKED (pending operator allowlist or credentialed access)

- **`ufoevidence.org`** (Larry Hatch's UFO Evidence Project successor, ~2,500 cases): site confirmed alive (Wayback snapshot 2026-05-29) but unreachable from the dispatch session's egress allowlist. Wait for operator allowlist widening before reopening Batch 10.
- **MUFON CMS direct (authenticated)**: uncredentialed access only; deeper sweep requires MUFON credentials.
- **El Nuevo Día / Primera Hora digital archives**: newspaper-OCR vector partially explored (P1.12). Needs pay/auth path or UPR dLOC handshake.

## Year coverage — still OPEN after Batches 1–9

1950, 1951, 1953, 1956, 1958, 1961, 1966, 1982, 1984, 1985, 2010, 2019.

(2022 and 2026 remain CLOSED_LOW_YIELD per the original dispatch finding.)

## Operator carry-forward

1. **Merge decision pending**: `PRUAP-GAP-INX-1973-001` (Blanca Ruiz Sabana Grande Dec 1973) vs `PRUAP-0116` (Aug 1973 PR-120 Impala). Currently labeled POSSIBLE DUPLICATE.
2. **Wayback retry**: 1 remaining BLANK archived_url for the 2026-05-12 Impala Inexplicata post — Save Page Now hung twice via Chrome. Re-run from an unrestricted browser.
3. **ufoevidence.org Batch 10**: re-attempt from a session whose allowlist includes `www.ufoevidence.org`.

## Source-data provenance

The companion CSV preserves `source_url` and `archived_url` per row, plus tier scoring (T1–T4), conventional-explanation checks, FOIA candidate agency, and the full 36-field PRUFON schema. The master ledger of 470 canonical cases lives in `releases/v2026-06-01/prufon_cases_master.{csv,jsonl,geojson,parquet}` and is unmodified by this release.

## Verification

```sh
cd releases/v2026-06-06_gap_sweep_b1-b9
sha256sum -c checksums.sha256
```
