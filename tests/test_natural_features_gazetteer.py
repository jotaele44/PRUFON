"""Gate: the shared PR natural-features gazetteer (terrain+coastal slice) is valid.

The canonical gazetteer is owned by spiderweb-pr; ovnis consumes the
terrain+coastal slice as reference geography (data/reference/pr_natural_features.json)
for locating anomalous-event cases against the same canonical place vocabulary the
federation joins on. See spiderweb-pr docs/NATURAL_FEATURES_CONTRACT.md.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
DATASET = REPO / "data" / "reference" / "pr_natural_features.json"
SCHEMA = REPO / "schemas" / "pr_natural_feature.schema.json"


def _dataset():
    return json.loads(DATASET.read_text(encoding="utf-8"))


def test_dataset_matches_schema():
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    data = _dataset()
    assert data["_count"] == len(data["features"]) == 991
    errors = []
    for rec in data["features"]:
        errors.extend(e.message for e in list(validator.iter_errors(rec))[:1])
    assert not errors, errors[:5]


def test_slice_is_terrain_and_coastal_only():
    assert {r["group"] for r in _dataset()["features"]} == {"terrain", "coastal"}


def test_canonical_ids_unique_and_in_pr_bounds():
    recs = _dataset()["features"]
    ids = [r["canonical_id"] for r in recs]
    assert len(ids) == len(set(ids))
    for r in recs:
        assert 17.7 <= r["lat"] <= 18.7 and -68.1 <= r["lon"] <= -65.1
