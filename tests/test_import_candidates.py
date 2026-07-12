"""Tests for the OVNIS candidate-intake pipeline (scripts/import_candidates.py).

Runs under pytest, and also under a bare interpreter:

    python3 tests/test_import_candidates.py

The __main__ fallback exists because pytest and jsonschema are not guaranteed to be
installed in the offline environment.
"""

import json
import sys
from pathlib import Path

# Make scripts/ importable whether launched by pytest (conftest handles it) or bare.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import import_candidates as ic  # noqa: E402
from validate_case_ledgers import core_validate  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "candidate_feed.jsonl"
MASTER = ROOT / "data" / "master" / "master_cases.jsonl"


def _run(tmp_dir):
    return ic.run(
        FIXTURE,
        MASTER,
        Path(tmp_dir),
        apply=False,
        duplicate_threshold=0.85,
        update_threshold=0.55,
        noise_floor=0.35,
        now="2026-07-12",
        report_path=None,
    )


def test_fixture_present():
    assert FIXTURE.exists(), "fixture feed missing"
    assert MASTER.exists(), "master ledger missing"


def test_routes_all_four_branches(tmp_path):
    summary = _run(tmp_path)
    routed = summary["routed"]
    # The fixture is crafted so exactly one row lands in each ledger.
    assert routed["already_listed"] == 1
    assert routed["updates_new_evidence"] == 1
    assert routed["candidate"] == 1
    assert routed["echoes_noise"] == 1
    assert summary["feed_rows"] == 4


def test_duplicate_matches_real_master_case(tmp_path):
    summary = _run(tmp_path)
    by_id = {r["record_id"]: r for r in summary["report_rows"]}
    dup = by_id["FEED-0001"]
    assert dup["routed_to"] == "already_listed.jsonl"
    assert dup["record_type"] == "duplicate"
    assert dup["review_action"] == "reject"
    # matched_case_id must be a real master case id.
    assert dup["matched_case_id"] == "PRUAP-0006"


def test_update_band_routes_to_updates(tmp_path):
    summary = _run(tmp_path)
    by_id = {r["record_id"]: r for r in summary["report_rows"]}
    upd = by_id["FEED-0002"]
    assert upd["routed_to"] == "updates_new_evidence.jsonl"
    assert upd["record_type"] == "update_existing"
    assert upd["review_action"] == "merge"
    assert upd["matched_case_id"] == "PRUAP-0018"


def test_noise_routes_to_echoes(tmp_path):
    summary = _run(tmp_path)
    by_id = {r["record_id"]: r for r in summary["report_rows"]}
    noise = by_id["FEED-0004"]
    assert noise["routed_to"] == "echoes_noise.jsonl"
    assert noise["record_type"] == "echo_noise"
    assert noise["review_action"] == "monitor"


def test_routed_rows_pass_core_validation(tmp_path):
    _run(tmp_path)
    checked = 0
    for name in ("candidate_cases.jsonl", "already_listed.jsonl",
                 "updates_new_evidence.jsonl", "echoes_noise.jsonl"):
        path = tmp_path / name
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            errors, _ = core_validate(row, path=path, line_no=line_no)
            assert errors == [], f"{name}:{line_no} validation errors: {errors}"
            checked += 1
    assert checked == 4


def test_master_is_never_mutated(tmp_path):
    before = MASTER.read_bytes()
    _run(tmp_path)
    assert MASTER.read_bytes() == before, "intake pipeline must never touch master"


def test_normalize_fills_required_defaults():
    row = ic.normalize({"description": "x" * 25, "location_name": "Ponce malecon"},
                       index=7, now="2026-07-12")
    assert row["record_type"] == "candidate"
    assert row["case_id"] is None
    assert row["candidate_id"] == "CAND-0007"
    assert row["evidence_tier"] == "T4"
    assert row["source_url"]  # defaulted, non-empty
    assert row["dedupe_status"] == "not_checked"


def test_missing_required_row_is_quarantined(tmp_path):
    # A feed row missing REQUIRED content fields (here: description) must be
    # quarantined before routing, never written to a ledger.
    feed = tmp_path / "bad_feed.jsonl"
    feed.write_text(
        json.dumps({"record_id": "FEED-BAD1", "location_name": "Ponce"}) + "\n",
        encoding="utf-8",
    )
    summary = ic.run(
        feed, MASTER, tmp_path / "staging",
        apply=False,
        duplicate_threshold=0.85, update_threshold=0.55, noise_floor=0.35,
        now="2026-07-12", report_path=None,
    )
    assert summary["feed_rows"] == 1
    assert sum(summary["routed"].values()) == 0
    assert [q["record_id"] for q in summary["quarantined"]] == ["FEED-BAD1"]
    assert "description" in summary["quarantined"][0]["missing"]


def test_apply_keeps_record_ids_globally_unique_across_ledgers(tmp_path):
    # Guard against cross-ledger duplicate ids: re-running --apply with a stricter
    # duplicate threshold re-routes a record out of already_listed; it must not also
    # be appended to the new target (the validator enforces globally-unique ids).
    fake_root = tmp_path / "data"
    (fake_root / "master").mkdir(parents=True)
    (fake_root / "candidates").mkdir(parents=True)
    fake_master = fake_root / "master" / "master_cases.jsonl"
    fake_master.write_bytes(MASTER.read_bytes())

    common = dict(update_threshold=0.55, noise_floor=0.35, now="2026-07-12", report_path=None)
    # Run 1: FEED-0001 scores as a duplicate -> already_listed.
    ic.run(FIXTURE, fake_master, tmp_path / "s1", apply=True, duplicate_threshold=0.85, **common)
    # Run 2: nothing can clear a 1.0 duplicate bar, so FEED-0001 re-routes to updates.
    ic.run(FIXTURE, fake_master, tmp_path / "s2", apply=True, duplicate_threshold=1.0, **common)

    all_ids = []
    for name in ("candidates/candidate_cases.jsonl", "already_listed.jsonl",
                 "updates_new_evidence.jsonl", "echoes_noise.jsonl"):
        p = fake_root / name
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    all_ids.append(json.loads(line)["record_id"])
    assert len(all_ids) == len(set(all_ids)), f"duplicate record_id across ledgers: {all_ids}"


def test_apply_never_writes_master(tmp_path):
    # Point the "canonical" tree at a temp copy so --apply cannot touch the real repo.
    fake_root = tmp_path / "data"
    (fake_root / "master").mkdir(parents=True)
    (fake_root / "candidates").mkdir(parents=True)
    fake_master = fake_root / "master" / "master_cases.jsonl"
    fake_master.write_bytes(MASTER.read_bytes())
    before = fake_master.read_bytes()

    ic.run(
        FIXTURE, fake_master, tmp_path / "staging",
        apply=True,
        duplicate_threshold=0.85, update_threshold=0.55, noise_floor=0.35,
        now="2026-07-12", report_path=None,
    )
    # aux ledgers written under fake data root; master unchanged.
    assert (fake_root / "already_listed.jsonl").exists()
    assert fake_master.read_bytes() == before


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
