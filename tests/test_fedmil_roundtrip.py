import importlib.util
import json
from pathlib import Path

import pytest


def _load():
    path = Path(__file__).parents[1] / "scripts" / "fedmil_roundtrip.py"
    spec = importlib.util.spec_from_file_location("fedmil_roundtrip", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _candidate():
    return {
        "candidate_id": "cand_" + "1" * 32,
        "case_entity_id": "ent_" + "2" * 32,
        "document_id": "doc_" + "3" * 32,
        "finding_id": "find_" + "4" * 32,
        "candidate_basis": ["FACILITY_MATCH"],
        "candidate_score": 0.7,
        "generated_by": "thehub-pr",
        "requires_human_review": True,
        "lineage": {
            "producer_script": "test",
            "producer_phase": "PHASE_3",
            "source_inputs": ["fixture"],
        },
        "synthetic": True,
        "created_at": "2026-07-27T16:00:00Z",
        "extracted_at": "2026-07-27T16:00:00Z",
    }


def _assessment(second_reviewer="reviewer-b"):
    return {
        "assessment_id": "assess_" + "1" * 32,
        "candidate_id": "cand_" + "1" * 32,
        "case_id": "OVNIS-TEST-001",
        "classification": "DIRECT_MATCH",
        "explanatory_strength": 0.4,
        "evidence_strength": 0.7,
        "reasoning_summary": "Two reviewers confirmed the public historical record match.",
        "supports_conventional_explanation": True,
        "contradicts_case_claim": False,
        "data_gap_codes": [],
        "reviewer": "reviewer-a",
        "second_reviewer": second_reviewer,
        "reviewed_at": "2026-07-27T16:00:00Z",
        "review_status": "adjudicated",
        "lineage": {
            "producer_script": "scripts/fedmil_roundtrip.py",
            "producer_phase": "PHASE_3_ROUNDTRIP",
            "source_inputs": ["cand_" + "1" * 32],
        },
        "synthetic": True,
        "created_at": "2026-07-27T16:00:00Z",
        "extracted_at": "2026-07-27T16:00:00Z",
    }


def test_candidate_import_is_idempotent(tmp_path):
    module = _load()
    package = tmp_path / "package"
    package.mkdir()
    source = package / "case_activity_candidates.jsonl"
    source.write_text(json.dumps(_candidate(), sort_keys=True) + "\n")
    target = tmp_path / "pending.jsonl"
    assert module.import_candidates(package, target)["inserted"] == 1
    replay = module.import_candidates(package, target)
    assert replay == {"inserted": 0, "updated": 0, "unchanged": 1}


def test_second_reviewer_must_be_distinct():
    module = _load()
    with pytest.raises(ValueError, match="different identity"):
        module.enforce_reviewer_identity(_assessment("reviewer-a"))


def test_assessment_roundtrip_is_stable(tmp_path):
    module = _load()
    ledger = tmp_path / "assessments.jsonl"
    export = tmp_path / "export"
    first = module.write_assessment_roundtrip(_assessment(), ledger, export)
    second = module.write_assessment_roundtrip(_assessment(), ledger, export)
    assert first["ledger_sha256"] == second["ledger_sha256"]
    assert second["record_count"] == 1
    assert Path(second["export_path"]).read_text() == ledger.read_text()


def test_review_queue_import_excludes_adjudicated(tmp_path):
    module = _load()
    candidates = tmp_path / "candidates.jsonl"
    assessments = tmp_path / "assessments.jsonl"
    candidates.write_text(json.dumps(_candidate()) + "\n")
    assessments.write_text(json.dumps(_assessment()) + "\n")
    assert module.review_queue(candidates, assessments) == []
