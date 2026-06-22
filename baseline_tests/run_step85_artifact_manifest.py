import os
import re
from pathlib import Path

from step85_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step85_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step85_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step85_rows = [row for row in rows if row["step85_related"]]
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in step85_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step85_file_count": sum(
            1 for row in step85_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step85_file_count": sum(
            1 for row in step85_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "raw_geometry_file_count": sum(
            1 for row in step85_rows if row["extension"] in set(policy["raw_geometry_extensions"])
        ),
        "step85_driver_run_dir_count": len(step85_driver_run_dirs(ROOT)),
        "step85_file_count": len(step85_rows),
        "step85_particle_npy_count": sum(
            1 for row in step85_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step85_total_size_bytes": sum(int(row["size_bytes"]) for row in step85_rows),
        "step85_total_size_mb": sum(int(row["size_bytes"]) for row in step85_rows) / (1024.0 * 1024.0),
        "step85_vtr_count": sum(1 for row in step85_rows if row["extension"] == ".vtr"),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step85_file_count"] <= int(policy["max_step85_file_count"])
        and summary["step85_total_size_mb"] < float(policy["max_step85_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step85_file_count"] == 0
        and summary["protected_real_geometry_candidates_step85_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step85_driver_run_dir_count"] == 0
        and summary["step85_particle_npy_count"] == 0
        and summary["step85_vtr_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step85 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step85_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step85 artifact manifest finished"
    write_log("logs/step85_artifact_manifest.log", [marker, f"step85_file_count={summary['step85_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step85_artifact_manifest/"):
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
        "step85_related": is_step85_related(rel),
    }


def is_step85_related(path: str) -> bool:
    lower = path.lower()
    return (
        "step85" in lower
        or "squid_proxy_static_geometry_activation_plan_and_guard" in lower
        or lower
        in {
            "readme.md",
            "docs/00_project_status.md",
            "docs/85_squid_proxy_static_geometry_activation_plan_and_guard.md",
            "docs/activation_preconditions.md",
            "docs/post_gate_simulation_campaign_plan.md",
            "docs/post_gate_simulation_campaign_status.md",
            "step85_squid_proxy_static_geometry_activation_plan_and_guard_goal.md",
            "step85_squid_proxy_static_geometry_activation_plan_and_guard_report.md",
        }
    )


def step85_driver_run_dirs(root: Path) -> list[Path]:
    run_root = root / "outputs" / "step85_driver_runs"
    if not run_root.exists():
        return []
    return [path for path in run_root.iterdir() if path.is_dir()]


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step85_", "logs/step85_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
