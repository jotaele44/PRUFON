# PRUFON Changelog

## [v2026-06-06c] Gap-Sweep Batch 11 added — AARO 25-P-0553 Tier-1 MERGE: Aguadilla 2013 resolved as sky lanterns

**Released:** 2026-06-06 afternoon (same day; supersedes b1-b10 snapshot)
**Snapshot:** `releases/v2026-06-06_gap_sweep_b1-b11/`

### Summary

Adds **Batch 11 = 1 MERGE row** capturing AARO's authoritative 2025-03-20 Case Resolution PDF (Document 25-P-0553) for the 2013 Aguadilla CBP IR sensor case. **The first T1 (government primary-source) row in the entire Batches 1–11 candidates table.** Total candidate rows rise from 89 to **90**. AARO source family is now EXHAUSTED at the open-document layer (FY24 Annual Report + Historical Record Report Vol 1 have zero PR mentions).

### Highlights

- **Batch 11** (AARO public reading-room refresh, 2026-06-06 afternoon): AARO has published a dedicated "Puerto Rico Case Resolution" for the famous 26 April 2013 Aguadilla CBP DHC-8 IR sensor encounter. **Attribution: pair of sky lanterns (MODERATE confidence). No anomalous behavior, no transmedium (HIGH confidence).** Motion-parallax + thermal-crossover physics explain the apparent high speed and "water entry." Marine birds + mylar balloons hypotheses explicitly REJECTED. The 7-page PDF (25-P-0553) is the authoritative Tier-1 government source for the case. This is a **MERGE to existing ledger rows PRUAP-0422 + PRUAP-0423**, not a new case.
- **AARO source family EXHAUSTED**: FY24 Consolidated Annual Report on UAP (Nov 2024) and AARO Historical Record Report Volume 1 (March 2024) have **zero** mentions of Puerto Rico, Aguadilla, Vieques, Mayagüez, Caribbean, or Rafael Hernández. The only PR case AARO publicly addresses is the 2013 Aguadilla.
- **Master ledger action item**: operator should update PRUAP-0422 + PRUAP-0423 with the AARO sky-lantern attribution + thermal-crossover physics + AARO PDF as Tier-1 source URL.

### Schema integrity (re-run 2026-06-06 afternoon)

- 37-column schema consistent across all 90 rows
- 0 rows with wrong column count
- 90/90 unique `provisional_case_id` values
- 0 rows missing `source_url`
- 44 real HTTP durable archives (43 Wayback + 1 AARO .mil PDF, itself a durable primary source)
- 42 intentional Batch-6 `n/a — local PDF` entries
- 4 honest blanks (unchanged)

### Carry-forward updated for v2026-06-06c

1. Operator merge decision: `PRUAP-GAP-INX-1973-001` vs `PRUAP-0116` (unchanged).
2. Wayback Save Page Now retry on the 2026-05-12 Impala URL (unchanged).
3. AMS bolide network search for 2013-03-14 23:32 UTC (San Germán Batch-10 case; unchanged).
4. 2013 NUFORC PR cross-reference for Batch-10 cases (unchanged).
5. Locate Manolo Terrón Humacao 2013 photos (unchanged).
6. **NEW: Master ledger update** — merge AARO 25-P-0553 findings into PRUAP-0422 + PRUAP-0423 `conventional_explanation_check`, `source_url`, and `case_status` fields.
7. `ufoevidence.org` Batch 12 attempt from allowlist-enabled session (unchanged).
8. **NEW: YouTube Marquina 1975 documentary `dfG0B5l-AIQ`** — pending Chrome session (web_fetch returns empty, Chrome navigate hung in this session).

### Files in this release

- `PRUFON_GAP_SWEEP_candidates.csv` — 90 rows × 37 columns
- `PRUFON_GAP_SWEEP_DISPATCH_RESULT.md` — Full dispatch result, §0–§24 + Appendix
- `checksums.sha256` — SHA256 verification
- `MANIFEST.md` — Release manifest

---

## [v2026-06-06b] Gap-Sweep Batch 10 added — puertoricoufo.com 2013 snapshot deep-read; OVNI.NET source-family DEAD

**Released:** 2026-06-06 (same day as v2026-06-06; supersedes the b1-b9 snapshot)
**Snapshot:** `releases/v2026-06-06_gap_sweep_b1-b10/`

### Summary

Adds **Batch 10 = 5 NEW PR cases** from the only Wayback-preserved snapshot of `puertoricoufo.com` (2013-08-03 homepage). Total candidate rows rise from 84 to **89**. Definitively documents **OVNI.NET as a PERMANENTLY DEAD source family** (zero Wayback snapshots ever; current site is a server health stub).

### Highlights

- **Batch 10** (`puertoricoufo.com` Wayback snapshot, 2026-06-06): the single 2013-08-03 homepage snapshot is the only durable preserved record of this dedicated PR UFO archive. Chrome `get_page_text` harvested 6 PR cases from homepage excerpts; dedup vs 470-case ledger + 84 Batch 1-9 rows = 5 NEW (1 topical-article non-case). Promoted as PRUAP-GAP-PRU-2013-001 through -005 (San Juan disc, Humacao Terrón, Naranjito red orb, Peñuelas family triangle, San Germán ball-of-fire multi-witness video). Conservative T3 scoring 25–35.
- **OVNI.NET source-family DEAD** (§21): `ovni.net`, `www.ovni.net`, and `lucyguzman.com` all return `archived_snapshots: {}` from the Wayback availability API — i.e., Wayback has never crawled them. The 2005-2009 OVNI.NET case archive is not recoverable from the open web. Cases survive only via Inexplicata aggregation (which is now in the master ledger).
- **Strongest Batch-10 case for follow-up:** PRUAP-GAP-PRU-2013-005 (San Germán 2013-03-14 22:32 AST ball-of-fire video, multi-witness, silent, 4km from Lajas) — AMS bolide network search for 03:32 UTC 2013-03-15 is the recommended conventional-check.

### Schema integrity (re-run 2026-06-06)

- 37-column schema consistent across all 89 rows
- 0 rows with wrong column count
- 89/89 unique `provisional_case_id` values
- 0 rows missing `source_url`
- 43 real Wayback HTTP snapshots (38 prior + 5 new Batch-10 sharing the homepage snapshot URL)
- 42 intentional Batch-6 `n/a — local PDF` entries
- 4 honest blanks (3 from Batches 1–4 prior + 1 Batch-9 Save-Page-Now hang)

### Carry-forward updated for v2026-06-06b

1. Operator merge decision: `PRUAP-GAP-INX-1973-001` vs `PRUAP-0116` (unchanged from v2026-06-06).
2. Wayback Save Page Now retry on the 2026-05-12 Impala URL from an unrestricted browser (unchanged).
3. **NEW: AMS bolide network search for 2013-03-14 23:32 UTC** (San Germán Batch-10 case conventional check).
4. **NEW: 2013 NUFORC PR cross-reference** for the 5 Batch-10 cases — tier-upgrade if any filed with NUFORC.
5. **NEW: Locate Manolo Terrón Humacao 2013 photos** via 2013-era PR media archives.
6. `ufoevidence.org` Batch 11 attempt from a session with `www.ufoevidence.org` in the egress allowlist (unchanged).
7. **Next-batch source candidates (recommended order)**: YouTube Marquina 1975 documentary `dfG0B5l-AIQ` (pre-1980 case content), AARO public reading-room refresh, allowlisted ufoevidence.org retry.

### Files in this release

- `PRUFON_GAP_SWEEP_candidates.csv` — 89 rows × 37 columns
- `PRUFON_GAP_SWEEP_DISPATCH_RESULT.md` — Full dispatch result, §0–§22 + Appendix
- `checksums.sha256` — SHA256 verification
- `MANIFEST.md` — Release manifest

---

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
