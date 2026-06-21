import os

from step48_common import ROOT, summary_rows, ten_step_envelope_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_10step_diagnostics import summarize_ten_step_envelope_quality

    summary = summarize_ten_step_envelope_quality(ten_step_envelope_rows())
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 48 ten-step envelope quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step48_10step_envelope_quality"
    rows = summary_rows(summary)
    write_csv_rows(out_dir / "ten_step_envelope_quality.csv", rows, ["metric", "value"])
    write_json(out_dir / "ten_step_envelope_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 48 10-step envelope quality finished"
    write_log("logs/step48_10step_envelope_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
