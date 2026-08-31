#!/usr/bin/env python3
"""Inventory and optionally copy legacy PRUFON/OVNIS source files.

This script is deliberately byte-oriented. It does not infer case identity from
file names, directory names, proximity, or counts. Its job is to preserve source
paths, sizes, hashes when requested, and copy outcomes so later ingestion can
make stronger semantic claims from explicit evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
}


def parse_source(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("source must be SOURCE_ID=/absolute/path")
    source_id, raw_path = value.split("=", 1)
    source_id = source_id.strip()
    if not source_id:
        raise argparse.ArgumentTypeError("source id cannot be empty")
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        raise argparse.ArgumentTypeError(f"source path must be absolute: {raw_path}")
    return source_id, path


def should_exclude(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    return any(part in EXCLUDED_DIR_NAMES for part in rel.parts)


def iter_source_files(root: Path) -> list[Path]:
    if root.is_file():
        return [] if root.name in EXCLUDED_FILE_NAMES else [root]
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if should_exclude(path, root):
            continue
        files.append(path)
    return files


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def maybe_hash(path: Path, max_hash_bytes: int | None, no_hash: bool = False) -> tuple[str | None, str]:
    if no_hash:
        return None, "HASH_DEFERRED"
    size = path.stat().st_size
    if max_hash_bytes is not None and size > max_hash_bytes:
        return None, "HASH_SKIPPED_OVER_LIMIT"
    return sha256_file(path), "HASHED"


def destination_for(dest_root: Path, source_id: str, root: Path, path: Path) -> Path:
    relative = path.name if root.is_file() else str(path.relative_to(root))
    return dest_root / source_id / relative


def copy_file(source: Path, destination: Path, max_copy_bytes: int | None = None) -> str:
    source_stat = source.stat()
    if destination.exists():
        if destination.is_file() and source_stat.st_size == destination.stat().st_size:
            return "EXISTS_SAME_SIZE"
        return "EXISTS_DIFFERENT_SIZE"
    if max_copy_bytes is not None and source_stat.st_size > max_copy_bytes:
        return "COPY_SKIPPED_OVER_LIMIT"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return "COPIED"


def allocated_bytes(stat_result: Any) -> int | None:
    blocks = getattr(stat_result, "st_blocks", None)
    if blocks is None:
        return None
    return int(blocks) * 512


def is_sparse_or_placeholder(stat_result: Any) -> bool:
    allocated = allocated_bytes(stat_result)
    return allocated is not None and int(stat_result.st_size) > 0 and allocated < int(stat_result.st_size)


def build_record(
    *,
    source_id: str,
    source_root: Path,
    source_path: Path,
    dest_root: Path,
    copy: bool,
    max_hash_bytes: int | None,
    max_copy_bytes: int | None,
    no_hash: bool,
    skip_sparse_sources: bool,
) -> dict[str, Any]:
    stat = source_path.stat()
    sha256, hash_status = maybe_hash(source_path, max_hash_bytes, no_hash=no_hash)
    destination_path = destination_for(dest_root, source_id, source_root, source_path)
    copy_status = "NOT_REQUESTED"
    if copy:
        if skip_sparse_sources and is_sparse_or_placeholder(stat) and not destination_path.exists():
            copy_status = "COPY_SKIPPED_SPARSE_OR_PLACEHOLDER"
        else:
            copy_status = copy_file(source_path, destination_path, max_copy_bytes=max_copy_bytes)
    return {
        "source_id": source_id,
        "source_root": str(source_root),
        "source_path": str(source_path),
        "relative_path": source_path.name
        if source_root.is_file()
        else str(source_path.relative_to(source_root)),
        "destination_path": str(destination_path),
        "size_bytes": stat.st_size,
        "allocated_bytes": allocated_bytes(stat),
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256,
        "hash_status": hash_status,
        "copy_status": copy_status,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_summary(path: Path, rows: list[dict[str, Any]], sources: list[tuple[str, Path]]) -> None:
    by_source = Counter(row["source_id"] for row in rows)
    by_hash_status = Counter(row["hash_status"] for row in rows)
    by_copy_status = Counter(row["copy_status"] for row in rows)
    bytes_by_copy_status: dict[str, int] = {}
    for row in rows:
        copy_status = str(row["copy_status"])
        bytes_by_copy_status[copy_status] = bytes_by_copy_status.get(copy_status, 0) + int(
            row["size_bytes"]
        )
    payload = {
        "claim_scope": "PRUFON/OVNIS filesystem source inventory and optional raw copy manifest",
        "identity_note": (
            "Source folder taxonomy is not canonical identity; semantic case identity remains "
            "unresolved until rows are ingested and deduplicated by stronger evidence."
        ),
        "sources": [{"source_id": source_id, "path": str(path)} for source_id, path in sources],
        "files": len(rows),
        "bytes": sum(int(row["size_bytes"]) for row in rows),
        "allocated_bytes": sum(
            int(row["allocated_bytes"]) for row in rows if row["allocated_bytes"] is not None
        ),
        "by_source": dict(sorted(by_source.items())),
        "by_hash_status": dict(sorted(by_hash_status.items())),
        "by_copy_status": dict(sorted(by_copy_status.items())),
        "bytes_by_copy_status": dict(sorted(bytes_by_copy_status.items())),
        "over_100mb": sum(1 for row in rows if int(row["size_bytes"]) > 100 * 1024 * 1024),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=parse_source, required=True)
    parser.add_argument("--dest-root", type=Path, default=Path("data/legacy_prufon/raw"))
    parser.add_argument("--manifest", type=Path, default=Path("data/legacy_prufon/file_manifest.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("data/legacy_prufon/manifest.json"))
    parser.add_argument("--copy", action="store_true", help="copy files into --dest-root")
    parser.add_argument(
        "--no-hash",
        action="store_true",
        help="record size/path metadata only and mark each file HASH_DEFERRED",
    )
    parser.add_argument(
        "--max-hash-bytes",
        type=int,
        help="skip hashing files larger than this byte count; omit to hash every file",
    )
    parser.add_argument(
        "--max-copy-bytes",
        type=int,
        help="skip copying files larger than this byte count; omit to copy every file",
    )
    parser.add_argument(
        "--skip-sparse-sources",
        action="store_true",
        help="skip copying sources whose allocated bytes are smaller than logical size",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=0,
        help="print a progress line to stderr every N manifest records",
    )
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for source_id, source_root in args.source:
        if not source_root.exists():
            raise FileNotFoundError(source_root)
        for source_path in iter_source_files(source_root):
            rows.append(
                build_record(
                    source_id=source_id,
                    source_root=source_root,
                    source_path=source_path,
                    dest_root=args.dest_root,
                    copy=args.copy,
                    max_hash_bytes=args.max_hash_bytes,
                    max_copy_bytes=args.max_copy_bytes,
                    no_hash=args.no_hash,
                    skip_sparse_sources=args.skip_sparse_sources,
                )
            )
            if args.progress_every and len(rows) % args.progress_every == 0:
                print(f"manifested {len(rows)} files", file=sys.stderr, flush=True)

    write_jsonl(args.manifest, rows)
    write_summary(args.summary, rows, args.source)
    print(json.dumps({"files": len(rows), "manifest": str(args.manifest), "summary": str(args.summary)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
