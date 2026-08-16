#!/usr/bin/env python3
"""Normalize legacy PRUFON tabular rows without fabricating unknown facts.

Supported inputs:
- CSV with a header row
- Markdown pipe tables
- XLSX workbooks (first worksheet; stdlib ZIP/XML parser, no new dependency)

The adapter emits staging JSONL only. It never writes the canonical master ledger,
never promotes cases, and rejects rows that lack an explicit date representation,
location representation, source provenance, evidence tier, or adequate summary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from validate_case_ledgers import core_validate

TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}

ALIASES = {
    "event_date": "date_local",
    "municipio": "municipality",
    "location": "location_name",
    "location_text": "location_name",
    "lat": "latitude",
    "lon": "longitude",
    "source_tier": "evidence_tier",
    "summary": "description",
    "confidence": "case_confidence",
}

REVIEW_STATUS_TO_ACTION = {
    "draft": "pending",
    "needs_review": "pending",
    "promoted": "promote",
    "rejected": "reject",
}

BOOLEAN_FIELDS = {
    "date_conflict",
    "location_conflict",
    "source_conflict",
    "identity_conflict",
    "narrative_conflict",
}

FLOAT_FIELDS = {
    "latitude",
    "longitude",
    "location_confidence",
    "source_reliability",
    "chronology_confidence",
    "case_confidence",
    "confidence",
}


def _clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value


def _slug_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")


def _stable_record_id(raw: dict[str, Any]) -> str:
    material = json.dumps(raw, sort_keys=True, ensure_ascii=False, default=str)
    return "LEGACY-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16].upper()


def _bool(value: Any) -> bool | None:
    value = _clean(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def _float(value: Any) -> float | None:
    value = _clean(value)
    if value is None:
        return None
    return float(value)


def normalize_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Map legacy aliases to the existing case ledger without semantic guessing."""
    source = {_slug_key(str(k)): _clean(v) for k, v in raw.items() if str(k).strip()}
    mapped: dict[str, Any] = {}
    for key, value in source.items():
        mapped[ALIASES.get(key, key)] = value

    record_id = mapped.get("record_id") or mapped.get("candidate_id") or _stable_record_id(source)
    case_id = mapped.get("case_id")
    review_status = mapped.get("review_status")
    review_action = mapped.get("review_action")
    if review_action is None and review_status is not None:
        review_action = REVIEW_STATUS_TO_ACTION.get(str(review_status).lower())
    if review_action is None:
        review_action = "pending"

    row: dict[str, Any] = {
        "record_id": str(record_id),
        "record_type": str(mapped.get("record_type") or "candidate"),
        "case_id": case_id,
        "candidate_id": mapped.get("candidate_id") or (None if case_id else str(record_id)),
        "date_local": mapped.get("date_local"),
        "event_date": mapped.get("event_date"),
        "date_start": mapped.get("date_start"),
        "date_end": mapped.get("date_end"),
        "date_unknown_reason": mapped.get("date_unknown_reason"),
        "time_local": mapped.get("time_local"),
        "timezone": mapped.get("timezone"),
        "location_name": mapped.get("location_name"),
        "location_text": mapped.get("location_text"),
        "municipality": mapped.get("municipality"),
        "municipio": mapped.get("municipio"),
        "location_unknown_reason": mapped.get("location_unknown_reason"),
        "nearest_feature": mapped.get("nearest_feature"),
        "latitude": mapped.get("latitude"),
        "longitude": mapped.get("longitude"),
        "location_confidence": mapped.get("location_confidence"),
        "environment": mapped.get("environment"),
        "object_type": mapped.get("object_type"),
        "description": mapped.get("description"),
        "summary": mapped.get("summary"),
        "language": mapped.get("language"),
        "translation_status": mapped.get("translation_status"),
        "witness_type": mapped.get("witness_type"),
        "witness_count": mapped.get("witness_count"),
        "evidence_tier": mapped.get("evidence_tier"),
        "source_tier": mapped.get("source_tier"),
        "source_ref": mapped.get("source_ref"),
        "source_url": mapped.get("source_url"),
        "source_citation": mapped.get("source_citation"),
        "source_title_original": mapped.get("source_title_original"),
        "source_family": mapped.get("source_family"),
        "source_hash": mapped.get("source_hash"),
        "retrieved_at": mapped.get("retrieved_at"),
        "dedupe_status": str(mapped.get("dedupe_status") or "not_checked"),
        "dedupe_confidence": mapped.get("dedupe_confidence"),
        "matched_case_id": mapped.get("matched_case_id"),
        "review_action": str(review_action),
        "review_status": review_status,
        "date_conflict": mapped.get("date_conflict"),
        "location_conflict": mapped.get("location_conflict"),
        "source_conflict": mapped.get("source_conflict"),
        "identity_conflict": mapped.get("identity_conflict"),
        "narrative_conflict": mapped.get("narrative_conflict"),
        "contradiction_notes": mapped.get("contradiction_notes"),
        "contradiction_note": mapped.get("contradiction_note"),
        "gap_note": mapped.get("gap_note"),
        "source_reliability": mapped.get("source_reliability"),
        "chronology_confidence": mapped.get("chronology_confidence"),
        "case_confidence": mapped.get("case_confidence"),
        "confidence": mapped.get("confidence"),
        "created_at": mapped.get("created_at"),
        "updated_at": mapped.get("updated_at"),
    }

    for field in FLOAT_FIELDS:
        if field in row:
            row[field] = _float(row[field])
    for field in BOOLEAN_FIELDS:
        row[field] = _bool(row.get(field))

    # Preserve issue-facing aliases explicitly when they were supplied.
    if source.get("event_date") is not None:
        row["event_date"] = source["event_date"]
    if source.get("municipio") is not None:
        row["municipio"] = source["municipio"]
    if source.get("location_text") is not None:
        row["location_text"] = source["location_text"]
    if source.get("source_tier") is not None:
        row["source_tier"] = source["source_tier"]
    if source.get("summary") is not None:
        row["summary"] = source["summary"]
    if source.get("confidence") is not None:
        row["confidence"] = _float(source["confidence"])

    return row


def source_record(case: dict[str, Any]) -> dict[str, Any] | None:
    ref = case.get("source_ref") or case.get("source_url")
    if not ref or not case.get("evidence_tier"):
        return None
    return {
        "source_ref": ref,
        "source_tier": case["evidence_tier"],
        "source_url": case.get("source_url"),
        "source_title": case.get("source_citation"),
        "source_title_original": case.get("source_title_original"),
        "source_family": case.get("source_family"),
        "language": case.get("language"),
        "retrieved_at": case.get("retrieved_at"),
        "sha256": case.get("source_hash"),
    }


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_markdown(path: Path) -> list[dict[str, Any]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if "|" in line]
    if len(lines) < 2:
        raise ValueError("markdown table requires a header and separator row")

    def cells(line: str) -> list[str]:
        return [part.strip() for part in line.strip().strip("|").split("|")]

    headers = cells(lines[0])
    separator = cells(lines[1])
    if len(headers) != len(separator) or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise ValueError("invalid markdown table separator")
    rows: list[dict[str, Any]] = []
    for line in lines[2:]:
        values = cells(line)
        if len(values) != len(headers):
            raise ValueError("markdown row column count does not match header")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def _shared_strings(book: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in book.namelist():
        return []
    root = ET.fromstring(book.read(name))
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    strings: list[str] = []
    for item in root.findall(f"{ns}si"):
        strings.append("".join(node.text or "" for node in item.iter(f"{ns}t")))
    return strings


def _cell_value(cell: ET.Element, shared: list[str], ns: str) -> str | None:
    value = cell.find(f"{ns}v")
    if value is None:
        inline = cell.find(f"{ns}is")
        if inline is None:
            return None
        return "".join(node.text or "" for node in inline.iter(f"{ns}t"))
    text = value.text or ""
    if cell.attrib.get("t") == "s":
        return shared[int(text)]
    return text


def read_xlsx(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as book:
        sheet_names = sorted(
            name
            for name in book.namelist()
            if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name)
        )
        if not sheet_names:
            raise ValueError("xlsx has no worksheets")
        shared = _shared_strings(book)
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        root = ET.fromstring(book.read(sheet_names[0]))
        table: list[list[str | None]] = []
        for row in root.iter(f"{ns}row"):
            values: list[str | None] = []
            for cell in row.findall(f"{ns}c"):
                ref = cell.attrib.get("r", "A1")
                col_letters = re.match(r"[A-Z]+", ref)
                if not col_letters:
                    continue
                col = 0
                for ch in col_letters.group(0):
                    col = col * 26 + (ord(ch) - ord("A") + 1)
                while len(values) < col - 1:
                    values.append(None)
                values.append(_cell_value(cell, shared, ns))
            table.append(values)
    if not table:
        return []
    headers = [str(value or "").strip() for value in table[0]]
    rows: list[dict[str, Any]] = []
    for values in table[1:]:
        padded = values + [None] * (len(headers) - len(values))
        rows.append({headers[i]: padded[i] for i in range(len(headers)) if headers[i]})
    return rows


def read_rows(path: Path, input_format: str | None = None) -> list[dict[str, Any]]:
    fmt = (input_format or path.suffix.lstrip(".")).lower()
    if fmt == "csv":
        return read_csv(path)
    if fmt in {"md", "markdown"}:
        return read_markdown(path)
    if fmt == "xlsx":
        return read_xlsx(path)
    raise ValueError(f"unsupported legacy input format: {fmt}")


def convert(
    rows: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    rejected: list[dict[str, Any]] = []
    for index, raw in enumerate(rows, start=1):
        try:
            case = normalize_row(raw)
        except (TypeError, ValueError) as exc:
            rejected.append(
                {"row": index, "record_id": raw.get("record_id"), "errors": [str(exc)]}
            )
            continue
        errors, warnings = core_validate(case, path=Path("legacy-input"), line_no=index)
        if errors:
            rejected.append(
                {
                    "row": index,
                    "record_id": case["record_id"],
                    "errors": errors,
                    "warnings": warnings,
                }
            )
            continue
        accepted.append(case)
        src = source_record(case)
        if src is not None:
            sources[str(src["source_ref"])] = src
    return accepted, list(sources.values()), rejected


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize legacy PRUFON CSV/Markdown/XLSX rows")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["csv", "md", "markdown", "xlsx"])
    parser.add_argument("--out", type=Path, required=True, help="staging case JSONL output")
    parser.add_argument("--sources-out", type=Path, help="optional source-lineage JSONL output")
    parser.add_argument("--report", type=Path, help="optional machine-readable conversion report")
    parser.add_argument("--strict", action="store_true", help="exit nonzero when any row is rejected")
    args = parser.parse_args()

    rows = read_rows(args.input, args.format)
    cases, sources, rejected = convert(rows)
    write_jsonl(args.out, cases)
    if args.sources_out:
        write_jsonl(args.sources_out, sources)
    report = {
        "input": str(args.input),
        "rows": len(rows),
        "accepted": len(cases),
        "rejected": len(rejected),
        "source_records": len(sources),
        "rejections": rejected,
        "master_mutated": False,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, sort_keys=True))
    return 1 if args.strict and rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
