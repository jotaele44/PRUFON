import importlib.util
from pathlib import Path


def _load_validator():
    path = Path(__file__).parents[1] / "scripts" / "validate_fedmil_context.py"
    spec = importlib.util.spec_from_file_location("validate_fedmil_context", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _row(classification="NO_KNOWN_MATCH", gaps=None):
    return {
        "assessment_id": "assess_" + "1" * 32,
        "candidate_id": "cand_" + "2" * 32,
        "case_id": "OVNIS-TEST",
        "classification": classification,
        "explanatory_strength": 0.0,
        "evidence_strength": 0.8,
        "reasoning_summary": "Synthetic adjudication fixture.",
        "supports_conventional_explanation": False,
        "contradicts_case_claim": False,
        "data_gap_codes": gaps or [],
        "reviewer": "reviewer",
        "reviewed_at": "2026-07-27T12:00:00-04:00",
        "review_status": "adjudicated",
        "lineage": {"producer_script": "test", "producer_phase": "TEST", "source_inputs": ["fixture"]},
        "synthetic": True,
        "created_at": "2026-07-27T16:00:00Z",
        "extracted_at": "2026-07-27T16:00:00Z",
    }


def test_no_known_match_is_distinct_from_data_gap():
    validator = _load_validator()
    assert validator.validate_assessment(_row()) == []
    errors = validator.validate_assessment(_row("DATA_GAP"))
    assert "DATA_GAP requires at least one data_gap_code" in errors
    assert validator.validate_assessment(_row("DATA_GAP", ["SOURCE_UNAVAILABLE"])) == []


def test_no_known_match_rejects_unresolved_gaps():
    validator = _load_validator()
    errors = validator.validate_assessment(_row("NO_KNOWN_MATCH", ["SOURCE_UNAVAILABLE"]))
    assert "NO_KNOWN_MATCH cannot carry unresolved data gaps" in errors


def test_module_contains_no_acquisition_surface():
    source = (Path(__file__).parents[1] / "scripts" / "validate_fedmil_context.py").read_text()
    forbidden = ("requests", "httpx", "urllib.request", "selenium", "playwright")
    assert not any(token in source for token in forbidden)
