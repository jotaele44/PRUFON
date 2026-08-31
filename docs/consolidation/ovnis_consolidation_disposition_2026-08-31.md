# OVNIS Consolidation Disposition - 2026-08-31

## Scope

FACT: Repository path inspected and mutated: `/Users/jotaele/fed-repos/ovnis-pr-actual`.

FACT: Remote: `https://github.com/jotaele44/ovnis-pr.git`.

FACT: Main pushed through `0bbbdff06d1edc044a1acdf4c989717aa5a0843a`.

FACT: Original unresolved `git stash pop` conflict on `README.md` was resolved before this ledger; `.venv` was removed from the Git index and remains ignored/local.

## Merged Into Main

| Vector | Source branch / PR | Main evidence | Disposition |
|---|---|---|---|
| Unified skillpack binding | `origin/chore/unified-skillpacks-v1.0.0-400994dc`, PR #72 | merge `313d4e5`, fix `9bbc3de` | PASS |
| Offline operator scaffold | `origin/gpt/offline-operator-model-v1`, PR #19 | merge `5c94cd6` | PASS |
| GIS case-map controls | `origin/claude/gis-capability-repos-jfvm9u`, PR #97 | merge `07938ee` | PASS |
| Setup Python action pin | `origin/dependabot/github_actions/actions/setup-python-7.0.0`, PR #105 | merge `eb15ee1` | PASS |
| Setup Node action pin | `origin/dependabot/github_actions/actions/setup-node-7.0.0`, PR #106 | merge `bdce0c1` | PASS |
| CodeQL action pin group | `origin/dependabot/github_actions/actions-minor-patch-f1ba23a83b`, PR #104 | merge `038e56d` | PASS |
| Python minor/patch constraints branch | `origin/dependabot/pip/python-minor-patch-af43fc0563`, PR #98 | merge `ef5aee3`, corrective commit `0bbbdff` | SUPERSEDED_BY_LOCKFILE |

## Dashboard Dependency Disposition

COMPUTED: The five remaining npm Dependabot PR branches were stale relative to pushed `main` and edited the same manifest/lockfile pair from an old base. A fresh npm resolution was used for the compatible subset.

FACT: `cc56d48` updated:

| Package | Final requested range in `dashboard/package.json` | Disposition |
|---|---:|---|
| `@vitejs/plugin-react` | `^6.1.1` | PASS, supersedes PR #99 target |
| `eslint-plugin-react-hooks` | `^7.1.1` | PASS, supersedes PR #101 target |
| `globals` | `^17.11.0` | PASS, supersedes PR #102 target |
| `eslint` | `^9.19.0` | BLOCKED for PR #100 target `^10.9.1` |
| `@eslint/js` | `^9.19.0` | BLOCKED for PR #103 target `^10.0.1` |

FACT: `npm install --save-dev @vitejs/plugin-react@^6.1.1 eslint-plugin-react-hooks@^7.1.1 globals@^17.11.0` completed with zero reported vulnerabilities.

FACT: `npm install --save-dev eslint@^10.9.1 @eslint/js@^10.0.1 ...` failed with `ERESOLVE`.

FACT: Registry evidence at run time: `eslint-plugin-react@7.37.5` declares peer dependency `eslint: ^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9.7`, so ESLint 10 is outside the supported peer range.

INFERENCE: PR #100 and PR #103 should remain blocked or be replaced only after `eslint-plugin-react` publishes ESLint 10 support, or after the project intentionally removes/replaces that plugin.

## PRUFON Raw Data Disposition

FACT: Tracked manifests:

| Manifest | Evidence |
|---|---|
| `data/legacy_prufon/manifest.json` | 3,131 files, 33,981,935,989 logical bytes |
| `data/legacy_prufon/file_manifest.jsonl` | one row per inventoried file |

COMPUTED: Raw copy status from manifest:

| Copy status | Files | Logical bytes |
|---|---:|---:|
| `EXISTS_SAME_SIZE` | 2,642 | 1,644,464,648 |
| `COPY_SKIPPED_SPARSE_OR_PLACEHOLDER` | 489 | 32,337,471,341 |

OPEN: Full raw-byte consolidation remains incomplete because many source files are sparse/cloud placeholders and the local filesystem did not have enough safe free space for a full 33.98 GB materialized copy.

OPEN: Hashing remains `HASH_DEFERRED`; byte identity has not been certified.

## Verification

PASS: `.venv/bin/python -m py_compile scripts/*.py tools/validate_unified_skillpacks.py`

PASS: `.venv/bin/python scripts/validate_case_ledgers.py` -> 471 rows, 2 ledgers, 0 errors, 0 warnings.

PASS: `.venv/bin/python tools/validate_unified_skillpacks.py --root .`

PASS: `.venv/bin/python -m pytest -q` -> 113 passed, 1 warning.

PASS: `npm test -- --run` from `dashboard/` -> 109 passed.

PASS: `npm run build` from `dashboard/`.

PASS: `npm run lint` from `dashboard/`.

PASS: `uv pip compile requirements.txt --universal --python-version 3.12 -o requirements.lock` left `requirements.lock` stable.

## Residue

OPEN: npm PR #99, #101, and #102 remain open on GitHub at the time of this ledger even though their target manifest values are present in `main` via `cc56d48`.

BLOCKED: npm PR #100 and #103 remain open and are not safe to apply while `eslint-plugin-react@7.37.5` excludes ESLint 10 from its peer range.

OPEN: Additional stale branches outside the live PR list still require separate disposition, including older backup/rescue/safety/audit refs.

OPEN: The separate `/Users/jotaele/Developer/PRUFON/chatgpt-pr` repository is inventoried as a source corpus but is not merged as OVNIS code because its remote identity is `jotaele44/chatgpt-pr.git`, not `jotaele44/ovnis-pr.git`.
