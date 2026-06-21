from __future__ import annotations

from pathlib import Path


LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def build_step53_artifact_manifest(root: Path) -> tuple[list[dict], dict]:
    files = list(repo_files(root))
    rows = [manifest_row(root, path) for path in files]
    step53 = [row for row in rows if row["step53_related"]]
    summary = {
        "file_count": len(rows),
        "step53_file_count": len(step53),
        "total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "total_size_mb": sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0),
        "step53_total_size_bytes": sum(int(row["size_bytes"]) for row in step53),
        "step53_total_size_mb": sum(int(row["size_bytes"]) for row in step53) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step53 if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step53_vtr_count": sum(1 for row in step53 if row["extension"] == ".vtr"),
        "step53_particle_npy_count": sum(1 for row in step53 if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "step53_displaced_particle_output_count": sum(1 for row in step53 if "displaced_particle" in row["path"].lower()),
        "step53_dense_displacement_output_count": sum(1 for row in step53 if "dense_displacement" in row["path"].lower()),
        "raw_candidate_large_file_count": sum(1 for row in rows if "real_geometry_candidates" in row["path"].lower() and int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "scan_data_file_count": sum(1 for row in rows if "scan" in row["path"].lower() and row["step53_related"]),
        "private_absolute_path_count": private_absolute_path_count(files),
        "geo_all_fluid_dat_count_added": sum(1 for row in step53 if Path(row["path"]).name.startswith("geo_all_fluid_") and row["extension"] == ".dat"),
    }
    summary["artifact_budget_pass"] = bool(
        int(summary["large_file_count"]) == 0
        and float(summary["step53_total_size_mb"]) < 5.0
        and float(summary["total_size_mb"]) < 400.0
        and int(summary["step53_vtr_count"]) == 0
        and int(summary["step53_particle_npy_count"]) == 0
        and int(summary["step53_displaced_particle_output_count"]) == 0
        and int(summary["step53_dense_displacement_output_count"]) == 0
        and int(summary["raw_candidate_large_file_count"]) == 0
        and int(summary["scan_data_file_count"]) == 0
        and int(summary["private_absolute_path_count"]) == 0
        and int(summary["geo_all_fluid_dat_count_added"]) == 0
    )
    return rows, summary


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts:
            continue
        yield path


def manifest_row(root: Path, path: Path) -> dict:
    rel = path.relative_to(root).as_posix()
    return {
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "extension": path.suffix.lower(),
        "step53_related": is_step53_related(rel),
    }


def is_step53_related(path: str) -> bool:
    lower = path.lower()
    return "step53" in lower or lower.startswith("docs/53_")


def private_absolute_path_count(files) -> int:
    count = 0
    windows_user_marker = "C:" + "\\Users\\"
    slash_user_marker = "C:" + "/Users/"
    for path in files:
        if path.suffix.lower() not in {".py", ".json", ".csv", ".md", ".log", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if windows_user_marker in text or slash_user_marker in text:
            count += 1
    return count
