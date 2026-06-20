import os
from pathlib import Path

from step28_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.artifact_utils import scan_artifacts, summarize_artifacts, write_artifact_manifest


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows = scan_artifacts(
        root_paths=[
            "logs",
            "outputs",
            "STEP*_REPORT.md",
            "STEP*_GOAL.md",
            "docs",
            "paper",
            "configs",
            "data/geometry_fixtures",
            "data/real_geometry_candidates",
            "tests",
            "src",
        ]
    )
    rows = [row for row in rows if not row["path"].startswith("outputs/step28_artifact_manifest/")]
    summary = summarize_artifacts(rows)
    summary.update(step28_summary(rows))
    assert_artifact_policy(summary)

    out_dir = ROOT / "outputs" / "step28_artifact_manifest"
    write_artifact_manifest(rows, out_dir / "artifact_manifest.csv")
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 28 artifact manifest finished"
    write_log(
        "logs/step28_artifact_manifest.log",
        [
            marker,
            f"file_count={summary['file_count']}",
            f"total_size_mb={summary['total_size_mb']:.6f}",
            f"large_file_count={summary['large_file_count']}",
            f"step28_total_size_mb={summary['step28_total_size_mb']:.6f}",
        ],
    )
    print(f"file_count={summary['file_count']}")
    print(f"total_size_mb={summary['total_size_mb']:.6f}")
    print(marker)


def step28_summary(rows):
    step28_rows = [
        row
        for row in rows
        if row["path"].startswith("outputs/step28")
        or row["path"].startswith("logs/step28")
        or row["path"].startswith("configs/step28")
        or row["path"].startswith("STEP28_")
        or row["path"].startswith("docs/28_")
        or row["path"].startswith("baseline_tests/run_step28")
        or row["path"].startswith("baseline_tests/step28")
        or row["path"].startswith("tests/test_step28")
    ]
    step28_size = sum(int(row["size_bytes"]) for row in step28_rows)
    candidate_raw_rows = [
        row
        for row in rows
        if row["path"].startswith("data/real_geometry_candidates/")
        and not row["path"].endswith("README.md")
        and not row["path"].endswith(".gitkeep")
        and not row["path"].endswith("_descriptor.json")
    ]
    return {
        "step28_file_count": len(step28_rows),
        "step28_total_size_bytes": int(step28_size),
        "step28_total_size_mb": step28_size / 1024.0 / 1024.0,
        "step28_vtr_count": sum(1 for row in step28_rows if row["path"].endswith(".vtr")),
        "step28_particle_npy_count": sum(
            1 for row in step28_rows if row["path"].endswith(".npy") and "particle" in row["path"].lower()
        ),
        "step28_quality_report_count": sum(
            1 for row in step28_rows if row["path"].endswith("geometry_quality_report.json")
        ),
        "step28_driver_config_count": sum(1 for row in rows if row["path"].startswith("configs/step28_compare")),
        "raw_candidate_large_file_count": sum(1 for row in candidate_raw_rows if int(row["size_bytes"]) >= 1_000_000),
        "scan_data_file_count": sum(1 for row in rows if "scan" in Path(row["path"]).name.lower()),
        "private_absolute_path_count": sum(1 for row in rows if file_contains_private_path(row["path"])),
    }


def assert_artifact_policy(summary):
    if int(summary["large_file_count"]) != 0:
        raise RuntimeError(f"artifact manifest found large files: {summary['large_file_count']}")
    if float(summary["step28_total_size_mb"]) >= 15.0:
        raise RuntimeError(f"Step 28 output size exceeds 15 MB: {summary['step28_total_size_mb']:.6f}")
    if float(summary["total_size_mb"]) >= 165.0:
        raise RuntimeError(f"repo artifact summary exceeds 165 MB: {summary['total_size_mb']:.6f}")
    if int(summary["raw_candidate_large_file_count"]) != 0:
        raise RuntimeError("raw candidate directory contains committed large files")
    if int(summary["scan_data_file_count"]) != 0:
        raise RuntimeError("scan data files are present in scanned artifacts")
    if int(summary["step28_vtr_count"]) != 0:
        raise RuntimeError("Step 28 wrote forbidden .vtr outputs")
    if int(summary["step28_particle_npy_count"]) != 0:
        raise RuntimeError("Step 28 wrote forbidden particle .npy outputs")
    if int(summary["step28_quality_report_count"]) != 4:
        raise RuntimeError(f"Step 28 must have 4 quality reports: {summary}")
    if int(summary["private_absolute_path_count"]) != 0:
        raise RuntimeError(f"private absolute paths found in committed artifacts: {summary}")


def file_contains_private_path(relative_path):
    path = ROOT / relative_path
    if path.suffix.lower() not in {".csv", ".json", ".md", ".log"}:
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return "C:\\Users\\" in text or "\\Users\\lizhu\\" in text


if __name__ == "__main__":
    main()
