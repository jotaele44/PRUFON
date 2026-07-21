"""Tests for the Centinelas dispatch adapter (scripts/ingest_centinelas_dispatch.py).

Runs under pytest, and also under a bare interpreter:

    python3 tests/test_ingest_centinelas_dispatch.py

The adapter only bridges the Centinelas ovnis intake contract to an OVNIS candidate
feed; the existing import_candidates.py pipeline does the scoring/dedupe/routing, so
these tests assert the end-to-end handoff: a located signal becomes a routed
candidate, and a location-less signal is quarantined by the existing schema gate.
"""

import json
import sys
from pathlib import Path

# Make scripts/ importable whether launched by pytest (conftest handles it) or bare.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ingest_centinelas_dispatch as adapter  # noqa: E402
import import_candidates as ic  # noqa: E402


def _dispatch_event(signal: dict) -> dict:
    """Wrap a signal the way GitHub delivers a repository_dispatch event."""
    return {"client_payload": {"item_id": signal.get("item_id"), "repo": "ovnis-pr", "signal": signal}}


_LOCATED_SIGNAL = {
    "schema_version": "1.0",
    "item_id": "CENT-UAP-0001",
    "source_url": "https://example.org/anomalous-report",
    "source_name": "The Black Vault",
    "title": "Unidentified craft filmed over Cabo Rojo",
    "body_text": "Multiple witnesses reported a silent disc off the coast at dawn.",
    "published_at": "2026-07-15T09:30:00+00:00",
    "captured_at": "2026-07-16T00:00:00+00:00",
    "evidence_tier": "T2",
    "labels": ["ANOMALOUS"],
    "confidence": 0.9,
    "routed_to": "ovnis-pr",
    "municipalities": ["Cabo Rojo"],
}

_LOCATIONLESS_SIGNAL = {
    "schema_version": "1.0",
    "item_id": "CENT-UAP-0002",
    "source_url": "https://example.org/global-report",
    "source_name": "news",
    "title": "Lights reported over open ocean",
    "body_text": "Distant unverified lights, no fixable location.",
    "published_at": "2026-07-15T09:30:00+00:00",
    "captured_at": "2026-07-16T00:00:00+00:00",
    "evidence_tier": "T4",
    "labels": ["ANOMALOUS"],
    "confidence": 0.6,
    "routed_to": "ovnis-pr",
    "municipalities": [],
}


def test_coerce_date_local_drops_time():
    assert adapter.coerce_date_local("2026-07-15T09:30:00+00:00") == "2026-07-15"
    assert adapter.coerce_date_local("2026-07") == "2026-07"
    assert adapter.coerce_date_local("") is None
    assert adapter.coerce_date_local(None) is None


def test_located_signal_maps_to_candidate_row():
    row = adapter.signal_to_candidate_row(_LOCATED_SIGNAL)
    assert row["record_id"] == "CENT-UAP-0001"
    assert row["date_local"] == "2026-07-15"
    assert row["location_name"] == "Cabo Rojo"
    assert row["municipality"] == "Cabo Rojo"
    assert "Cabo Rojo" in row["description"]
    assert row["evidence_tier"] == "T2"
    assert row["source_url"] == "https://example.org/anomalous-report"


def test_adapter_writes_feed_and_extracts_signal(tmp_path):
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(_dispatch_event(_LOCATED_SIGNAL)), encoding="utf-8")
    out = tmp_path / "feed.jsonl"
    summary = adapter.run(event_path, out)
    assert summary["signals"] == 1 and summary["rows"] == 1
    lines = [l for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["record_id"] == "CENT-UAP-0001"


def _feed_from(signal: dict, tmp_path: Path) -> Path:
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(_dispatch_event(signal)), encoding="utf-8")
    out = tmp_path / "feed.jsonl"
    adapter.run(event_path, out)
    return out


def _empty_master(tmp_path: Path) -> Path:
    master = tmp_path / "master.jsonl"
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("", encoding="utf-8")
    return master


def test_located_signal_routes_as_candidate(tmp_path):
    """End to end: adapter feed -> import_candidates routes it into the candidate ledger."""
    feed = _feed_from(_LOCATED_SIGNAL, tmp_path)
    summary = ic.run(
        feed,
        _empty_master(tmp_path),
        tmp_path / "out",
        apply=False,
        duplicate_threshold=0.85,
        update_threshold=0.55,
        noise_floor=0.35,
        now="2026-07-16",
        report_path=None,
    )
    assert summary["feed_rows"] == 1
    assert summary["routed"]["candidate"] == 1
    assert summary["quarantined"] == []


def test_locationless_signal_is_quarantined(tmp_path):
    """A signal with no resolvable PR location is quarantined by the schema gate, not routed."""
    feed = _feed_from(_LOCATIONLESS_SIGNAL, tmp_path)
    summary = ic.run(
        feed,
        _empty_master(tmp_path),
        tmp_path / "out",
        apply=False,
        duplicate_threshold=0.85,
        update_threshold=0.55,
        noise_floor=0.35,
        now="2026-07-16",
        report_path=None,
    )
    assert summary["feed_rows"] == 1
    assert sum(summary["routed"].values()) == 0
    assert len(summary["quarantined"]) == 1
    assert "location_name" in summary["quarantined"][0]["missing"]


if __name__ == "__main__":
    import tempfile

    test_coerce_date_local_drops_time()
    test_located_signal_maps_to_candidate_row()
    with tempfile.TemporaryDirectory() as d:
        test_adapter_writes_feed_and_extracts_signal(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_located_signal_routes_as_candidate(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_locationless_signal_is_quarantined(Path(d))
    print("All ingest_centinelas_dispatch tests passed.")
