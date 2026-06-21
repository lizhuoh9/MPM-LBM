from __future__ import annotations

from pathlib import Path


LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def build_step54_artifact_manifest(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = [manifest_row(root, path) for path in repo_files(root)]
    step54_rows = [row for row in rows if row["step54_related"]]
    summary = {
        "file_count": len(rows),
        "step54_file_count": len(step54_rows),
        "total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "total_size_mb": sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0),
        "step54_total_size_bytes": sum(int(row["size_bytes"]) for row in step54_rows),
        "step54_total_size_mb": sum(int(row["size_bytes"]) for row in step54_rows) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step54_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step54_vtr_count": sum(1 for row in step54_rows if row["extension"] == ".vtr"),
        "step54_particle_npy_count": sum(1 for row in step54_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "step54_displaced_particle_output_count": sum(1 for row in step54_rows if "displaced_particle" in row["path"].lower()),
        "step54_dense_displacement_output_count": sum(1 for row in step54_rows if "dense_displacement" in row["path"].lower()),
        "private_absolute_path_count": private_absolute_path_count(root, rows),
        "protected_external_taichi_lbm3d_step54_file_count": sum(1 for row in step54_rows if row["path"].startswith("external/taichi_LBM3D/")),
        "protected_real_geometry_candidates_step54_file_count": sum(1 for row in step54_rows if row["path"].startswith("data/real_geometry_candidates/")),
    }
    summary["artifact_budget_pass"] = bool(
        int(summary["large_file_count"]) == 0
        and float(summary["step54_total_size_mb"]) < 5.0
        and int(summary["step54_vtr_count"]) == 0
        and int(summary["step54_particle_npy_count"]) == 0
        and int(summary["step54_displaced_particle_output_count"]) == 0
        and int(summary["step54_dense_displacement_output_count"]) == 0
        and int(summary["private_absolute_path_count"]) == 0
        and int(summary["protected_external_taichi_lbm3d_step54_file_count"]) == 0
        and int(summary["protected_real_geometry_candidates_step54_file_count"]) == 0
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
        "step54_related": is_step54_related(rel),
    }


def is_step54_related(path: str) -> bool:
    lower = path.lower()
    return (
        "step54" in lower
        or lower.startswith("docs/54_")
        or lower in {
            "docs/repository_evidence_index.md",
            "docs/repository_evidence_integrity_errata.md",
            "src/lbm_relaxation_semantics.py",
            "src/proxy_diagnostic_truthfulness.py",
            "src/state_guard_truthfulness.py",
            "src/repository_evidence_index.py",
            "src/repository_test_strength_audit.py",
            "src/repository_evidence_integrity_claim_guard.py",
            "src/repository_evidence_integrity_artifact_manifest.py",
            "src/repository_evidence_integrity_regression_guard.py",
        }
    )


def private_absolute_path_count(root: Path, rows: list[dict]) -> int:
    count = 0
    windows_user_marker = "C:" + "\\Users\\"
    slash_user_marker = "C:" + "/Users/"
    for row in rows:
        path = root / row["path"]
        if path.suffix.lower() not in {".py", ".json", ".csv", ".md", ".log", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if windows_user_marker in text or slash_user_marker in text:
            count += 1
    return count
