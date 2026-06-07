# PRUFON Gap-Sweep Release — v2026-06-06 (Batches 1–11)

**Supersedes:** `releases/v2026-06-06_gap_sweep_b1-b10/` (same-day Batch 11 addition).

## Scope
Consolidated snapshot of the **PRUFON Gap-Sweep dispatch chain Batches 1–11**, covering all gap-sweep candidate cases identified beyond the v2026-06-01 master ledger of 470 canonical PRUAP cases. Adds **Batch 11 (AARO public reading-room refresh → 1 MERGE row capturing AARO's Tier-1 25-P-0553 PDF for the 2013 Aguadilla Case Resolution)** to the prior b1-b10 release.

## Files

| File | Size | Description |
|---|---|---|
| `PRUFON_GAP_SWEEP_candidates.csv` | ~142 KB | 90 candidate rows × 37 columns (batch + 36-field PRUFON schema) |
| `PRUFON_GAP_SWEEP_DISPATCH_RESULT.md` | ~122 KB | Full dispatch result document, §0–§24 + Appendix |
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
| 9 | 6 | Inexplicata year-by-year crawl (2026-05-28 v1 + 2026-05-31 v2) |
| 10 | 5 | puertoricoufo.com 2013-08 Wayback homepage snapshot (2026-06-06 morning) |
| **11** | **1** | **AARO 25-P-0553 Tier-1 MERGE: Aguadilla 2013 sky-lantern resolution (2026-06-06 afternoon)** |
| **Total** | **90** | |

## Schema verification (re-run 2026-06-06 afternoon)

- Header columns: 37
- Total data rows: 90
- Rows with wrong column count: 0
- Unique `provisional_case_id` values: 90/90
- Rows missing `source_url`: 0
- `archived_url` populated: 86 of 90
  - 44 real HTTP archives (43 Wayback + 1 AARO .mil PDF, which is itself a durable primary-source archive)
  - 42 intentional `n/a — local PDF/book source` (Batch 6)
  - 4 honest blanks (unchanged)

## Batch 11 case (new this release)

| ID | Date | Locality | Class | Verdict | Conf | Source Tier |
|---|---|---|---|---|---|---|
| PRUAP-GAP-AARO-2013-001 | 2013-04-26 | Aguadilla / Rafael Hernández Airport | CBP DHC-8 IR sensor: 2 sky lanterns (AARO assess) | **MERGE → PRUAP-0422 + PRUAP-0423** | 85 (high — conventional-explanation update) | **T1 (government primary)** |

**This is the first T1 (government-primary-source) row in the entire Batches 1–11 candidates table.** All prior 89 rows are T2-T4 community/aggregator/witness sources.

## What AARO's 25-P-0553 PDF says (summary)

- **NO anomalous behavior** (HIGH confidence)
- **NO transmedium** (HIGH confidence) — never entered water; apparent water entry was thermal crossover within the 2-hour post-sunset IR-degradation window
- **TWO objects** (HIGH confidence) — pixel analysis showed separation at 00:29, 00:40, 00:47
- **Attribution: pair of sky lanterns** (MODERATE confidence) — local hospitality vendors confirmed sky-lantern releases common during celebrations
- **8 mph straight-line drift** consistent with recorded wind 9.8 mph from E/NE
- **656 ft altitude**, drifted SW over land
- **< 1 m object size** via pixel analysis
- Apparent high speed explained by motion parallax + sensor zoom
- Marine birds + mylar balloons hypotheses explicitly REJECTED

## Operator action item (master ledger update)

Use the AARO PDF (`https://www.aaro.mil/Portals/136/PDFs/case_resolution_reports/AARO_Puerto_Rico_UAP_Case_Resolution.pdf`) to update master ledger rows **PRUAP-0422 + PRUAP-0423**:
- `conventional_explanation_check`: add AARO 25-P-0553 finding (sky lanterns, moderate confidence; thermal crossover; motion parallax)
- `source_url`: add the AARO PDF + dvidshub Digital Systems Toolkit reconstruction at `https://www.dvidshub.net/video/955936/2013-puerto-rico-object-reconstruction`
- `case_status`: change from "active unresolved" to "AARO-resolved (sky lanterns, moderate confidence)"

## Source families closed by this release (final)

- Inexplicata: EXHAUSTED.
- puertoricoufo.com: EXHAUSTED at Wayback layer.
- NUFORC, ufo-hunters.com, Black Vault PR, 6 uploaded PDFs, URECAT: EXHAUSTED.
- OVNI.NET source family: PERMANENTLY DEAD (§21).
- **AARO public reading-room: EXHAUSTED at open-document layer** (2013 Aguadilla is the only PR case AARO publicly addresses; FY24 Annual Report + Historical Record Report Vol 1 have zero PR mentions).

## Source families flagged BLOCKED (pending operator allowlist or credentialed access)

- `ufoevidence.org`: site alive (Wayback 2026-05-29) but unreachable from this dispatch's egress allowlist.
- MUFON CMS authenticated: uncredentialed access only.
- El Nuevo Día / Primera Hora digital archives: needs pay/auth path.

## Year coverage — still OPEN after Batches 1–11

1950, 1951, 1953, 1956, 1958, 1961, 1966, 1982, 1984, 1985, 2010, 2019.

(2022 and 2026 remain CLOSED_LOW_YIELD per the original dispatch finding.)

## Carry-forward to next dispatch

1. **Merge decision pending**: `PRUAP-GAP-INX-1973-001` vs `PRUAP-0116`.
2. **Wayback retry**: 1 remaining BLANK archived_url for the 2026-05-12 Impala URL.
3. **AMS bolide network search** for 2013-03-14 23:32 UTC (San Germán Batch-10 case).
4. **2013 NUFORC PR cross-reference** for the 5 Batch-10 cases.
5. **Locate Manolo Terrón Humacao 2013 photos**.
6. **Master ledger update**: merge AARO 25-P-0553 findings into PRUAP-0422 + PRUAP-0423.
7. `ufoevidence.org` Batch 12 attempt from allowlist-enabled session.
8. **YouTube Marquina 1975 documentary `dfG0B5l-AIQ`** — pending Chrome session.

## Verification

```sh
cd releases/v2026-06-06_gap_sweep_b1-b11
sha256sum -c checksums.sha256
```
