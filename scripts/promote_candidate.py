#!/usr/bin/env python3
"""Promote ONE reviewed candidate row into the master ledger.

This is the reviewed, human-gated promotion step referenced in
docs/CASE_PROMOTION_STANDARD.md and docs/OVNIS_GITHUB_CONTROL_PLANE.md. The
intake pipeline (scripts/import_candidates.py) only routes rows into the
candidate / aux ledgers and never touches master. Promotion is the *separate*
step that moves a single reviewed candidate into data/master/master_cases.jsonl.

Safety doctrine:
  * Promotion is refused unless the operator passes BOTH an explicit
    --record-id <id> AND the --i-have-reviewed acknowledgement flag.
  * The selected row is re-transformed into a master record and re-validated with
    ``core_validate`` (imported from validate_case_ledgers) *before* anything is
    written; an invalid row is refused and nothing changes on disk.
  * The master ledger is append-only: promotion only ever appends one line and
    never rewrites existing master rows. A fresh, unused master record_id and
    case_id are minted so promotion cannot collide with an existing case.
  * Placeholder rows (source_family == "placeholder") are refused outright.

The promoted candidate is removed from the candidate ledger (the candidate ledger
is not append-only) so it cannot be promoted twice. Candidate lineage is preserved
on the master row via ``candidate_id`` and the ``promoted_from`` provenance field.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Allow reuse of the sibling intake/validation scripts whether run as a file or imported.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from import_candidates import FULL_KEYS  # noqa: E402
from validate_case_ledgers import core_validate, iter_jsonl  # noqa: E402


class PromotionError(Exception):
    """Raised when a promotion is refused. Nothing is written when this is raised."""


def _next_sequence_id(masters: list[dict[str, Any]], key: str, prefix: str) -> str:
    """Return the next unused ``prefix``NNNN id for ``key`` across ``masters``."""
    max_n = 0
    for m in masters:
        value = str(m.get(key) or "")
        if value.startswith(prefix):
            suffix = value[len(prefix):]
            if suffix.isdigit():
                max_n = max(max_n, int(suffix))
    return f"{prefix}{max_n + 1:04d}"


def build_master_row(
    candidate: dict[str, Any],
    masters: list[dict[str, Any]],
    *,
    now: str,
    case_id: str | None = None,
) -> dict[str, Any]:
    """Transform a reviewed candidate row into a master-ledger record.

    Mints fresh master record_id / case_id, stamps promotion provenance, and
    normalizes the review/dedupe fields so the row satisfies the master gates in
    ``core_validate`` (case_id present, review_action in {promote, merge},
    dedupe_status != not_checked).
    """
    source_candidate_id = candidate.get("candidate_id") or candidate.get("record_id")

    promoted: dict[str, Any] = dict(candidate)
    # Strip validator bookkeeping keys that iter_jsonl attaches.
    for meta_key in ("__path", "__line"):
        promoted.pop(meta_key, None)

    promoted["record_id"] = _next_sequence_id(masters, "record_id", "PRUFON-")
    promoted["case_id"] = case_id or _next_sequence_id(masters, "case_id", "PRUAP-")
    promoted["candidate_id"] = source_candidate_id
    promoted["record_type"] = "master"

    # A promoted case stands on its own; it is not a dedupe match of another case.
    promoted["matched_case_id"] = None
    # Master rows must carry a decisive review action and a checked dedupe state.
    if promoted.get("review_action") not in {"promote", "merge"}:
        promoted["review_action"] = "promote"
    if promoted.get("dedupe_status") in (None, "", "not_checked"):
        promoted["dedupe_status"] = "new"

    promoted["updated_at"] = now

    # Provenance stamp (schema allows additional properties).
    promoted["promoted_from"] = candidate.get("record_id")
    promoted["promoted_at"] = now
    note = f"promoted from candidate {candidate.get('record_id')} on {now}"
    existing_gap = str(promoted.get("gap_note") or "").strip()
    promoted["gap_note"] = f"{existing_gap}; {note}" if existing_gap else note

    # Preserve the canonical master key order, then append provenance keys.
    ordered = {k: promoted.get(k) for k in FULL_KEYS}
    for extra in ("promoted_from", "promoted_at"):
        ordered[extra] = promoted[extra]
    return ordered


def append_master(master_path: Path, row: dict[str, Any]) -> None:
    """Append a single JSONL row to the master ledger (append-only)."""
    line = json.dumps(row, ensure_ascii=False)
    existing = master_path.read_text(encoding="utf-8") if master_path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    master_path.write_text(existing + line + "\n", encoding="utf-8")


def rewrite_candidates_without(candidates_path: Path, record_id: str) -> None:
    """Rewrite the candidate ledger dropping the single promoted ``record_id``."""
    kept: list[str] = []
    for line in candidates_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if str(json.loads(line).get("record_id", "")) == record_id:
            continue
        kept.append(line)
    candidates_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")


def promote(
    record_id: str,
    *,
    candidates_path: Path,
    master_path: Path,
    reviewed: bool,
    now: str,
    case_id: str | None = None,
) -> dict[str, Any]:
    """Promote one reviewed candidate into master. Raises PromotionError on refusal.

    Nothing is written unless every gate passes: the reviewed flag is set, the
    record exists, it is not a placeholder, and the transformed master row passes
    ``core_validate``.
    """
    if not reviewed:
        raise PromotionError(
            "refused: promotion requires the --i-have-reviewed acknowledgement flag"
        )

    candidates = iter_jsonl(candidates_path)
    matches = [c for c in candidates if str(c.get("record_id", "")) == record_id]
    if not matches:
        raise PromotionError(f"refused: no candidate row with record_id {record_id!r}")
    if len(matches) > 1:
        raise PromotionError(f"refused: {len(matches)} rows share record_id {record_id!r}")
    candidate = matches[0]

    if str(candidate.get("source_family") or "").lower() == "placeholder":
        raise PromotionError(
            f"refused: {record_id!r} is a placeholder row and must not be promoted"
        )

    masters = iter_jsonl(master_path) if master_path.exists() else []
    master_row = build_master_row(candidate, masters, now=now, case_id=case_id)

    # Re-validate the transformed row before touching master.
    errors, _warnings = core_validate(master_row, path=master_path, line_no=0)
    if errors:
        raise PromotionError(
            "refused: promoted row failed validation:\n  " + "\n  ".join(errors)
        )

    # Uniqueness guard against the existing master ledger.
    master_ids = {str(m.get("record_id", "")) for m in masters}
    master_case_ids = {str(m.get("case_id", "")) for m in masters}
    if master_row["record_id"] in master_ids:
        raise PromotionError(f"refused: master record_id {master_row['record_id']!r} already exists")
    if master_row["case_id"] in master_case_ids:
        raise PromotionError(f"refused: master case_id {master_row['case_id']!r} already exists")

    # All gates passed: append to master (append-only), then drop from candidates.
    append_master(master_path, master_row)
    rewrite_candidates_without(candidates_path, record_id)

    return {
        "promoted_record_id": record_id,
        "master_record_id": master_row["record_id"],
        "master_case_id": master_row["case_id"],
        "master_path": str(master_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote ONE reviewed candidate row into the master ledger."
    )
    parser.add_argument(
        "--record-id",
        required=True,
        help="record_id of the candidate row to promote (required).",
    )
    parser.add_argument(
        "--i-have-reviewed",
        action="store_true",
        help="Explicit acknowledgement that the row has been reviewed. "
             "Promotion is refused without it.",
    )
    parser.add_argument("--candidates", default="data/candidates/candidate_cases.jsonl")
    parser.add_argument("--master", default="data/master/master_cases.jsonl")
    parser.add_argument(
        "--case-id",
        default=None,
        help="Optional explicit master case_id; otherwise the next PRUAP-NNNN is minted.",
    )
    parser.add_argument(
        "--now",
        default=date.today().isoformat(),
        help="Promotion stamp date (YYYY-MM-DD); defaults to the current run date. "
             "Override explicitly for deterministic tests.",
    )
    args = parser.parse_args(argv)

    try:
        result = promote(
            args.record_id,
            candidates_path=Path(args.candidates),
            master_path=Path(args.master),
            reviewed=args.i_have_reviewed,
            now=args.now,
            case_id=args.case_id,
        )
    except PromotionError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(
        f"Promoted candidate {result['promoted_record_id']} -> master "
        f"{result['master_record_id']} (case {result['master_case_id']}). "
        "Master appended; candidate ledger updated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
