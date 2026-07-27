import importlib.util
from pathlib import Path


def _module():
    path = Path(__file__).parents[1] / "scripts" / "fedmil_review_queue.py"
    spec = importlib.util.spec_from_file_location("fedmil_review_queue", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _candidate(score=0.8):
    return {
        "candidate_id": "cand_" + "1" * 32,
        "case_entity_id": "ent_" + "2" * 32,
        "candidate_score": score,
        "requires_human_review": True,
        "synthetic": True,
    }


def test_queue_excludes_terminal_assessments():
    module = _module()
    candidate = _candidate()
    assert len(module.build_queue([candidate], [])) == 1
    assessment = {
        "candidate_id": candidate["candidate_id"],
        "review_status": "adjudicated",
    }
    assert module.build_queue([candidate], [assessment]) == []


def test_no_known_match_and_data_gap_are_distinct():
    module = _module()
    candidate = _candidate()
    no_match = module.adjudicate(
        candidate,
        classification="NO_KNOWN_MATCH",
        reasoning_summary="Reviewed sources contain no matching activity.",
        reviewer="reviewer-a",
    )
    assert no_match["review_status"] == "adjudicated"
    assert no_match["data_gap_codes"] == []
    try:
        module.adjudicate(
            candidate,
            classification="DATA_GAP",
            reasoning_summary="Missing source.",
            reviewer="reviewer-a",
        )
    except ValueError as exc:
        assert "requires" in str(exc)
    else:
        raise AssertionError("DATA_GAP without codes should fail")


def test_material_findings_require_second_review():
    module = _module()
    candidate = _candidate()
    first = module.adjudicate(
        candidate,
        classification="CONTRADICTORY",
        reasoning_summary=(
            "The documented activity conflicts with the reported characteristics."
        ),
        reviewer="reviewer-a",
    )
    assert first["review_status"] == "needs_second_review"
    second = module.adjudicate(
        candidate,
        classification="CONTRADICTORY",
        reasoning_summary="Second reviewer confirmed the conflict.",
        reviewer="reviewer-a",
        second_reviewer="reviewer-b",
    )
    assert second["review_status"] == "adjudicated"
