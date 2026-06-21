import os
from pathlib import Path

from step58_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step58_related"]
SUMMARY_FIELDS = ["metric", "value"]
LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def main():
    os.chdir(ROOT)
    related_paths = step58_related_paths()
    rows = [manifest_row(path, related_paths) for path in repo_files(ROOT)]
    step58_rows = [row for row in rows if row["step58_related"]]
    summary = {
        "file_count": len(rows),
        "step58_file_count": len(step58_rows),
        "step58_total_size_bytes": sum(int(row["size_bytes"]) for row in step58_rows),
        "step58_total_size_mb": sum(int(row["size_bytes"]) for row in step58_rows) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step58_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step58_vtr_count": sum(1 for row in step58_rows if row["extension"] == ".vtr"),
        "step58_particle_npy_count": sum(1 for row in step58_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "protected_external_taichi_lbm3d_step58_file_count": sum(1 for row in step58_rows if row["path"].startswith("external/taichi_LBM3D/")),
        "protected_real_geometry_candidates_step58_file_count": sum(1 for row in step58_rows if row["path"].startswith("data/real_geometry_candidates/")),
        "artifact_budget_pass": False,
    }
    summary["artifact_budget_pass"] = bool(
        summary["step58_total_size_mb"] < 5.0
        and summary["large_file_count"] == 0
        and summary["step58_vtr_count"] == 0
        and summary["step58_particle_npy_count"] == 0
        and summary["protected_external_taichi_lbm3d_step58_file_count"] == 0
        and summary["protected_real_geometry_candidates_step58_file_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 58 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step58_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 58 artifact manifest finished"
    write_log("logs/step58_artifact_manifest.log", [marker, f"step58_file_count={summary['step58_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path, related_paths: set[str]):
    rel = path.relative_to(ROOT).as_posix()
    return {
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "extension": path.suffix.lower(),
        "step58_related": is_step58_related(rel, related_paths),
    }


def is_step58_related(path: str, related_paths: set[str]) -> bool:
    lower = path.lower()
    return (
        "step58" in lower
        or lower.startswith("docs/58_")
        or path in related_paths
    )


def step58_related_paths() -> set[str]:
    migration = read_json("configs/step58_fsidriver_migration_policy.json")["migration"]
    bridge_policy = read_json("configs/step58_optional_bridge_policy.json")
    paths = {
        "src/__init__.py",
        "src/mpm_lbm/sim/motion/__init__.py",
        "src/mpm_lbm/sim/wall_velocity/__init__.py",
        migration["canonical_path"],
        migration["legacy_path"],
    }
    for bridge in bridge_policy["bridges"]:
        paths.add(bridge["canonical_path"])
    return paths


if __name__ == "__main__":
    main()
