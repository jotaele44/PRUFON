#!/usr/bin/env python3
"""Adapt a Centinelas ``repository_dispatch`` signal into an OVNIS candidate feed.

Centinelas (the federation "sentinel") classifies anomalous public-interest items
found on the Internet and POSTs each to ovnis-pr as a GitHub ``repository_dispatch``
of type ``centinelas-signal`` (see the sibling emit_dispatches.py). GitHub delivers
the event at ``$GITHUB_EVENT_PATH`` with the intake record wrapped as::

    { "client_payload": { "item_id": ..., "repo": "ovnis-pr", "signal": { ... } } }

``signal`` conforms to Centinelas' ovnis intake contract
(centinelas-pr/src/centinelas/route/contracts/ovnis.schema.json).

This script is a *pure contract adapter*: it transforms the signal into a single
OVNIS candidate-feed row (JSONL) and writes it to a staging path. It does NOT touch
any ledger — the existing scripts/import_candidates.py pipeline (normalize -> score
-> dedupe -> route) consumes the feed and remains the single source of intake logic,
and the master ledger stays read-only + human-gated per the control-plane doctrine.

Rows that cannot supply a Puerto Rico ``location_name`` (or a datable
``date_local`` / ``description``) are written as-is; import_candidates.py's existing
``missing_required`` gate then quarantines them rather than admitting a
schema-invalid case. That is by design — OVNIS is PR-scoped.

Usage:
  python3 scripts/ingest_centinelas_dispatch.py --event "$GITHUB_EVENT_PATH" \
      --out reports/intake/centinelas_feed.jsonl
  python3 scripts/ingest_centinelas_dispatch.py --event sample_event.json --out feed.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# A datable value OVNIS accepts: YYYY, YYYY-MM, or YYYY-MM-DD (mirrors
# validate_case_ledgers.DATE_RE so a coerced date will pass ledger validation).
_DATE_RE = re.compile(r"^[0-9]{4}(-[0-9]{2}){0,2}$")


def coerce_date_local(published_at: Any) -> str | None:
    """Reduce an ISO datetime/date to the OVNIS ``date_local`` grain (drop the time).

    Returns a YYYY[-MM[-DD]] string when the leading date component is valid, else
    None (leaving the row to be quarantined rather than fabricating a date).
    """
    if not isinstance(published_at, str) or not published_at.strip():
        return None
    # ISO datetimes are "YYYY-MM-DDTHH:MM:SS±HH:MM"; the date is everything before 'T'.
    date_part = published_at.strip().split("T", 1)[0]
    return date_part if _DATE_RE.match(date_part) else None


def signal_to_candidate_row(signal: dict[str, Any]) -> dict[str, Any]:
    """Map a Centinelas ovnis intake signal to an OVNIS candidate-feed row.

    Only the content fields OVNIS cannot default (date_local, location_name,
    description) plus provenance are set here; import_candidates.normalize fills the
    rest of the candidate schema. Location comes from the resolved municipalities the
    Centinelas router now forwards for ovnis-pr; absent that, location_name is left
    blank and the row is quarantined downstream.
    """
    title = (signal.get("title") or "").strip()
    body = (signal.get("body_text") or "").strip()
    description = "\n\n".join(part for part in (title, body) if part)

    municipalities = signal.get("municipalities") or []
    location_name = municipalities[0] if municipalities else None
    source_name = signal.get("source_name")

    return {
        "record_id": signal.get("item_id"),
        "date_local": coerce_date_local(signal.get("published_at")),
        "location_name": location_name,
        "municipality": location_name,
        "description": description or None,
        "object_type": "UAP",
        "environment": None,
        "language": "en",
        "evidence_tier": signal.get("evidence_tier") or "T4",
        "source_url": signal.get("source_url"),
        "source_citation": source_name,
        "source_family": source_name,
        "retrieved_at": signal.get("captured_at"),
    }


def extract_signals(event: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull the Centinelas signal(s) out of a repository_dispatch event.

    Centinelas emits one signal per dispatch (client_payload.signal), but accept a
    ``signals`` list too so a batched event or a hand-authored fixture both work.
    """
    client_payload = event.get("client_payload") or event
    if isinstance(client_payload.get("signals"), list):
        return [s for s in client_payload["signals"] if isinstance(s, dict)]
    signal = client_payload.get("signal")
    if isinstance(signal, dict):
        return [signal]
    return []


def run(event_path: Path, out_path: Path) -> dict[str, Any]:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    signals = extract_signals(event)
    rows = [signal_to_candidate_row(s) for s in signals]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    return {"signals": len(signals), "rows": len(rows), "out": str(out_path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event",
        required=True,
        help="Path to the repository_dispatch event JSON (e.g. $GITHUB_EVENT_PATH)",
    )
    parser.add_argument(
        "--out",
        default="reports/intake/centinelas_feed.jsonl",
        help="Where to write the OVNIS candidate feed (JSONL)",
    )
    args = parser.parse_args(argv)

    summary = run(Path(args.event), Path(args.out))
    print(
        f"Centinelas dispatch adapter: {summary['signals']} signal(s) "
        f"-> {summary['rows']} candidate row(s) at {summary['out']}"
    )
    if summary["rows"] == 0:
        print("No signals found in event — nothing to ingest.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
