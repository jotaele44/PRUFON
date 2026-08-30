from pathlib import Path

import pytest

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
        no_hash=False,
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


def test_copy_refuses_same_path_different_size_collision(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "dest.txt"
    source.write_text("new", encoding="utf-8")
    destination.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        corpus.copy_file(source, destination)
