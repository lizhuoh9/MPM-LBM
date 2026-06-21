import os

from step49_common import ROOT, summary_rows, twenty_step_envelope_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_diagnostics import summarize_twenty_step_envelope_quality

    summary = summarize_twenty_step_envelope_quality(twenty_step_envelope_rows())
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 49 twenty-step envelope quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_20step_envelope_quality"
    rows = summary_rows(summary)
    write_csv_rows(out_dir / "twenty_step_envelope_quality.csv", rows, ["metric", "value"])
    write_json(out_dir / "twenty_step_envelope_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 49 20-step envelope quality finished"
    write_log("logs/step49_20step_envelope_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
