import os
from pathlib import Path

from step57_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step57_related"]
SUMMARY_FIELDS = ["metric", "value"]
LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def main():
    os.chdir(ROOT)
    migration_paths = step57_migration_paths()
    rows = [manifest_row(path, migration_paths) for path in repo_files(ROOT)]
    step57_rows = [row for row in rows if row["step57_related"]]
    summary = {
        "file_count": len(rows),
        "step57_file_count": len(step57_rows),
        "step57_total_size_bytes": sum(int(row["size_bytes"]) for row in step57_rows),
        "step57_total_size_mb": sum(int(row["size_bytes"]) for row in step57_rows) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step57_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step57_vtr_count": sum(1 for row in step57_rows if row["extension"] == ".vtr"),
        "step57_particle_npy_count": sum(1 for row in step57_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "protected_external_taichi_lbm3d_step57_file_count": sum(1 for row in step57_rows if row["path"].startswith("external/taichi_LBM3D/")),
        "protected_real_geometry_candidates_step57_file_count": sum(1 for row in step57_rows if row["path"].startswith("data/real_geometry_candidates/")),
        "artifact_budget_pass": False,
    }
    summary["artifact_budget_pass"] = bool(
        summary["step57_total_size_mb"] < 5.0
        and summary["large_file_count"] == 0
        and summary["step57_vtr_count"] == 0
        and summary["step57_particle_npy_count"] == 0
        and summary["protected_external_taichi_lbm3d_step57_file_count"] == 0
        and summary["protected_real_geometry_candidates_step57_file_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 57 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step57_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 57 artifact manifest finished"
    write_log("logs/step57_artifact_manifest.log", [marker, f"step57_file_count={summary['step57_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path, migration_paths: set[str]):
    rel = path.relative_to(ROOT).as_posix()
    return {
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "extension": path.suffix.lower(),
        "step57_related": is_step57_related(rel, migration_paths),
    }


def is_step57_related(path: str, migration_paths: set[str]) -> bool:
    lower = path.lower()
    return (
        "step57" in lower
        or lower.startswith("docs/57_")
        or path in migration_paths
    )


def step57_migration_paths() -> set[str]:
    policy = read_json("configs/step57_driver_support_migration_policy.json")
    paths = set()
    for migration in policy["migrations"]:
        paths.add(migration["canonical_path"])
        paths.add(migration["legacy_path"])
    return paths


if __name__ == "__main__":
    main()
