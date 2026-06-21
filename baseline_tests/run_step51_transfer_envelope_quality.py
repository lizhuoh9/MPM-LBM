import os

from step51_common import ROOT, summary_rows, transfer_closure_rows, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import summarize_transfer_envelope_quality

    rows = transfer_comparison_rows()
    closure_rows = transfer_closure_rows()
    summary = summarize_transfer_envelope_quality(rows, closure_rows)
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 51 transfer envelope quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_transfer_envelope_quality"
    write_csv_rows(out_dir / "transfer_envelope_quality.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "transfer_envelope_quality.json", {"summary": summary})
    marker = "[OK] Step 51 transfer envelope quality finished"
    write_log("logs/step51_transfer_envelope_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
