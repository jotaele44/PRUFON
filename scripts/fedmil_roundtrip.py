#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from fedmil_review_queue import append_assessment, build_queue, load_jsonl
from validate_fedmil_context import validate_assessment


def import_candidates(package_dir: Path, target: Path) -> dict[str, int]:
    source = package_dir / "case_activity_candidates.jsonl"
    incoming = load_jsonl(source)
    existing = {str(row["candidate_id"]): row for row in load_jsonl(target)}
    inserted = updated = unchanged = 0
    for row in incoming:
        candidate_id = str(row["candidate_id"])
        current = existing.get(candidate_id)
        if current is None:
            inserted += 1
        elif json.dumps(current, sort_keys=True) == json.dumps(row, sort_keys=True):
            unchanged += 1
        else:
            updated += 1
        existing[candidate_id] = row
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "".join(json.dumps(existing[key], sort_keys=True) + "\n" for key in sorted(existing))
    )
    return {"inserted": inserted, "updated": updated, "unchanged": unchanged}


def enforce_reviewer_identity(assessment: dict[str, Any]) -> None:
    reviewer = str(assessment.get("reviewer") or "").strip()
    second = str(assessment.get("second_reviewer") or "").strip()
    if second and reviewer == second:
        raise ValueError("second_reviewer must be a different identity from reviewer")
    errors = validate_assessment(assessment)
    if errors:
        raise ValueError("; ".join(errors))


def write_assessment_roundtrip(
    assessment: dict[str, Any],
    ledger: Path,
    export_dir: Path,
) -> dict[str, Any]:
    enforce_reviewer_identity(assessment)
    append_assessment(ledger, assessment)
    rows = load_jsonl(ledger)
    canonical = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    export_dir.mkdir(parents=True, exist_ok=True)
    target = export_dir / "case_activity_assessments.jsonl"
    target.write_text(canonical)
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    return {
        "assessment_id": assessment["assessment_id"],
        "candidate_id": assessment["candidate_id"],
        "ledger_sha256": digest,
        "record_count": len(rows),
        "export_path": str(target),
    }


def review_queue(candidate_path: Path, assessment_path: Path) -> list[dict[str, Any]]:
    return build_queue(load_jsonl(candidate_path), load_jsonl(assessment_path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package")
    parser.add_argument(
        "--candidates",
        default="data/fedmil_context/pending_candidates.jsonl",
    )
    parser.add_argument(
        "--assessments",
        default="data/fedmil_context/assessments.jsonl",
    )
    args = parser.parse_args()
    candidate_path = Path(args.candidates)
    if args.package:
        print(json.dumps(import_candidates(Path(args.package), candidate_path), sort_keys=True))
    print(json.dumps(review_queue(candidate_path, Path(args.assessments)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
