import os

from step54_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.repository_evidence_integrity_artifact_manifest import build_step54_artifact_manifest


FIELDS = ["path", "size_bytes", "extension", "step54_related"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_step54_artifact_manifest(ROOT)
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 54 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step54_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 54 artifact manifest finished"
    write_log("logs/step54_artifact_manifest.log", [marker, f"step54_file_count={summary['step54_file_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
