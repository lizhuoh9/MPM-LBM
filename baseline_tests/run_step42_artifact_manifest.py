import os
from pathlib import Path

from step42_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
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
            "configs",
            "tests",
            "src",
            "baseline_tests",
            "README.md",
        ]
    )
    rows = [
        row
        for row in rows
        if not row["path"].startswith("outputs/step42_artifact_manifest/")
        and "__pycache__/" not in row["path"]
        and row["extension"] != ".pyc"
    ]
    summary = summarize_artifacts(rows)
    summary.update(step42_summary(rows))
    assert_artifact_policy(summary)

    out_dir = ROOT / "outputs" / "step42_artifact_manifest"
    write_artifact_manifest(rows, out_dir / "artifact_manifest.csv")
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 42 artifact manifest finished"
    write_log("logs/step42_artifact_manifest.log", [marker, f"file_count={summary['file_count']}", f"step42_total_size_mb={summary['step42_total_size_mb']:.6f}"])
    print(f"file_count={summary['file_count']}")
    print(marker)


def step42_summary(rows):
    step42_rows = [
        row
        for row in rows
        if row["path"].startswith("outputs/step42")
        or row["path"].startswith("logs/step42")
        or row["path"].startswith("configs/step42")
        or row["path"].startswith("STEP42_")
        or row["path"].startswith("docs/42_")
        or row["path"].startswith("baseline_tests/run_step42")
        or row["path"].startswith("baseline_tests/step42")
        or row["path"].startswith("tests/test_step42")
        or row["path"].startswith("src/geometry_displacement")
    ]
    step42_size = sum(int(row["size_bytes"]) for row in step42_rows)
    candidate_raw_rows = [
        row
        for row in rows
        if row["path"].startswith("data/real_geometry_candidates/")
        and not row["path"].endswith("README.md")
        and not row["path"].endswith(".gitkeep")
        and not row["path"].endswith("_descriptor.json")
    ]
    return {
        "step42_file_count": len(step42_rows),
        "step42_total_size_bytes": int(step42_size),
        "step42_total_size_mb": step42_size / 1024.0 / 1024.0,
        "step42_vtr_count": sum(1 for row in step42_rows if row["path"].endswith(".vtr")),
        "step42_particle_npy_count": sum(1 for row in step42_rows if row["path"].endswith(".npy") and "particle" in row["path"].lower()),
        "raw_candidate_large_file_count": sum(1 for row in candidate_raw_rows if int(row["size_bytes"]) >= 1_000_000),
        "scan_data_file_count": sum(1 for row in rows if "scan" in Path(row["path"]).name.lower()),
        "private_absolute_path_count": sum(1 for row in rows if file_contains_private_path(row["path"])),
    }


def assert_artifact_policy(summary):
    if int(summary["large_file_count"]) != 0:
        raise RuntimeError(f"artifact manifest found large files: {summary['large_file_count']}")
    if float(summary["step42_total_size_mb"]) >= 5.0:
        raise RuntimeError(f"Step 42 output size exceeds 5 MB: {summary['step42_total_size_mb']:.6f}")
    if float(summary["total_size_mb"]) >= 310.0:
        raise RuntimeError(f"repo artifact summary exceeds 310 MB: {summary['total_size_mb']:.6f}")
    if int(summary["raw_candidate_large_file_count"]) != 0:
        raise RuntimeError("raw candidate directory contains committed large files")
    if int(summary["scan_data_file_count"]) != 0:
        raise RuntimeError("scan data files are present in scanned artifacts")
    if int(summary["step42_vtr_count"]) != 0:
        raise RuntimeError("Step 42 wrote forbidden .vtr outputs")
    if int(summary["step42_particle_npy_count"]) != 0:
        raise RuntimeError("Step 42 wrote forbidden particle .npy outputs")
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
