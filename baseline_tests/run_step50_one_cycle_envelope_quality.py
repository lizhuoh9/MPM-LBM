import os

from step50_common import ROOT, one_cycle_closure_rows, one_cycle_envelope_rows, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import summarize_one_cycle_envelope_quality

    rows = one_cycle_envelope_rows()
    closure_rows = one_cycle_closure_rows()
    summary = summarize_one_cycle_envelope_quality(rows, closure_rows)
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 50 one-cycle envelope quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_one_cycle_envelope_quality"
    write_csv_rows(out_dir / "one_cycle_envelope_quality.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "one_cycle_envelope_quality.json", {"summary": summary})
    marker = "[OK] Step 50 one-cycle envelope quality finished"
    write_log("logs/step50_one_cycle_envelope_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
