#!/usr/bin/env python3
"""Export OVNIS human assessments of Hub-generated activity candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from prii_export_utils import sha256

from validate_fedmil_context import validate_file


def export_assessments(ledger: Path, out_dir: Path, mode: str, now: str) -> Path:
    errors = validate_file(ledger)
    if errors:
        raise ValueError("; ".join(errors))
    rows = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
    if mode == "production" and any(row.get("synthetic") for row in rows):
        raise ValueError("synthetic assessments are forbidden in production mode")
    if not rows:
        raise ValueError("assessment ledger is empty")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "case_activity_assessments.jsonl"
    target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    file_entry = {
        "filename": target.name,
        "stream": "case_activity_assessments",
        "record_count": len(rows),
        "sha256": sha256(target),
        "schema_id": "federation_case_activity_assessment.schema.json",
    }
    digest = hashlib.sha256(
        f"{target.name}:{file_entry['sha256']}|{mode}".encode()
    ).hexdigest()[:32]
    manifest = {
        "package_id": f"pkg_{digest}",
        "producer": "ovnis-pr",
        "export_contract_version": "1.1.0",
        "mode": mode,
        "created_at": now,
        "extracted_at": now,
        "federation": {
            "producer_repo": "ovnis-pr",
            "hub_parent": "thehub-pr",
            "contract": "fedmil-context-v1",
        },
        "files": [file_entry],
    }
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", default="data/fedmil_context/assessments.jsonl")
    parser.add_argument("--out", default="exports/fedmil-context")
    parser.add_argument("--mode", choices=["test", "production"], default="test")
    args = parser.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    print(export_assessments(Path(args.ledger), Path(args.out), args.mode, now))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
