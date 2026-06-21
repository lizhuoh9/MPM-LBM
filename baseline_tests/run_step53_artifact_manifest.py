import os

from step53_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_artifact_guard import build_step53_artifact_manifest


MANIFEST_FIELDS = ["path", "size_bytes", "extension", "step53_related"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_step53_artifact_manifest(ROOT)
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 53 artifact budget failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, MANIFEST_FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 53 artifact manifest finished"
    write_log("logs/step53_artifact_manifest.log", [marker, f"file_count={summary['file_count']}", f"step53_total_size_mb={summary['step53_total_size_mb']}"])
    print(f"file_count={summary['file_count']}")
    print(marker)


if __name__ == "__main__":
    main()
