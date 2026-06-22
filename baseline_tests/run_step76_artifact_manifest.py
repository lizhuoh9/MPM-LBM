import os
import re
from pathlib import Path

from step76_common import ROOT, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step76_related"]
LARGE_FILE_THRESHOLD_BYTES = 5 * 1024 * 1024
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")
RAW_GEOMETRY_EXTENSIONS = {".stl", ".obj", ".ply", ".vtk", ".vtu"}


def main():
    os.chdir(ROOT)
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step76_rows = [row for row in rows if row["step76_related"]]
    required_dir = ROOT / "outputs" / "step76_driver_runs" / "canonical_driver_moving_boundary_engineering_32_1step_rebaseline"
    optional_dir = ROOT / "outputs" / "step76_driver_runs" / "canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional"
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in step76_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step76_file_count": sum(
            1 for row in step76_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step76_file_count": sum(
            1 for row in step76_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "raw_geometry_file_count": sum(1 for row in step76_rows if row["extension"] in RAW_GEOMETRY_EXTENSIONS),
        "step76_file_count": len(step76_rows),
        "step76_optional_driver_run_dir_count": int(optional_dir.exists()),
        "step76_particle_npy_count": sum(
            1 for row in step76_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step76_required_driver_run_dir_count": int(required_dir.is_dir()),
        "step76_total_size_bytes": sum(int(row["size_bytes"]) for row in step76_rows),
        "step76_total_size_mb": sum(int(row["size_bytes"]) for row in step76_rows) / (1024.0 * 1024.0),
        "step76_vtr_count": sum(1 for row in step76_rows if row["extension"] == ".vtr"),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step76_total_size_mb"] < 20.0
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step76_file_count"] == 0
        and summary["protected_real_geometry_candidates_step76_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step76_required_driver_run_dir_count"] == 1
        and summary["step76_optional_driver_run_dir_count"] == 0
        and summary["step76_particle_npy_count"] == 0
        and summary["step76_vtr_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step76 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step76_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step76 artifact manifest finished"
    write_log("logs/step76_artifact_manifest.log", [marker, f"step76_file_count={summary['step76_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step76_artifact_manifest/"):
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
        "step76_related": is_step76_related(rel),
    }


def is_step76_related(path: str) -> bool:
    lower = path.lower()
    return (
        "step76" in lower
        or "post_gate_rebaseline" in lower
        or "post_gate_simulation_campaign_status" in lower
        or lower
        in {
            "readme.md",
            "docs/00_project_status.md",
            "docs/activation_preconditions.md",
            "docs/post_gate_simulation_campaign_plan.md",
            "docs/76_minimal_post_gate_canonical_driver_rebaseline.md",
            "docs/post_gate_simulation_campaign_status.md",
            "step76_minimal_post_gate_canonical_driver_rebaseline_goal.md",
            "step76_minimal_post_gate_canonical_driver_rebaseline_report.md",
        }
    )


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step76_", "logs/step76_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
