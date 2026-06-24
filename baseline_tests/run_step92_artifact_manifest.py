import os
import re
from pathlib import Path

from step92_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step92_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step92_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step92_rows = [row for row in rows if row["step92_related"]]
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(
            1 for row in step92_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step92_file_count": sum(
            1 for row in step92_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step92_file_count": sum(
            1 for row in step92_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "raw_geometry_file_count": sum(
            1 for row in step92_rows if row["extension"] in set(policy["raw_geometry_extensions"])
        ),
        "step92_file_count": len(step92_rows),
        "step92_particle_npy_count": sum(
            1 for row in step92_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step92_required_driver_run_dir_count": len(step92_required_driver_run_dirs(ROOT)),
        "step92_total_size_bytes": sum(int(row["size_bytes"]) for row in step92_rows),
        "step92_total_size_mb": sum(int(row["size_bytes"]) for row in step92_rows) / (1024.0 * 1024.0),
        "step92_vtr_count": sum(1 for row in step92_rows if row["extension"] == ".vtr"),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step92_file_count"] <= int(policy["max_step92_file_count"])
        and summary["step92_total_size_mb"] < float(policy["max_step92_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step92_file_count"] == 0
        and summary["protected_real_geometry_candidates_step92_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step92_required_driver_run_dir_count"] == 1
        and summary["step92_particle_npy_count"] == 0
        and summary["step92_vtr_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step92 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step92_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step92 artifact manifest finished"
    write_log("logs/step92_artifact_manifest.log", [marker, f"step92_file_count={summary['step92_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step92_artifact_manifest/"):
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {
        "extension": path.suffix.lower(),
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "step92_related": is_step92_related(rel),
    }


def is_step92_related(path: str) -> bool:
    lower = path.lower()
    return "step92" in lower or lower in {
        "docs/92_first_user_simulation_10step_dry_run.md",
    }


def step92_required_driver_run_dirs(root: Path) -> list[Path]:
    run_root = root / "outputs" / "step92_driver_runs"
    if not run_root.exists():
        return []
    required = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run"
    return [path for path in run_root.iterdir() if path.is_dir() and path.name == required]


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step92_", "logs/step92_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
