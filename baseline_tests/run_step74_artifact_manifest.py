import os
import re
from pathlib import Path

from step74_common import ROOT, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step74_related"]
SUMMARY_FIELDS = ["metric", "value"]
LARGE_FILE_THRESHOLD_BYTES = 5 * 1024 * 1024
PRIVATE_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+")
RAW_GEOMETRY_EXTENSIONS = {".stl", ".obj", ".ply", ".vtk", ".vtu", ".vtr", ".npy", ".npz"}


def main():
    os.chdir(ROOT)
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    related_rows = [row for row in rows if row["step74_related"]]
    forbidden_driver_dirs = [
        ROOT / "outputs" / "step74_driver_runs",
        ROOT / "outputs" / "step74_real_geometry_driver_runs",
        ROOT / "outputs" / "step74_projection_smoke",
    ]
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in related_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step74_file_count": sum(
            1 for row in related_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step74_file_count": sum(
            1 for row in related_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "raw_geometry_file_count": sum(
            1 for row in related_rows if row["extension"] in RAW_GEOMETRY_EXTENSIONS and not row["path"].endswith(".txt")
        ),
        "step74_driver_run_output_dir_count": sum(1 for path in forbidden_driver_dirs if path.exists()),
        "step74_file_count": len(related_rows),
        "step74_particle_npy_count": sum(
            1 for row in related_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step74_total_size_bytes": sum(int(row["size_bytes"]) for row in related_rows),
        "step74_total_size_mb": sum(int(row["size_bytes"]) for row in related_rows) / (1024.0 * 1024.0),
        "step74_vtr_count": sum(1 for row in related_rows if row["extension"] == ".vtr"),
        "synthetic_fixture_count": sum(
            1 for row in related_rows if row["path"] == "outputs/step74_synthetic_geometry_fixture/synthetic_fixture.txt"
        ),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step74_total_size_mb"] < 20.0
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step74_file_count"] == 0
        and summary["protected_real_geometry_candidates_step74_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step74_driver_run_output_dir_count"] == 0
        and summary["step74_particle_npy_count"] == 0
        and summary["step74_vtr_count"] == 0
        and summary["synthetic_fixture_count"] <= 1
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 74 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step74_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 74 artifact manifest finished"
    write_log("logs/step74_artifact_manifest.log", [marker, f"step74_file_count={summary['step74_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step74_artifact_manifest/"):
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
        "step74_related": is_step74_related(rel),
    }


def is_step74_related(path: str) -> bool:
    lower = path.lower()
    return (
        "step74" in lower
        or "real_geometry_data_boundary" in lower
        or lower
        in {
            "readme.md",
            "docs/00_project_status.md",
            "docs/activation_preconditions.md",
            "docs/real_geometry_data_boundary.md",
            "docs/real_geometry_candidate_policy.md",
            "docs/74_real_geometry_data_boundary_audit.md",
            "step74_real_geometry_data_boundary_audit_goal.md",
            "step74_real_geometry_data_boundary_audit_report.md",
        }
    )


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step74_", "logs/step74_")):
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
