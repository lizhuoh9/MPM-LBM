import os

from step54_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.repository_evidence_index import build_repository_evidence_index


FIELDS = [
    "step",
    "primary_artifact",
    "primary_artifact_exists",
    "evidence_kind",
    "solver_time_integration_run",
    "record_kind",
    "scope_note",
    "claim_boundary",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_repository_evidence_index(ROOT)
    if not summary["repository_evidence_index_pass"]:
        raise RuntimeError(f"Step 54 repository evidence index failed: {summary}")
    out_dir = ROOT / "outputs" / "step54_repository_evidence_index"
    write_csv_rows(out_dir / "repository_evidence_index.csv", rows, FIELDS)
    write_csv_rows(out_dir / "repository_evidence_index_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "repository_evidence_index.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 54 repository evidence index finished"
    write_log("logs/step54_repository_evidence_index.log", [marker, f"indexed_step_count={summary['indexed_step_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
