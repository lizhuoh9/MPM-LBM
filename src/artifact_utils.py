import csv
import glob
import json
import os
from pathlib import Path


LARGE_FILE_THRESHOLD_MB = 5.0


def format_size(num_bytes: int) -> str:
    if num_bytes < 0:
        raise ValueError("num_bytes must be non-negative")
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024**2:
        return f"{num_bytes / 1024.0:.2f} KB"
    return f"{num_bytes / 1024.0 / 1024.0:.2f} MB"


def _iter_paths(root_path):
    matches = glob.glob(str(root_path))
    if not matches:
        matches = [str(root_path)]

    for match in sorted(matches):
        path = Path(match)
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    yield child


def _kind_for_path(path):
    parts = path.as_posix().split("/")
    if parts[0].startswith("STEP") and parts[0].endswith("_REPORT.md"):
        return "reports"
    return parts[0]


def scan_artifacts(root_paths=("logs", "outputs")) -> list[dict]:
    rows = []
    seen = set()
    for root_path in root_paths:
        for path in _iter_paths(root_path):
            rel_path = path.as_posix()
            if rel_path in seen:
                continue
            seen.add(rel_path)
            size_bytes = int(path.stat().st_size)
            size_mb = size_bytes / 1024.0 / 1024.0
            extension = path.suffix.lower()
            rows.append(
                {
                    "path": rel_path,
                    "kind": _kind_for_path(path),
                    "extension": extension,
                    "size_bytes": size_bytes,
                    "size_mb": size_mb,
                    "is_large": size_mb >= LARGE_FILE_THRESHOLD_MB,
                }
            )
    return sorted(rows, key=lambda row: row["path"])


def write_artifact_manifest(rows, csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    fieldnames = ["path", "kind", "extension", "size_bytes", "size_mb", "is_large"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})


def summarize_artifacts(rows) -> dict:
    total_size_bytes = int(sum(int(row["size_bytes"]) for row in rows))
    by_extension = {}
    for row in rows:
        extension = row["extension"] or "<none>"
        by_extension[extension] = by_extension.get(extension, 0) + int(row["size_bytes"])

    return {
        "file_count": len(rows),
        "total_size_bytes": total_size_bytes,
        "total_size_mb": total_size_bytes / 1024.0 / 1024.0,
        "large_file_count": sum(1 for row in rows if bool(row["is_large"])),
        "by_extension": dict(sorted(by_extension.items())),
    }


def write_artifact_summary(summary, json_path):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
