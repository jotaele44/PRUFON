#!/usr/bin/env python3
"""Automated OVNIS candidate-intake pipeline.

Implements the intake doctrine described in docs/OVNIS_GITHUB_CONTROL_PLANE.md and
docs/CASE_PROMOTION_STANDARD.md:

    local candidate feed (JSONL)
      -> normalize to the candidate schema
      -> score preliminarily        (reuse scripts/score_candidates.py)
      -> dedupe against master       (reuse scripts/dedupe_candidates.py)
      -> route to the correct aux ledger

Routing (against the master ledger):

    match_score >= --duplicate-threshold      -> already_listed.jsonl   (duplicate / reject)
    --update-threshold <= score < duplicate   -> updates_new_evidence.jsonl (update_existing / merge)
    score below update-threshold:
        case_confidence < --noise-floor         -> echoes_noise.jsonl   (echo_noise / monitor)
        otherwise                                -> candidate_cases.jsonl (candidate / pending)

Guarantees:
  * The master ledger is read-only. This script NEVER writes to it.
  * Fully offline and deterministic; drivable from a local fixture feed.
  * By default routed rows are written into a staging --out-dir (never the canonical
    data ledgers) so a dry run cannot contaminate committed data. Pass --apply to
    append into the canonical data/ aux ledgers (still never master).

This is an intake/routing stage only. It does not promote anything to master;
promotion remains a reviewed pull-request step per the control-plane doctrine.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

# Allow reuse of the sibling intake scripts whether run as a file or imported.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dedupe_candidates import iter_jsonl, match_score  # noqa: E402
from score_candidates import score_row  # noqa: E402
from validate_case_ledgers import REQUIRED as REQUIRED_FIELDS  # noqa: E402

# Full ordered schema key set, mirroring the existing ledger rows.
FULL_KEYS = [
    "record_id", "record_type", "case_id", "candidate_id", "date_local", "time_local",
    "timezone", "location_name", "municipality", "nearest_feature", "latitude", "longitude",
    "location_confidence", "environment", "object_type", "description", "language",
    "translation_status", "witness_type", "witness_count", "evidence_tier", "source_url",
    "source_citation", "source_family", "source_hash", "retrieved_at", "dedupe_status",
    "dedupe_confidence", "matched_case_id", "review_action", "contradiction_note", "gap_note",
    "source_reliability", "chronology_confidence", "case_confidence", "created_at", "updated_at",
]

# ledger key -> canonical filename under the data root (aux ledgers live at data/ root,
# candidate ledger lives under data/candidates/).
LEDGER_FILES = {
    "candidate": "candidates/candidate_cases.jsonl",
    "already_listed": "already_listed.jsonl",
    "updates_new_evidence": "updates_new_evidence.jsonl",
    "echoes_noise": "echoes_noise.jsonl",
}


def normalize(raw: dict[str, Any], *, index: int, now: str) -> dict[str, Any]:
    """Coerce an arbitrary feed row into a complete candidate-schema record."""
    row: dict[str, Any] = {k: raw.get(k) for k in FULL_KEYS}

    cand_id = raw.get("candidate_id") or raw.get("record_id") or f"CAND-{index:04d}"
    row["candidate_id"] = cand_id
    row["record_id"] = raw.get("record_id") or cand_id
    row["record_type"] = "candidate"
    row["case_id"] = None
    row["timezone"] = raw.get("timezone") or "America/Puerto_Rico"

    if not row.get("evidence_tier"):
        row["evidence_tier"] = "T4"
    if not row.get("source_url"):
        row["source_url"] = raw.get("source_citation") or "offline-intake"
    if not row.get("language"):
        row["language"] = "unknown"

    # Intake rows arrive unchecked; dedupe/scoring below refine these.
    row["dedupe_status"] = "not_checked"
    row["matched_case_id"] = None
    row["review_action"] = "pending"
    row["created_at"] = raw.get("created_at") or now
    row["updated_at"] = now
    return row


def route_row(
    row: dict[str, Any],
    masters: list[dict[str, Any]],
    *,
    duplicate_threshold: float,
    update_threshold: float,
    noise_floor: float,
) -> tuple[str, dict[str, Any]]:
    """Score, dedupe, and assign a routed copy of ``row`` to an aux ledger."""
    scored = score_row(row)

    best_score = 0.0
    best_master: dict[str, Any] | None = None
    for master in masters:
        s = match_score(scored, master)
        if s > best_score:
            best_score, best_master = s, master

    matched_id = None
    if best_master is not None:
        matched_id = best_master.get("case_id") or best_master.get("record_id")

    scored["dedupe_confidence"] = round(best_score, 3)
    scored["matched_case_id"] = matched_id

    if best_master is not None and best_score >= duplicate_threshold:
        target = "already_listed"
        scored["record_type"] = "duplicate"
        scored["dedupe_status"] = "duplicate"
        scored["review_action"] = "reject"
    elif best_master is not None and best_score >= update_threshold:
        target = "updates_new_evidence"
        scored["record_type"] = "update_existing"
        scored["dedupe_status"] = "update_existing"
        scored["review_action"] = "merge"
    elif float(scored.get("case_confidence") or 0.0) < noise_floor:
        target = "echoes_noise"
        scored["record_type"] = "echo_noise"
        scored["dedupe_status"] = "rejected"
        scored["review_action"] = "monitor"
        scored["matched_case_id"] = None
    else:
        target = "candidate"
        scored["record_type"] = "candidate"
        scored["dedupe_status"] = "new"
        scored["review_action"] = "pending"
        scored["matched_case_id"] = None

    ordered = {k: scored.get(k) for k in FULL_KEYS}
    return target, ordered


def missing_required(row: dict[str, Any]) -> list[str]:
    """Return the REQUIRED schema fields that are absent or empty on ``row``.

    ``normalize`` defaults the structural fields (record_id, source_url, tiers, …)
    but content fields — date_local, location_name, description — come straight
    from the feed with no default. A row missing any REQUIRED field would append
    schema-invalid JSONL that ``validate_case_ledgers.py`` then rejects, so such
    rows are quarantined before routing rather than fabricating placeholder values.
    """
    return [k for k in REQUIRED_FIELDS if not str(row.get(k) or "").strip()]


def existing_record_ids(paths: list[Path]) -> set[str]:
    """Union of ``record_id`` values already present across ``paths`` (missing ok)."""
    ids: set[str] = set()
    for p in paths:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    ids.add(str(json.loads(line).get("record_id", "")))
    return ids


def write_ledger(
    path: Path, rows: list[dict[str, Any]], *, append: bool, reserved: set[str] | None = None
) -> int:
    """Write ``rows`` to ``path`` as JSONL. Idempotent on record_id when appending.

    ``reserved`` pre-seeds the seen-set with record_ids already committed to *other*
    canonical ledgers, so a rerun that re-routes a record to a different ledger cannot
    create a duplicate id across ledgers (which the global validator would reject).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_lines: list[str] = []
    seen: set[str] = set(reserved or ())
    if append and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_lines.append(line)
                seen.add(str(json.loads(line).get("record_id", "")))

    added = 0
    new_lines: list[str] = []
    for row in rows:
        rid = str(row.get("record_id", ""))
        if rid in seen:
            continue
        seen.add(rid)
        new_lines.append(json.dumps(row, ensure_ascii=False))
        added += 1

    all_lines = existing_lines + new_lines
    path.write_text("\n".join(all_lines) + ("\n" if all_lines else ""), encoding="utf-8")
    return added


def run(
    feed_path: Path,
    master_path: Path,
    out_dir: Path,
    *,
    apply: bool,
    duplicate_threshold: float,
    update_threshold: float,
    noise_floor: float,
    now: str,
    report_path: Path | None,
) -> dict[str, Any]:
    """Execute the intake pipeline. Returns a routing summary dict."""
    feed = iter_jsonl(feed_path)
    masters = iter_jsonl(master_path)

    routed: dict[str, list[dict[str, Any]]] = {k: [] for k in LEDGER_FILES}
    report_rows: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []

    for i, raw in enumerate(feed, start=1):
        normalized = normalize(raw, index=i, now=now)
        # Schema-gate before routing: never let a row missing a REQUIRED field reach
        # the ledgers (with --apply that would append data the validator rejects).
        gaps = missing_required(normalized)
        if gaps:
            quarantined.append({"record_id": normalized.get("record_id"), "missing": gaps})
            continue
        target, row = route_row(
            normalized,
            masters,
            duplicate_threshold=duplicate_threshold,
            update_threshold=update_threshold,
            noise_floor=noise_floor,
        )
        routed[target].append(row)
        report_rows.append({
            "record_id": row["record_id"],
            "routed_to": LEDGER_FILES[target],
            "record_type": row["record_type"],
            "dedupe_status": row["dedupe_status"],
            "review_action": row["review_action"],
            "matched_case_id": row["matched_case_id"],
            "dedupe_confidence": row["dedupe_confidence"],
            "case_confidence": row["case_confidence"],
        })

    # When appending to the canonical ledgers, reserve every record_id already
    # committed to ANY aux/candidate ledger so a re-routed record can't be duplicated
    # across ledgers (the repo validator enforces globally-unique ids). Also carry ids
    # written earlier in this same run forward to later targets.
    data_root = master_path.parents[1]
    reserved: set[str] = (
        existing_record_ids([data_root / fn for fn in LEDGER_FILES.values()]) if apply else set()
    )

    counts: dict[str, int] = {}
    for key, rows in routed.items():
        if not rows:
            counts[key] = 0
            continue
        if apply:
            # data root = parent of data/master/ ; aux ledgers live at data/ root.
            target_path = data_root / LEDGER_FILES[key]
        else:
            target_path = out_dir / Path(LEDGER_FILES[key]).name
        counts[key] = write_ledger(target_path, rows, append=apply, reserved=reserved)
        reserved |= {str(r.get("record_id", "")) for r in rows}

    if report_path is not None and report_rows:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        fields = list(report_rows[0].keys())
        with report_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(report_rows)

    return {
        "feed_rows": len(feed),
        "routed": counts,
        "report_rows": report_rows,
        "quarantined": quarantined,
        "apply": apply,
        "out_dir": str(out_dir),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OVNIS automated candidate-intake pipeline")
    parser.add_argument("feed", help="Local candidate feed (JSONL) to ingest")
    parser.add_argument("--master", default="data/master/master_cases.jsonl")
    parser.add_argument(
        "--out-dir",
        default="reports/intake",
        help="Staging directory for routed ledgers (default; never touches canonical data/).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Append routed rows into the canonical data/ aux + candidate ledgers "
             "(still never master). Off by default.",
    )
    parser.add_argument("--report", default="reports/intake/routing_report.csv")
    parser.add_argument("--duplicate-threshold", type=float, default=0.85)
    parser.add_argument("--update-threshold", type=float, default=0.55)
    parser.add_argument("--noise-floor", type=float, default=0.35)
    parser.add_argument("--now", default="2026-07-12")
    args = parser.parse_args(argv)

    summary = run(
        Path(args.feed),
        Path(args.master),
        Path(args.out_dir),
        apply=args.apply,
        duplicate_threshold=args.duplicate_threshold,
        update_threshold=args.update_threshold,
        noise_floor=args.noise_floor,
        now=args.now,
        report_path=Path(args.report) if args.report else None,
    )

    dest = "canonical data/ ledgers" if args.apply else f"staging dir {args.out_dir}"
    print(f"OVNIS candidate intake: {summary['feed_rows']} feed rows -> {dest}")
    for key, filename in LEDGER_FILES.items():
        print(f"  {filename:<34} {summary['routed'].get(key, 0)}")
    if summary["quarantined"]:
        print(f"  {'(quarantined: missing required)':<34} {len(summary['quarantined'])}")
    if args.report:
        print(f"Routing report: {args.report}")
    print("Master ledger untouched (read-only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
