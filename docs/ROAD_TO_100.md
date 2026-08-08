# Road to 100 — normalized federation score

**Audit date:** 2026-08-04  
**Scoring model:** code completeness 20%; main-branch availability 15%; CI enforcement 15%; data materialization 15%; operator verification 15%; GUI completeness 10%; federation readiness 10%.

## Current normalized score: 79.90 / 100

| Dimension | Weight | Score | Weighted |
|---|---:|---:|---:|
| Code completeness | 20 | 90 | 18.00 |
| Main-branch availability | 15 | 88 | 13.20 |
| CI enforcement | 15 | 78 | 11.70 |
| Data materialization | 15 | 75 | 11.25 |
| Operator verification | 15 | 65 | 9.75 |
| GUI completeness | 10 | 75 | 7.50 |
| Federation readiness | 10 | 85 | 8.50 |

The former ~82% figure measured intended-scope implementation. The normalized score discounts incomplete recurring intake, operator evidence and open infrastructure candidates.

## State reconciliation

- The 470-case production corpus, candidate intake, reviewed promotion helper, source registry, federation export and dashboard test harness are on `main`.
- PR #70 is the isolated-clone runtime candidate.
- PR #68 is the workspace-policy candidate and should be reconciled with #70.
- PR #67 is an older GUI-parity candidate that is now behind later frontend work and requires successor or current-main reconciliation.
- Corpus growth, source discovery and coordinate backfill remain operational work rather than completed automation.

## Priority exit sequence

1. Land one isolated workspace/runtime authority.
2. Supersede or reconcile #67 against the current tested dashboard.
3. Execute the first governed recurring candidate-intake cycle against registered sources.
4. Promote only individually reviewed candidates and preserve append-only master lineage.
5. Backfill coordinates with explicit source, method, precision and review state.

## Machine-readable authority

See `docs/unfinished_implementation_ledger.v1.json`. A production corpus is not equivalent to a continuously maintained intake system.
