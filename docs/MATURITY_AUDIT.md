# ovnis-pr — Professional Maturity Audit

**Date:** 2026-07-26 · **Method:** static review **plus execution** — every number below came
from running the code in a clean container (Python 3.11.15, Node v22.22.2). Setup followed
this repo's own `hub_callable_commands.setup` (`pip install -r requirements.txt`).

Scope: this repository only. Cross-repo comparisons live in
[`thehub-pr/docs/FEDERATION_MATURITY_AUDIT.md`](https://github.com/jotaele44/thehub-pr/blob/main/docs/FEDERATION_MATURITY_AUDIT.md).

---

## Scorecard

| Dim | Area | Score | Evidence |
|---|---|---|---|
| D1 | Functional completeness | **3** | 7 application routes serving a real case corpus; a single but data-rich dashboard page |
| D2 | Data reality | **4** | 1.1 MB of case data, **zero synthetic-flagged files**; ships a populated 1.5 MB offline snapshot |
| D3 | UI craft | **2** | 4.8k LOC but **1 page**; 32 `aria-*` and 8 `role=` (good markup); empty states exist inline, but there is no `ErrorBoundary` and no way to tell a failed fetch from an empty result |
| D4 | Test coverage | **2** | `72 passed` (6.5s), 8 test files — the smallest suite in the federation, though also the smallest codebase |
| D5 | Engineering hygiene | **1** | JS side is fine (`dashboard/eslint.config.js` + `lint` scripts, clean). Python side has **no `pyproject.toml`, no ruff, no mypy**, and **no lint step of either kind in any of its 7 workflows**. |
| D6 | Doc accuracy | **3** | 10 markdown files; `federation.json` is accurate; no drift found |

**Overall: good data and honest markup, with no Python-side engineering scaffolding.** The
case corpus is real and the UI markup is more accessible than most siblings. What is missing
is the machinery that keeps the Python half healthy as it grows: no package config, no
linter, no type checker — and no CI lint gate for either language.

---

## What is fully developed vs. what is not

**PRODUCTION**

| Module | Evidence |
|---|---|
| Case corpus | `data/` 1.1 MB, zero synthetic-flagged files; `production_status: PRODUCTION`, `ready_for_hub_live_execution: true` |
| `server/backend/main.py` (334 LOC) | 7 application routes — `/health`, `/cases`, `/cases/{id}`, `/candidates`, `/geojson`, `/stats`, `/search` |
| `dashboard/src/lib/snapshot.json` | **1.5 MB populated** with `/candidates`, `/cases`, `/geojson`, `/health`, `/stats`. The only fully working offline export bundle in the federation. |
| CI | `ci.yml`, `validate.yml`, `candidate-intake.yml`, `centinelas-intake.yml`, `maintenance.yml`, `template-drift.yml`, `desktop-build.yml` |

**FUNCTIONAL**

| Module | Gap |
|---|---|
| `dashboard/` (1 page, 4,779 LOC) | builds and lints clean; substantial code, but all in one route |
| `scripts/` (11 files) | proportionate, and **5 of the 9 test modules import them directly** (`test_import_candidates.py`, `test_promote_candidate.py`, `test_validate_case_ledgers.py`, the two federation-export tests) |

**SCAFFOLD**

| Item | Why |
|---|---|
| Error UX | No `ErrorBoundary`, and `getJSON` converts a failed request to `[]`, so a fetch failure renders as "Queue empty" — indistinguishable from a genuinely empty queue |
| Python packaging | no `pyproject.toml` at all — the only repo in the federation without one |

**DEAD** — none found. This repo ships **no auth UI**, which is the honest posture given a
backend with no authentication. Its backend also exposes **zero mutating routes** — read-only
by construction, so the unauthenticated-write issue found in `thehub-pr` and `skywatcher-pr`
cannot arise here.

---

## UI feature matrix

| Page | Backing endpoint | States handled | Verdict |
|---|---|---|---|
| `Dashboard.jsx` (4,779 LOC across the app) | `lib/api.js` → `/cases`, `/candidates`, `/geojson`, `/stats`, `/search` | loading; inline empty state (`CandidateReview.jsx:46` renders "Queue empty"); **no error boundary and no error state** | **Functional but single-route** |

The API client is the shared federation pattern and well built: `API_BASE` indirection,
`AbortSignal.timeout(8000)`, snapshot fallback for `VITE_OFFLINE` builds. Accessibility
markup is genuinely better than most of the federation — 32 `aria-*` and 8 `role=` beats
`thehub-pr`'s 18 and 2 despite having a fraction of the pages.

The gap is structure, not craft: 4,779 LOC of UI behind one route means navigation,
deep-linking, and per-view state all have nowhere to live.

---

## No fixes applied in this PR

The federation-wide fixes in this audit round do not apply here:

- **Dead auth routes** — no auth UI exists to gate.
- **Unauthenticated entity writes** — no mutating routes exist.
- **Documentation drift** — checked, none found.

This PR therefore adds the audit document only, in a new `docs/` directory. Baseline recorded
for future comparison: `72 passed` (6.5s); `npm ci && npm run lint && npm run build` all clean
(1.5 MB JS).

---

## Backlog, ranked

| # | Item | Effort | Why it matters |
|---|---|---|---|
| 1 | Add `pyproject.toml` with ruff + mypy config, and a CI lint step for both Python and the existing ESLint | **S** | The single cheapest maturity gain available in the federation. `ruff check .` currently reports 3 findings under default rules — this repo could be clean today and stay clean. `aguayluz-pr`'s config (`E,F,I,B,UP,SIM,W`) is a good template at a comparable size. Note the dashboard already lints clean; it just is not gated. |
| 2 | Split the dashboard into routed pages | **M** | 4,779 LOC behind one route. `aguayluz-pr` (11 pages) is the closest in-house model. |
| 3 | Add an `ErrorBoundary` and distinguish errors from empty results | **S** | Empty states already exist inline; the gap is that `getJSON` swallows failures into `[]`, so an outage looks like an empty queue. `centinelas-pr/frontend/src/components/ListState.jsx` models the three-way loading/error/empty split. |
| 4 | Grow the test suite | **M** | 8 test files / 72 tests for 3.8k LOC. Ratio is not alarming for the size, but it is the federation's thinnest. |
| 5 | Add a frontend test runner | **M** | Zero frontend tests for 4.8k LOC. |
| 6 | Add an a11y test to lock in the good markup | **S** | The `aria-*` coverage here is a real asset; `thehub-pr`'s `vitest-axe` gate would keep it from eroding. |
