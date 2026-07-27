#!/usr/bin/env python3
"""Validate analyst-adjudicated federal/military context records.

This module deliberately contains no portal, HTTP, scraping, or acquisition code.
OVNIS consumes Hub-generated candidates and exports human assessments only.
"""
from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path

ASSESSMENT_ID = re.compile(r"^assess_[a-f0-9]{32}$")
CANDIDATE_ID = re.compile(r"^cand_[a-f0-9]{32}$")
CLASSIFICATIONS = {
    "DIRECT_MATCH",
    "TEMPORAL_GEOGRAPHIC_MATCH",
    "PLAUSIBLE_CONTEXT",
    "WEAK_ASSOCIATION",
    "CONTRADICTORY",
    "POST_EVENT_DISCLOSURE",
    "BACKGROUND_ONLY",
    "NO_KNOWN_MATCH",
    "DATA_GAP",
    "EXCLUDED",
}
REVIEW_STATES = {
    "pending",
    "needs_second_review",
    "adjudicated",
    "excluded",
    "deferred",
}
MATERIAL_SECOND_REVIEW = {"DIRECT_MATCH", "CONTRADICTORY"}


def validate_assessment(row: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "assessment_id",
        "candidate_id",
        "case_id",
        "classification",
        "explanatory_strength",
        "evidence_strength",
        "reasoning_summary",
        "supports_conventional_explanation",
        "contradicts_case_claim",
        "data_gap_codes",
        "reviewer",
        "reviewed_at",
        "review_status",
        "lineage",
        "synthetic",
        "created_at",
        "extracted_at",
    }
    missing = sorted(required - row.keys())
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
        return errors
    if not ASSESSMENT_ID.fullmatch(str(row["assessment_id"])):
        errors.append("invalid assessment_id")
    if not CANDIDATE_ID.fullmatch(str(row["candidate_id"])):
        errors.append("invalid candidate_id")
    if row["classification"] not in CLASSIFICATIONS:
        errors.append("invalid classification")
    if row["review_status"] not in REVIEW_STATES:
        errors.append("invalid review_status")
    for field in ("explanatory_strength", "evidence_strength"):
        value = row[field]
        valid_number = isinstance(value, (int, float)) and not isinstance(
            value, bool
        )
        if not valid_number or not 0 <= value <= 1:
            errors.append(f"{field} must be in [0, 1]")
    if row["classification"] == "DATA_GAP" and not row["data_gap_codes"]:
        errors.append("DATA_GAP requires at least one data_gap_code")
    if row["classification"] == "NO_KNOWN_MATCH" and row["data_gap_codes"]:
        errors.append("NO_KNOWN_MATCH cannot carry unresolved data gaps")
    if row["review_status"] == "adjudicated" and not str(
        row["reviewer"]
    ).strip():
        errors.append("adjudicated assessment requires reviewer")
    if (
        row["review_status"] == "adjudicated"
        and row["classification"] in MATERIAL_SECOND_REVIEW
        and not str(row.get("second_reviewer") or "").strip()
    ):
        errors.append("material adjudication requires second_reviewer")
    if (
        row["review_status"] == "needs_second_review"
        and row["classification"] not in MATERIAL_SECOND_REVIEW
    ):
        errors.append("needs_second_review is limited to material findings")
    return errors


def load_jsonl(path: Path) -> Iterable[tuple[int, dict]]:
    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        if raw.strip():
            yield lineno, json.loads(raw)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for lineno, row in load_jsonl(path):
        assessment_id = str(row.get("assessment_id", ""))
        if assessment_id in seen:
            errors.append(
                f"{path}:{lineno}: duplicate assessment_id {assessment_id}"
            )
        seen.add(assessment_id)
        errors.extend(
            f"{path}:{lineno}: {error}"
            for error in validate_assessment(row)
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ledger",
        nargs="?",
        default="data/fedmil_context/assessments.jsonl",
    )
    args = parser.parse_args()
    errors = validate_file(Path(args.ledger))
    if errors:
        print("\n".join(errors))
        return 1
    print("fedmil context ledger valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
