import csv
import json
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator

import import_prufon_legacy as legacy
from validate_case_ledgers import core_validate

ROOT = Path(__file__).resolve().parents[1]
CASE_SCHEMA = ROOT / "schemas" / "case_record.schema.json"
SOURCE_SCHEMA = ROOT / "schemas" / "source_record.schema.json"


def _base_row(**overrides):
    row = {
        "event_date": "1987-04",
        "municipio": "Lajas",
        "location_text": "Sierra Bermeja foothills",
        "source_tier": "T2",
        "source_ref": "archive:PRUFON:test-001",
        "source_title_original": "Informe de observación",
        "summary": "Historical observation preserved as a structured source report.",
        "confidence": "0.65",
        "review_status": "needs_review",
        "date_conflict": "false",
        "location_conflict": "false",
    }
    row.update(overrides)
    return row


def test_public_schemas_are_valid_draft_2020_12():
    Draft202012Validator.check_schema(json.loads(CASE_SCHEMA.read_text(encoding="utf-8")))
    Draft202012Validator.check_schema(json.loads(SOURCE_SCHEMA.read_text(encoding="utf-8")))


def test_csv_aliases_preserve_issue_facing_fields_without_inference(tmp_path):
    path = tmp_path / "legacy.csv"
    row = _base_row()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)

    cases, sources, rejected = legacy.convert(legacy.read_csv(path))
    assert rejected == []
    assert len(cases) == len(sources) == 1
    case = cases[0]
    assert case["date_local"] == "1987-04"
    assert case["event_date"] == "1987-04"
    assert case["municipality"] == "Lajas"
    assert case["municipio"] == "Lajas"
    assert case["location_name"] == "Sierra Bermeja foothills"
    assert case["location_text"] == "Sierra Bermeja foothills"
    assert case["evidence_tier"] == case["source_tier"] == "T2"
    assert case["source_ref"] == "archive:PRUFON:test-001"
    assert case["case_confidence"] == case["confidence"] == 0.65
    assert case["review_status"] == "needs_review"
    assert case["review_action"] == "pending"
    assert case["latitude"] is None and case["longitude"] is None
    assert case["record_id"].startswith("LEGACY-")


def test_markdown_bounded_date_is_valid_without_exact_date(tmp_path):
    path = tmp_path / "legacy.md"
    path.write_text(
        "| date_start | date_end | municipio | location_text | source_tier | source_ref | summary | review_status |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| 1965 | 1967 | Arecibo | Northern karst area | T1 | doc:bounded-1 | "
        "Bounded historical report with no exact event day asserted. | draft |\n",
        encoding="utf-8",
    )
    cases, _, rejected = legacy.convert(legacy.read_markdown(path))
    assert rejected == []
    case = cases[0]
    assert case["date_local"] is None
    assert case["date_start"] == "1965"
    assert case["date_end"] == "1967"
    errors, _ = core_validate(case, path=path, line_no=1)
    assert errors == []


def test_explicit_unknown_date_and_location_are_accepted():
    row = _base_row(
        event_date=None,
        municipio=None,
        location_text=None,
        date_unknown_reason="Source gives no usable date",
        location_unknown_reason="Source does not identify a place",
    )
    case = legacy.normalize_row(row)
    errors, _ = core_validate(case, path=Path("legacy"), line_no=1)
    assert errors == []
    assert case["date_local"] is None
    assert case["location_name"] is None


def test_missing_evidence_tier_is_rejected_not_defaulted():
    row = _base_row(source_tier=None)
    cases, sources, rejected = legacy.convert([row])
    assert cases == [] and sources == []
    assert len(rejected) == 1
    assert any("evidence_tier" in error for error in rejected[0]["errors"])


def test_missing_source_provenance_is_rejected_not_fabricated():
    row = _base_row(source_ref=None)
    cases, sources, rejected = legacy.convert([row])
    assert cases == [] and sources == []
    assert any("source_url_or_source_ref" in error for error in rejected[0]["errors"])


def _write_minimal_xlsx(path: Path, headers: list[str], values: list[str]) -> None:
    def cell(ref: str, value: str) -> str:
        return f'<c r="{ref}" t="inlineStr"><is><t>{value}</t></is></c>'

    header_cells = "".join(cell(f"{chr(65 + i)}1", value) for i, value in enumerate(headers))
    value_cells = "".join(cell(f"{chr(65 + i)}2", value) for i, value in enumerate(values))
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData><row r="1">{header_cells}</row><row r="2">{value_cells}</row></sheetData>'
        '</worksheet>'
    )
    with zipfile.ZipFile(path, "w") as book:
        book.writestr("xl/worksheets/sheet1.xml", xml)


def test_xlsx_first_sheet_is_parsed_without_openpyxl(tmp_path):
    row = _base_row()
    headers = list(row)
    values = [str(row[key]) for key in headers]
    path = tmp_path / "legacy.xlsx"
    _write_minimal_xlsx(path, headers, values)
    cases, _, rejected = legacy.convert(legacy.read_xlsx(path))
    assert rejected == []
    assert cases[0]["municipality"] == "Lajas"
    assert cases[0]["source_ref"] == "archive:PRUFON:test-001"


def test_source_record_validates_and_preserves_original_title():
    case = legacy.normalize_row(_base_row())
    source = legacy.source_record(case)
    assert source is not None
    schema = json.loads(SOURCE_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(source)
    assert source["source_title_original"] == "Informe de observación"


def test_case_record_validates_against_public_schema():
    case = legacy.normalize_row(_base_row())
    schema = json.loads(CASE_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(case)


def test_conversion_is_deterministic_for_same_raw_row():
    a = legacy.normalize_row(_base_row())
    b = legacy.normalize_row(_base_row())
    assert a["record_id"] == b["record_id"]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
