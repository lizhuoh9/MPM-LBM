import os
import re
from pathlib import Path

from step84_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step84_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step84_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step84_rows = [row for row in rows if row["step84_related"]]
    required_dir = ROOT / policy["required_driver_run_dir"]
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in step84_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step84_file_count": sum(
            1 for row in step84_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step84_file_count": sum(
            1 for row in step84_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "raw_geometry_file_count": sum(1 for row in step84_rows if row["extension"] in set(policy["raw_geometry_extensions"])),
        "step84_file_count": len(step84_rows),
        "step84_optional_driver_run_dir_count": len(step84_optional_driver_run_dirs(ROOT, required_dir)),
        "step84_particle_npy_count": sum(
            1 for row in step84_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step84_required_driver_run_dir_count": int(required_dir.is_dir()),
        "step84_total_size_bytes": sum(int(row["size_bytes"]) for row in step84_rows),
        "step84_total_size_mb": sum(int(row["size_bytes"]) for row in step84_rows) / (1024.0 * 1024.0),
        "step84_vtr_count": sum(1 for row in step84_rows if row["extension"] == ".vtr"),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step84_file_count"] <= int(policy["max_step84_file_count"])
        and summary["step84_total_size_mb"] < float(policy["max_step84_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step84_file_count"] == 0
        and summary["protected_real_geometry_candidates_step84_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step84_required_driver_run_dir_count"] == 1
        and summary["step84_optional_driver_run_dir_count"] == 0
        and summary["step84_particle_npy_count"] == 0
        and summary["step84_vtr_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step84 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step84_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step84 artifact manifest finished"
    write_log("logs/step84_artifact_manifest.log", [marker, f"step84_file_count={summary['step84_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step84_artifact_manifest/"):
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
        "step84_related": is_step84_related(rel),
    }


def is_step84_related(path: str) -> bool:
    lower = path.lower()
    return (
        "step84" in lower
        or "runtime_geometry_wall_velocity_combined_canonical_driver_smoke" in lower
        or lower
        in {
            "readme.md",
            "docs/00_project_status.md",
            "docs/activation_preconditions.md",
            "docs/post_gate_simulation_campaign_plan.md",
            "docs/post_gate_simulation_campaign_status.md",
            "docs/84_runtime_geometry_wall_velocity_combined_canonical_driver_smoke.md",
            "step84_runtime_geometry_wall_velocity_combined_canonical_driver_smoke_goal.md",
            "step84_runtime_geometry_wall_velocity_combined_canonical_driver_smoke_report.md",
        }
    )


def step84_optional_driver_run_dirs(root: Path, required_dir: Path) -> list[Path]:
    run_root = root / "outputs" / "step84_driver_runs"
    if not run_root.exists():
        return []
    return [path for path in run_root.iterdir() if path.is_dir() and path.resolve() != required_dir.resolve()]


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step84_", "logs/step84_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
