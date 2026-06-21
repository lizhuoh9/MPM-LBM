import os
from pathlib import Path

from step62_common import ROOT, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step62_related"]
SUMMARY_FIELDS = ["metric", "value"]
LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def main():
    os.chdir(ROOT)
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step62_rows = [row for row in rows if row["step62_related"]]
    summary = {
        "file_count": len(rows),
        "step62_file_count": len(step62_rows),
        "step62_total_size_bytes": sum(int(row["size_bytes"]) for row in step62_rows),
        "step62_total_size_mb": sum(int(row["size_bytes"]) for row in step62_rows) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step62_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step62_vtr_count": sum(1 for row in step62_rows if row["extension"] == ".vtr"),
        "step62_particle_npy_count": sum(1 for row in step62_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "protected_external_taichi_lbm3d_step62_file_count": sum(1 for row in step62_rows if row["path"].startswith("external/taichi_LBM3D/")),
        "protected_real_geometry_candidates_step62_file_count": sum(1 for row in step62_rows if row["path"].startswith("data/real_geometry_candidates/")),
        "artifact_budget_pass": False,
    }
    summary["artifact_budget_pass"] = bool(
        summary["step62_total_size_mb"] < 20.0
        and summary["large_file_count"] == 0
        and summary["step62_vtr_count"] == 0
        and summary["step62_particle_npy_count"] == 0
        and summary["protected_external_taichi_lbm3d_step62_file_count"] == 0
        and summary["protected_real_geometry_candidates_step62_file_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 62 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step62_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 62 artifact manifest finished"
    write_log("logs/step62_artifact_manifest.log", [marker, f"step62_file_count={summary['step62_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
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
        "step62_related": is_step62_related(rel),
    }


def is_step62_related(path: str) -> bool:
    lower = path.lower()
    return "step62" in lower or lower.startswith("docs/62_")


if __name__ == "__main__":
    main()
