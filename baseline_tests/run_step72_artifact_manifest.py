import os
from pathlib import Path

from step72_common import ROOT, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step72_related"]
SUMMARY_FIELDS = ["metric", "value"]
LARGE_FILE_THRESHOLD_BYTES = 5 * 1024 * 1024


def main():
    os.chdir(ROOT)
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    related_rows = [row for row in rows if row["step72_related"]]
    forbidden_driver_dirs = [
        ROOT / "outputs" / "step72_driver_runs",
        ROOT / "outputs" / "step72_runtime_geometry_driver_runs",
    ]
    summary = {
        "file_count": len(rows),
        "step72_file_count": len(related_rows),
        "step72_total_size_bytes": sum(int(row["size_bytes"]) for row in related_rows),
        "step72_total_size_mb": sum(int(row["size_bytes"]) for row in related_rows) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in related_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step72_vtr_count": sum(1 for row in related_rows if row["extension"] == ".vtr"),
        "step72_particle_npy_count": sum(1 for row in related_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "protected_external_taichi_lbm3d_step72_file_count": sum(1 for row in related_rows if row["path"].startswith("external/taichi_LBM3D/")),
        "protected_real_geometry_candidates_step72_file_count": sum(1 for row in related_rows if row["path"].startswith("data/real_geometry_candidates/")),
        "step72_driver_run_output_dir_count": sum(1 for path in forbidden_driver_dirs if path.exists()),
        "artifact_budget_pass": False,
    }
    summary["artifact_budget_pass"] = bool(
        summary["step72_total_size_mb"] < 20.0
        and summary["large_file_count"] == 0
        and summary["step72_vtr_count"] == 0
        and summary["step72_particle_npy_count"] == 0
        and summary["protected_external_taichi_lbm3d_step72_file_count"] == 0
        and summary["protected_real_geometry_candidates_step72_file_count"] == 0
        and summary["step72_driver_run_output_dir_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 72 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step72_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 72 artifact manifest finished"
    write_log("logs/step72_artifact_manifest.log", [marker, f"step72_file_count={summary['step72_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step72_artifact_manifest/"):
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "extension": path.suffix.lower(),
        "step72_related": is_step72_related(rel),
    }


def is_step72_related(path: str) -> bool:
    lower = path.lower()
    return (
        "step72" in lower
        or "runtime_geometry_activation_readiness" in lower
        or lower in {
            "readme.md",
            "docs/00_project_status.md",
            "docs/activation_preconditions.md",
            "docs/runtime_geometry_activation_readiness.md",
            "docs/72_runtime_geometry_activation_readiness_audit.md",
            "step72_runtime_geometry_activation_readiness_audit_goal.md",
            "step72_runtime_geometry_activation_readiness_audit_report.md",
        }
    )


if __name__ == "__main__":
    main()
