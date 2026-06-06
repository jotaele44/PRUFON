# PRUFON Changelog

## [v2026-06-06] Gap-Sweep Batches 1–9 closed — Inexplicata EXHAUSTED

**Released:** 2026-06-06
**Snapshot:** `releases/v2026-06-06_gap_sweep_b1-b9/`

### Summary

Closes the PRUFON Gap-Sweep dispatch chain Batches 1–9. Promotes **84 candidate cases** beyond the v2026-06-01 master ledger of 470 canonical PRUAP rows, all schema-clean and source-attributed.

### Highlights

- **Batch 9** (Inexplicata year-by-year crawl, 2026-05-28 v1 + 2026-05-31 Chrome follow-up): full pagination of all 2,282 posts of Scott Corrales's `inexplicata.blogspot.com` — modern era 2008-2026 in v1 + 2005-2007 tail in v2. 65 PR-keyword hits → ~30 real PR-content posts → 12 distinct cases extracted → **5 promoted as PRUAP-GAP-INX-### rows** (Sep 2006 Northern PR cluster, 2007 LMM Airport Carolina, 2009 Guánica AEP, 2023 Alicea Sábana Grande, 2023 Rivera Peñuelas) + 1 POSSIBLE DUPLICATE (1973 Blanca Ruiz vs PRUAP-0116). **The Inexplicata source family is now considered EXHAUSTED** for PR cases not already in the ledger.
- **§18 `ufoevidence.org` sweep**: site confirmed alive via Wayback (snapshot 2026-05-29) but unreachable from the dispatch session's egress allowlist. No Batch 10; honest BLOCKED finding with precise diagnosis at §18.3.
- **Wayback archival follow-up**: 38 verified Wayback HTTP snapshots across the 84-row CSV; 42 intentional Batch-6 PDF n/a entries; 4 honest blanks (3 from Batches 1–4 prior + 1 from a Save Page Now hang).
- **Source-family disposition**: Inexplicata, NUFORC, ufo-hunters.com, Black Vault PR, and the 6 uploaded PDFs (Bühler/Freixedo FSR, Jorge Martín, Phantoms & Monsters, Amaury Rivera, jhs2-2, 1952 USAF Blue Book) all fully swept. URECAT swept. MUFON CMS authenticated, El Nuevo Día / Primera Hora archives, and ufoevidence.org remain BLOCKED pending credentialed or allowlisted access.

### Operational improvements introduced

- **Wayback availability API path** (`archive.org/wayback/available?url=...` via `web_fetch`) replaces the §11 Chrome-URL-bar harvest method. Faster, unblocked.
- **JSON-recovery parser** for truncated Blogger Atom-JSON feeds: regex on `},{"id":{` to slice at the last complete entry boundary. Works on any Blogger-hosted source.

### Schema integrity (re-run 2026-05-31)

- 37-column schema consistent across all 84 rows
- 0 rows with wrong column count
- 84/84 unique `provisional_case_id` values
- 0 rows missing `source_url`

### Carry-forward items

1. Operator merge decision: `PRUAP-GAP-INX-1973-001` (Blanca Ruiz Dec 1973) vs `PRUAP-0116` (Aug 1973 PR-120 Impala).
2. Wayback Save Page Now retry on the 2026-05-12 Impala Inexplicata URL from an unrestricted browser.
3. `ufoevidence.org` Batch 10 attempt from a session with `www.ufoevidence.org` in the egress allowlist.
4. **Next-batch source candidates** (recommended order): OVNI.NET direct (Lucy Guzmán archive, post-2007), Marquina 1975 documentary YouTube enumeration, AARO public reading-room refresh, El Nuevo Día / Primera Hora digital archives.

### Files in this release

- `PRUFON_GAP_SWEEP_candidates.csv` — 84 rows × 37 columns
- `PRUFON_GAP_SWEEP_DISPATCH_RESULT.md` — Full dispatch result, §0–§19 + Appendix
- `checksums.sha256` — SHA256 verification
- `MANIFEST.md` — Release manifest

### Run dates

- 2026-05-20: Batches 1–4
- 2026-05-23: Batches 6–8
- 2026-05-28: Batch 9 v1 + §18 ufoevidence.org v1
- 2026-05-31: Batch 9 v2 (Chrome follow-up: 2005-2007 tail + Wayback fills + ufoevidence.org Chrome retry)
- 2026-06-06: Consolidation + export

---

## [v2026-06-01] Master ledger snapshot

**Released:** 2026-06-01
**Snapshot:** `releases/v2026-06-01/`

Canonical master ledger of 470 PRUAP cases — `prufon_cases_master.{csv,jsonl,geojson,parquet}` + dedup/echoes/updates feeds + MANIFEST and checksums. This release is the reference state against which all Gap-Sweep Batches 1–9 dedup verdicts are computed.
