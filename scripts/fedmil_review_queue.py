#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL = {"adjudicated", "excluded"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def build_queue(candidates: list[dict[str, Any]], assessments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_candidate = {str(row["candidate_id"]): row for row in assessments}
    queue: list[dict[str, Any]] = []
    for candidate in candidates:
        assessment = by_candidate.get(str(candidate["candidate_id"]))
        if assessment and assessment.get("review_status") in TERMINAL:
            continue
        queue.append({
            "candidate": candidate,
            "assessment": assessment,
            "state": "second_review" if assessment and assessment.get("review_status") == "needs_second_review" else "pending",
        })
    return sorted(queue, key=lambda row: float(row["candidate"].get("candidate_score", 0)), reverse=True)


def adjudicate(
    candidate: dict[str, Any],
    *,
    classification: str,
    reasoning_summary: str,
    reviewer: str,
    second_reviewer: str | None = None,
    data_gap_codes: list[str] | None = None,
) -> dict[str, Any]:
    gaps = data_gap_codes or []
    if classification == "DATA_GAP" and not gaps:
        raise ValueError("DATA_GAP requires at least one data gap code")
    if classification == "NO_KNOWN_MATCH" and gaps:
        raise ValueError("NO_KNOWN_MATCH cannot retain unresolved data gaps")
    needs_second = classification in {"DIRECT_MATCH", "CONTRADICTORY"} and not second_reviewer
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "assessment_id": "assess_" + str(candidate["candidate_id"]).split("_", 1)[1],
        "candidate_id": candidate["candidate_id"],
        "case_id": candidate.get("case_id") or candidate.get("case_entity_id"),
        "classification": classification,
        "explanatory_strength": 0.0,
        "evidence_strength": float(candidate.get("candidate_score", 0)),
        "reasoning_summary": reasoning_summary,
        "supports_conventional_explanation": classification in {"DIRECT_MATCH", "PLAUSIBLE_CONTEXT"},
        "contradicts_case_claim": classification == "CONTRADICTORY",
        "data_gap_codes": gaps,
        "reviewer": reviewer,
        "second_reviewer": second_reviewer,
        "reviewed_at": now,
        "review_status": "needs_second_review" if needs_second else "adjudicated",
        "lineage": {
            "producer_script": "scripts/fedmil_review_queue.py",
            "producer_phase": "PHASE_2_HUMAN_ADJUDICATION",
            "source_inputs": [candidate["candidate_id"]],
            "extraction_method": "human_review",
        },
        "synthetic": bool(candidate.get("synthetic")),
        "created_at": now,
        "extracted_at": now,
    }


def append_assessment(path: Path, assessment: dict[str, Any]) -> None:
    rows = load_jsonl(path)
    rows = [row for row in rows if row.get("candidate_id") != assessment["candidate_id"]]
    rows.append(assessment)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="data/fedmil_context/pending_candidates.jsonl")
    parser.add_argument("--assessments", default="data/fedmil_context/assessments.jsonl")
    args = parser.parse_args()
    queue = build_queue(load_jsonl(Path(args.candidates)), load_jsonl(Path(args.assessments)))
    print(json.dumps(queue, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
