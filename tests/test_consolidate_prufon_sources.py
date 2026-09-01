import json
from pathlib import Path

import consolidate_prufon_sources as corpus


def test_inventory_excludes_generated_noise(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "case.csv").write_text("case_id,summary\nA,Preserved\n", encoding="utf-8")
    (root / ".DS_Store").write_text("noise", encoding="utf-8")
    cache = root / "__pycache__"
    cache.mkdir()
    (cache / "module.pyc").write_bytes(b"ignored")

    files = corpus.iter_source_files(root)

    assert files == [root / "case.csv"]


def test_manifest_record_preserves_hash_and_relative_destination(tmp_path):
    root = tmp_path / "source"
    nested = root / "Case Evidence"
    nested.mkdir(parents=True)
    source = nested / "report.txt"
    source.write_text("raw report\n", encoding="utf-8")

    record = corpus.build_record(
        source_id="documents_prufon",
        source_root=root,
        source_path=source,
        dest_root=tmp_path / "dest",
        copy=True,
        max_hash_bytes=None,
        max_copy_bytes=None,
        no_hash=False,
        skip_sparse_sources=False,
    )

    assert record["relative_path"] == "Case Evidence/report.txt"
    assert record["copy_status"] == "COPIED"
    assert Path(record["destination_path"]).read_text(encoding="utf-8") == "raw report\n"
    assert record["sha256"] == corpus.sha256_file(source)


def test_hash_can_be_explicitly_deferred(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("defer me", encoding="utf-8")

    digest, status = corpus.maybe_hash(source, max_hash_bytes=None, no_hash=True)

    assert digest is None
    assert status == "HASH_DEFERRED"


def test_large_hash_can_be_explicitly_skipped(tmp_path):
    source = tmp_path / "large.bin"
    source.write_bytes(b"123456")

    digest, status = corpus.maybe_hash(source, max_hash_bytes=3)

    assert digest is None
    assert status == "HASH_SKIPPED_OVER_LIMIT"


def test_copy_records_same_path_different_size_collision(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "dest.txt"
    source.write_text("new", encoding="utf-8")
    destination.write_text("existing", encoding="utf-8")

    assert corpus.copy_file(source, destination) == "EXISTS_DIFFERENT_SIZE"
    assert destination.read_text(encoding="utf-8") == "existing"


def test_copy_can_be_explicitly_deferred_by_size(tmp_path):
    source = tmp_path / "large.bin"
    destination = tmp_path / "dest.bin"
    source.write_bytes(b"123456")

    status = corpus.copy_file(source, destination, max_copy_bytes=3)

    assert status == "COPY_SKIPPED_OVER_LIMIT"
    assert not destination.exists()


def test_allocated_bytes_uses_stat_blocks_when_available():
    class Stat:
        st_blocks = 3

    assert corpus.allocated_bytes(Stat()) == 1536


def test_sparse_or_placeholder_detects_underallocated_payload():
    class Stat:
        st_size = 4096
        st_blocks = 1

    assert corpus.is_sparse_or_placeholder(Stat())


def test_summary_reports_bytes_by_copy_status(tmp_path):
    summary = tmp_path / "manifest.json"
    rows = [
        {
            "source_id": "a",
            "hash_status": "HASH_DEFERRED",
            "copy_status": "EXISTS_SAME_SIZE",
            "size_bytes": 10,
            "allocated_bytes": 10,
        },
        {
            "source_id": "a",
            "hash_status": "HASH_DEFERRED",
            "copy_status": "COPY_SKIPPED_SPARSE_OR_PLACEHOLDER",
            "size_bytes": 90,
            "allocated_bytes": 0,
        },
    ]

    corpus.write_summary(summary, rows, [("a", tmp_path)])

    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["bytes"] == 100
    assert payload["allocated_bytes"] == 10
    assert payload["bytes_by_copy_status"] == {
        "COPY_SKIPPED_SPARSE_OR_PLACEHOLDER": 90,
        "EXISTS_SAME_SIZE": 10,
    }
