# OVNIS — Puerto Rico Historical Case Corpus Producer (PRII federation)

`OVNIS` is the historical case-corpus producer for Puerto Rico-centered anomalous-event research in the Puerto Rico Integrated Intelligence (PRII) federation.

Its federation alias is `ovnis-pr`. It should preserve case provenance, chronology, location references, witness/source tiers, document lineage, and review state for downstream analysis in [`thehub-pr`](https://github.com/jotaele44/thehub-pr) and analytical consumers.

## Federation role

| Field | Value |
|---|---|
| Repository | `jotaele44/ovnis-pr` |
| Federation alias | `ovnis-pr` |
| Parent hub | [`thehub-pr`](https://github.com/jotaele44/thehub-pr) |
| Primary function | Historical case corpus and review pipeline |
| Jurisdiction focus | Puerto Rico |

## Setup / Development

Requires **Python 3.10+** (CI's `validate` job tests 3.10–3.12; the `OVNIS CI`
job runs on 3.12). This repo is a flat-layout application — modules run in place,
there is no package install — so setup is just the test/validation dependencies.

```bash
git clone https://github.com/jotaele44/ovnis-pr.git
cd ovnis-pr
python3 -m venv .venv
source .venv/bin/activate

# Install the same dependency set CI uses (matches federation.json `setup`):
python -m pip install pytest jsonschema httpx -r server/backend/requirements.txt \
  "prii-maintenance @ git+https://github.com/jotaele44/thehub-pr.git@3c9e51e3de406f8455605a06fabd4823452d9b63#subdirectory=packages/prii_maintenance" \
  "prii-export-utils @ git+https://github.com/jotaele44/thehub-pr.git@c007a728910128efebcda79bdbe6b9b33212551e#subdirectory=packages/prii_export_utils"
```

> `prii-maintenance` and `prii-export-utils` are shared federation packages pulled
> from the hub repo at pinned commits; installing them needs network access.

Run the checks CI runs:

```bash
python3 scripts/validate_case_ledgers.py            # ledger integrity
python -m pytest -q                                 # unit tests
python3 scripts/federation_export.py --mode test    # canonical export smoke
```

For the double-click desktop app, see [`desktop/README.md`](desktop/README.md).

## Operating doctrine

| Rule | Requirement |
|---|---|
| Provenance first | Every promoted case should retain source, date, location, and review trail where available |
| No silent substitution | Unknown values stay unknown rather than inferred as fact |
| Tiered evidence | Separate technical records, operational records, eyewitness material, and secondary sources |
| Review queue | Ambiguous cases remain staged until enough metadata exists for promotion |
| Federation boundary | OVNIS exports case records; Hub performs cross-producer correlation |

## Suggested repository layout

```text
data/             raw and normalized case material
reports/          generated summaries and review outputs
scripts/          import, validation, deduplication, and reporting tools
docs/             methodology, source policy, FOIA notes, and analyst runbooks
tests/            validation and regression tests
exports/          federation-ready export packages
```

## Minimum promotion fields

| Field | Purpose |
|---|---|
| `case_id` | Stable local identifier |
| `event_date` | Known or bounded date/time |
| `municipio` / `location` | Spatial anchor for Puerto Rico analysis |
| `source_tier` | Evidence tier classification |
| `source_ref` | Document, URL, archive, interview, or file reference |
| `summary` | Controlled, non-dramatized case summary |
| `confidence` | Review-grade confidence score |
| `review_status` | `draft`, `needs_review`, `promoted`, or equivalent |

## Federation export target

OVNIS should emit canonical Hub-compatible records:

```text
sources.jsonl
entities.jsonl
relationships.jsonl
observations.jsonl
manifest.json
```

Do not treat exported cases as conclusions. Treat them as structured historical records available for correlation and review.
