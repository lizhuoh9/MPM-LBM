import os
from pathlib import Path

from step61_common import ROOT, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step61_related"]
SUMMARY_FIELDS = ["metric", "value"]
LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def main():
    os.chdir(ROOT)
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step61_rows = [row for row in rows if row["step61_related"]]
    summary = {
        "file_count": len(rows),
        "step61_file_count": len(step61_rows),
        "step61_total_size_bytes": sum(int(row["size_bytes"]) for row in step61_rows),
        "step61_total_size_mb": sum(int(row["size_bytes"]) for row in step61_rows) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step61_rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step61_vtr_count": sum(1 for row in step61_rows if row["extension"] == ".vtr"),
        "step61_particle_npy_count": sum(1 for row in step61_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "protected_external_taichi_lbm3d_step61_file_count": sum(1 for row in step61_rows if row["path"].startswith("external/taichi_LBM3D/")),
        "protected_real_geometry_candidates_step61_file_count": sum(1 for row in step61_rows if row["path"].startswith("data/real_geometry_candidates/")),
        "artifact_budget_pass": False,
    }
    summary["artifact_budget_pass"] = bool(
        summary["step61_total_size_mb"] < 20.0
        and summary["large_file_count"] == 0
        and summary["step61_vtr_count"] == 0
        and summary["step61_particle_npy_count"] == 0
        and summary["protected_external_taichi_lbm3d_step61_file_count"] == 0
        and summary["protected_real_geometry_candidates_step61_file_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 61 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step61_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 61 artifact manifest finished"
    write_log("logs/step61_artifact_manifest.log", [marker, f"step61_file_count={summary['step61_file_count']}"])
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
        "step61_related": is_step61_related(rel),
    }


def is_step61_related(path: str) -> bool:
    lower = path.lower()
    return "step61" in lower or lower.startswith("docs/61_")


if __name__ == "__main__":
    main()
