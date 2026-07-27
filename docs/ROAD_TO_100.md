# OVNIS-PR — Road to 100%

Living ledger of what makes this repository a complete, production-grade OVNIS
control plane. Completion is tracked honestly and split into **code** work (fully
closable inside this repo, offline) and **data / network-blocked** work (requires
live web/source discovery and large-scale harvesting that cannot run offline).

## Snapshot

| Dimension | Status |
|---|---|
| Master corpus | 470 real, reviewed cases in `data/master/master_cases.jsonl` |
| Federation export | Working — 758 entities / 563 relationships / 470 observations, checksummed |
| Ledger validation | `scripts/validate_case_ledgers.py` passes (default + aux ledgers, 0 errors) |
| Production status | `PRODUCTION` |
| Candidate-intake pipeline | **Closed by this PR** — `scripts/import_candidates.py` |
| Source registry | **Closed by this PR** — 12 real source families in `data/reference/source_registry.csv` |
| Seeded aux ledgers | **Closed by this PR** — grounded rows in `already_listed` / `updates_new_evidence` / `echoes_noise` |

**Overall completion: ~82%** (was ~68%).
Of the remaining gap, the **code** track is now effectively complete; what is left is
**data / network-blocked** corpus growth.

- **% closed (code):** the previously-open code items (intake pipeline, real source
  registry, seeded aux ledgers) are **done** in this PR. Remaining code items below are
  small hardening/CI wiring, not blockers.
- **% data-blocked:** live source discovery and large-scale candidate harvesting need a
  live network and are out of scope for an offline change.

## What is done

- [x] Doctrine: `docs/OVNIS_GITHUB_CONTROL_PLANE.md`, `docs/CASE_PROMOTION_STANDARD.md`.
- [x] Schema contract: `data/schemas/case.schema.json` (validator degrades gracefully
      when `jsonschema` is absent).
- [x] 470 promoted master cases; validator green.
- [x] Federation export with checksums/manifest.
- [x] Preliminary scoring (`scripts/score_candidates.py`) and dedupe review
      (`scripts/dedupe_candidates.py`).
- [x] **Candidate-intake pipeline** (`scripts/import_candidates.py`): normalizes a local
      feed, reuses scoring + dedupe, and routes rows to the correct aux ledger. Master is
      read-only; staging output by default.
- [x] **Real source registry** (`data/reference/source_registry.csv`): U.S. Navy,
      PR Police/FURA, USAF, NASA, FAA, AARO, CBP, U.S. Army, USCG, and reporting archives
      (NUFORC / NICAP / Inexplicata) — every family is one already present in the corpus.
- [x] **Seeded aux ledgers** at their real paths (`data/already_listed.jsonl`,
      `data/updates_new_evidence.jsonl`, `data/echoes_noise.jsonl`): schema-valid rows
      derived from specific real master cases (`PRUAP-0006`, `PRUAP-0018`, `PRUAP-0428`,
      `PRUAP-0266`), with `matched_case_id` pointing at the real case and provenance in
      `gap_note`. Placeholder `-0000` rows retained.
- [x] Offline test coverage: `tests/test_import_candidates.py` (+ fixture feed),
      runnable under pytest **and** via bare `python3`.
- [x] **Reviewed intake GitHub Action** (`.github/workflows/candidate-intake.yml`):
      `workflow_dispatch` with a `feed` input runs `import_candidates.py --apply`,
      uploads `reports/intake/routing_report.csv` as an artifact, and opens a PR with
      the candidate/aux-ledger changes via `peter-evans/create-pull-request`. The PR is
      path-scoped so `data/master/` can never be included — master is never touched.
- [x] **Reviewed promotion helper** (`scripts/promote_candidate.py`): moves ONE reviewed
      candidate row from `candidate_cases.jsonl` into `master_cases.jsonl`, gated behind an
      explicit `--record-id <id>` **and** `--i-have-reviewed`. It stamps promotion provenance,
      re-runs `core_validate` on the transformed row before appending, and refuses on an
      invalid or placeholder row. Master stays append-only; candidate lineage is preserved.
- [x] **Registry cadence/robots columns**: `source_registry.csv` now carries
      `retrieval_cadence` and `robots_policy` for every real source family (placeholder
      row retained), pre-wiring live-scraping governance.
- [x] Offline test coverage for promotion: `tests/test_promote_candidate.py`, runnable
      under pytest **and** via bare `python3` (promotes a fixture into a temp master copy;
      never touches the real master).

## Remaining — code (small, closable offline)

Leverage-ordered:

1. [x] ~~Wire `import_candidates.py --apply` into a reviewed GitHub Action so intake
   opens a PR into the candidate ledger (never master), per control-plane doctrine.~~
   Done — `.github/workflows/candidate-intake.yml`.
2. [x] ~~Emit the routing report into `reports/` on CI and attach it to intake PRs.~~
   Done — the intake Action uploads `routing_report.csv` as an artifact and includes it
   in the PR.
3. [x] ~~Add a promotion helper that moves a reviewed candidate row from
   `candidate_cases.jsonl` into `master_cases.jsonl` behind explicit review.~~
   Done — `scripts/promote_candidate.py`.
4. [x] ~~Expand `source_registry.csv` columns for retrieval cadence / robots policy once
   live scraping is enabled.~~ Done — `retrieval_cadence` / `robots_policy` columns added.

The offline **code** track is now closed. What remains is data / network-blocked
corpus growth (below).

## Remaining — data / network-blocked

Requires a live network; cannot be produced offline without fabricating facts:

1. [ ] Real web/source discovery against the registered source families.
2. [ ] Large-scale candidate harvesting into `data/candidates/`.
3. [ ] Ongoing corpus growth and periodic re-validation / re-dedupe of new intake.
4. [ ] GIS enrichment (lat/lon backfill) for cases currently missing coordinates.

## Verification (offline)

```
python3 scripts/validate_case_ledgers.py \
  data/candidates/candidate_cases.jsonl data/master/master_cases.jsonl \
  data/already_listed.jsonl data/echoes_noise.jsonl data/updates_new_evidence.jsonl
python3 scripts/import_candidates.py tests/fixtures/candidate_feed.jsonl --out-dir reports/intake
python3 tests/test_import_candidates.py
python3 tests/test_promote_candidate.py
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/candidate-intake.yml'))"
```

---

## Two completion numbers, and why they differ

This ledger says **~82%**. [`MATURITY_AUDIT.md`](MATURITY_AUDIT.md) says **68%**.
Both are correct; they measure different things and should be read together.

| | Measures | Counts a thing "done" when |
|---|---|---|
| **`ROAD_TO_100.md`** (~82%) | code completeness against intended scope | the code exists and works, with data- and network-blocked items called out separately |
| **`MATURITY_AUDIT.md`** (68%) | maturity of the repo as an engineering artifact | a **CI gate** keeps it working |

The spread is largely **enforcement rather than implementation**. Concretely, what this
repo is missing on the audit's axis: no coverage floor; no frontend tests; **no type-checking and no Python linter exist at all**, so both need tooling added rather than just wiring; the JS linter is configured but unrun.

Neither number supersedes the other. Use this ledger to answer "what is left to build";
use the audit to answer "what would a reviewer refuse to merge".
