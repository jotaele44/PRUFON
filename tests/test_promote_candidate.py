"""Tests for the reviewed promotion helper (scripts/promote_candidate.py).

Runs under pytest, and also under a bare interpreter:

    python3 tests/test_promote_candidate.py

The __main__ fallback exists because pytest and jsonschema are not guaranteed to be
installed in the offline environment.

None of these tests ever touch the real master ledger: every test promotes a
synthetic fixture candidate into a *temp copy* of the master.
"""

import json
import sys
from pathlib import Path

# Make scripts/ importable whether launched by pytest (conftest handles it) or bare.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import promote_candidate as pc  # noqa: E402
from validate_case_ledgers import core_validate  # noqa: E402

REAL_MASTER = ROOT / "data" / "master" / "master_cases.jsonl"

# A reviewed, schema-valid synthetic candidate used only by these tests.
GOOD_CANDIDATE = {
    "record_id": "CAND-TEST-0001",
    "record_type": "candidate",
    "case_id": None,
    "candidate_id": "CAND-TEST-0001",
    "date_local": "2025-03-04",
    "time_local": None,
    "timezone": "America/Puerto_Rico",
    "location_name": "Test Harbor overlook, Salinas",
    "municipality": "Salinas",
    "nearest_feature": None,
    "latitude": 17.95,
    "longitude": -66.29,
    "location_confidence": 0.6,
    "environment": "coastal",
    "object_type": "UAP",
    "description": "Reviewed test candidate row used to exercise the promotion path end to end.",
    "language": "en",
    "translation_status": "original",
    "witness_type": "civilian",
    "witness_count": 2,
    "evidence_tier": "T3",
    "source_url": "https://example.org/test-candidate",
    "source_citation": "test fixture",
    "source_family": "news",
    "source_hash": None,
    "retrieved_at": None,
    "dedupe_status": "new",
    "dedupe_confidence": 0.1,
    "matched_case_id": None,
    "review_action": "pending",
    "contradiction_note": None,
    "gap_note": None,
    "source_reliability": 0.6,
    "chronology_confidence": 0.8,
    "case_confidence": 0.6,
    "created_at": "2026-07-12",
    "updated_at": "2026-07-12",
}


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )


def _fixtures(tmp_path, candidates):
    """Create temp candidate + master ledgers; master is a copy of the real one."""
    cand_path = tmp_path / "data" / "candidates" / "candidate_cases.jsonl"
    master_path = tmp_path / "data" / "master" / "master_cases.jsonl"
    _write_jsonl(cand_path, candidates)
    master_path.parent.mkdir(parents=True, exist_ok=True)
    master_path.write_bytes(REAL_MASTER.read_bytes())
    return cand_path, master_path


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_real_master_present():
    assert REAL_MASTER.exists(), "real master ledger missing"


def test_promote_lands_and_validates(tmp_path):
    cand_path, master_path = _fixtures(tmp_path, [GOOD_CANDIDATE])
    before = len(_read_jsonl(master_path))

    result = pc.promote(
        "CAND-TEST-0001",
        candidates_path=cand_path,
        master_path=master_path,
        reviewed=True,
        now="2026-07-12",
    )

    masters = _read_jsonl(master_path)
    assert len(masters) == before + 1, "exactly one row appended to master"

    promoted = masters[-1]
    assert promoted["record_type"] == "master"
    assert promoted["case_id"] == result["master_case_id"]
    assert promoted["record_id"] == result["master_record_id"]
    # Lineage + provenance preserved.
    assert promoted["candidate_id"] == "CAND-TEST-0001"
    assert promoted["promoted_from"] == "CAND-TEST-0001"
    assert promoted["promoted_at"] == "2026-07-12"
    assert "promoted from candidate CAND-TEST-0001" in promoted["gap_note"]
    # The promoted row must pass core validation as a master record.
    errors, _ = core_validate(promoted, path=master_path, line_no=len(masters))
    assert errors == [], f"promoted master row invalid: {errors}"

    # Candidate consumed from the candidate ledger (cannot be promoted twice).
    remaining = _read_jsonl(cand_path)
    assert all(r["record_id"] != "CAND-TEST-0001" for r in remaining)


def test_refused_without_reviewed_flag(tmp_path):
    cand_path, master_path = _fixtures(tmp_path, [GOOD_CANDIDATE])
    master_before = master_path.read_bytes()
    cand_before = cand_path.read_bytes()

    raised = False
    try:
        pc.promote(
            "CAND-TEST-0001",
            candidates_path=cand_path,
            master_path=master_path,
            reviewed=False,
            now="2026-07-12",
        )
    except pc.PromotionError as exc:
        raised = True
        assert "i-have-reviewed" in str(exc)
    assert raised, "promotion must be refused without --i-have-reviewed"
    # Nothing written on refusal.
    assert master_path.read_bytes() == master_before
    assert cand_path.read_bytes() == cand_before


def test_refused_on_invalid_row(tmp_path):
    bad = dict(GOOD_CANDIDATE)
    bad["record_id"] = "CAND-TEST-BAD"
    bad["candidate_id"] = "CAND-TEST-BAD"
    bad["description"] = "too short"  # < 20 chars -> fails core_validate
    cand_path, master_path = _fixtures(tmp_path, [bad])
    master_before = master_path.read_bytes()
    cand_before = cand_path.read_bytes()

    raised = False
    try:
        pc.promote(
            "CAND-TEST-BAD",
            candidates_path=cand_path,
            master_path=master_path,
            reviewed=True,
            now="2026-07-12",
        )
    except pc.PromotionError as exc:
        raised = True
        assert "failed validation" in str(exc)
    assert raised, "promotion must be refused for an invalid row"
    # Nothing written on refusal.
    assert master_path.read_bytes() == master_before
    assert cand_path.read_bytes() == cand_before


def test_refused_on_placeholder_row(tmp_path):
    placeholder = dict(GOOD_CANDIDATE)
    placeholder["record_id"] = "CAND-0000"
    placeholder["candidate_id"] = "CAND-0000"
    placeholder["source_family"] = "placeholder"
    cand_path, master_path = _fixtures(tmp_path, [placeholder])
    master_before = master_path.read_bytes()

    raised = False
    try:
        pc.promote(
            "CAND-0000",
            candidates_path=cand_path,
            master_path=master_path,
            reviewed=True,
            now="2026-07-12",
        )
    except pc.PromotionError as exc:
        raised = True
        assert "placeholder" in str(exc)
    assert raised, "placeholder rows must never be promoted"
    assert master_path.read_bytes() == master_before


def test_refused_on_unknown_record_id(tmp_path):
    cand_path, master_path = _fixtures(tmp_path, [GOOD_CANDIDATE])
    master_before = master_path.read_bytes()

    raised = False
    try:
        pc.promote(
            "CAND-DOES-NOT-EXIST",
            candidates_path=cand_path,
            master_path=master_path,
            reviewed=True,
            now="2026-07-12",
        )
    except pc.PromotionError as exc:
        raised = True
        assert "no candidate row" in str(exc)
    assert raised, "promotion must be refused for an unknown record_id"
    assert master_path.read_bytes() == master_before


def test_minted_ids_extend_master_sequence(tmp_path):
    cand_path, master_path = _fixtures(tmp_path, [GOOD_CANDIDATE])
    result = pc.promote(
        "CAND-TEST-0001",
        candidates_path=cand_path,
        master_path=master_path,
        reviewed=True,
        now="2026-07-12",
    )
    # Minted ids follow the PRUFON-/PRUAP- families and are unique in master.
    assert result["master_record_id"].startswith("PRUFON-")
    assert result["master_case_id"].startswith("PRUAP-")
    masters = _read_jsonl(master_path)
    rids = [m["record_id"] for m in masters]
    cids = [m["case_id"] for m in masters]
    assert len(rids) == len(set(rids)), "master record_ids must stay unique"
    assert len(cids) == len(set(cids)), "master case_ids must stay unique"


def test_real_master_never_touched_by_tests(tmp_path):
    before = REAL_MASTER.read_bytes()
    cand_path, master_path = _fixtures(tmp_path, [GOOD_CANDIDATE])
    pc.promote(
        "CAND-TEST-0001",
        candidates_path=cand_path,
        master_path=master_path,
        reviewed=True,
        now="2026-07-12",
    )
    assert REAL_MASTER.read_bytes() == before, "the real master ledger must never be modified"


# ---------------------------------------------------------------------------
# Bare-interpreter fallback: run every test_* function without pytest.
# ---------------------------------------------------------------------------
class _TmpPath:
    def __init__(self, base):
        self._base = Path(base)

    def __truediv__(self, other):
        return self._base / other

    def mkdir(self, *a, **k):
        return self._base.mkdir(*a, **k)

    def __fspath__(self):
        return str(self._base)

    def __str__(self):
        return str(self._base)


def _main():
    import inspect
    import tempfile
    import traceback

    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in tests:
        params = inspect.signature(fn).parameters
        with tempfile.TemporaryDirectory() as td:
            kwargs = {}
            if "tmp_path" in params:
                kwargs["tmp_path"] = _TmpPath(td)
            try:
                fn(**kwargs)
                passed += 1
                print(f"PASS {name}")
            except Exception:  # noqa: BLE001
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
