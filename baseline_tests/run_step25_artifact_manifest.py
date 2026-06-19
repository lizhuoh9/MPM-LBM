import os
from pathlib import Path

from step25_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
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
    summary = summarize_artifacts(rows)
    summary.update(_step25_summary(rows))
    _assert_artifact_policy(rows, summary)

    out_dir = ROOT / "outputs" / "step25_artifact_manifest"
    write_artifact_manifest(rows, out_dir / "artifact_manifest.csv")
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 25 artifact manifest finished"
    write_log(
        "logs/step25_artifact_manifest.log",
        [
            marker,
            f"file_count={summary['file_count']}",
            f"total_size_mb={summary['total_size_mb']:.6f}",
            f"large_file_count={summary['large_file_count']}",
            f"step25_total_size_mb={summary['step25_total_size_mb']:.6f}",
        ],
    )
    print(f"file_count={summary['file_count']}")
    print(f"total_size_mb={summary['total_size_mb']:.6f}")
    print(marker)


def _step25_summary(rows):
    step25_rows = [
        row
        for row in rows
        if row["path"].startswith("outputs/step25")
        or row["path"].startswith("logs/step25")
        or row["path"].startswith("STEP25_")
    ]
    step25_size = sum(int(row["size_bytes"]) for row in step25_rows)
    candidate_raw_rows = [
        row
        for row in rows
        if row["path"].startswith("data/real_geometry_candidates/")
        and not row["path"].endswith("README.md")
        and not row["path"].endswith(".gitkeep")
        and not row["path"].endswith("_descriptor.json")
    ]
    return {
        "step25_file_count": len(step25_rows),
        "step25_total_size_bytes": int(step25_size),
        "step25_total_size_mb": step25_size / 1024.0 / 1024.0,
        "step25_vtr_count": sum(1 for row in step25_rows if row["path"].endswith(".vtr")),
        "step25_particle_npy_count": sum(
            1 for row in step25_rows if row["path"].endswith(".npy") and "particle" in row["path"].lower()
        ),
        "raw_candidate_large_file_count": sum(1 for row in candidate_raw_rows if int(row["size_bytes"]) >= 1_000_000),
        "scan_data_file_count": sum(1 for row in rows if "scan" in Path(row["path"]).name.lower()),
        "step25_descriptor_count": sum(1 for row in rows if row["path"].startswith("configs/step25_candidate")),
        "step25_policy_doc_count": sum(
            1
            for row in rows
            if row["path"] in {"docs/24_controlled_real_geometry_intake.md", "docs/25_real_geometry_candidate_policy.md"}
        ),
    }


def _assert_artifact_policy(rows, summary):
    if summary["large_file_count"] != 0:
        raise RuntimeError(f"artifact manifest found large files: {summary['large_file_count']}")
    if float(summary["step25_total_size_mb"]) >= 10.0:
        raise RuntimeError(f"Step 25 output size exceeds 10 MB: {summary['step25_total_size_mb']:.6f}")
    if float(summary["total_size_mb"]) >= 160.0:
        raise RuntimeError(f"repo artifact summary exceeds 160 MB: {summary['total_size_mb']:.6f}")
    if int(summary["raw_candidate_large_file_count"]) != 0:
        raise RuntimeError("raw candidate directory contains committed large files")
    if int(summary["step25_vtr_count"]) != 0:
        raise RuntimeError("Step 25 wrote forbidden .vtr outputs")
    if int(summary["step25_particle_npy_count"]) != 0:
        raise RuntimeError("Step 25 wrote forbidden particle .npy outputs")
    if int(summary["step25_descriptor_count"]) < 2:
        raise RuntimeError("Step 25 descriptor files are missing from artifact scan")
    if int(summary["step25_policy_doc_count"]) < 2:
        raise RuntimeError("Step 25 policy docs are missing from artifact scan")


if __name__ == "__main__":
    main()
