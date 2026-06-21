import os

from step47_common import ROOT, short_step_envelope_rows, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_envelope_diagnostics import summarize_short_step_envelope_quality

    summary = summarize_short_step_envelope_quality(short_step_envelope_rows())
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 47 short-step envelope quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step47_short_step_envelope_quality"
    rows = summary_rows(summary)
    write_csv_rows(out_dir / "short_step_envelope_quality.csv", rows, ["metric", "value"])
    write_json(out_dir / "short_step_envelope_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 47 short-step envelope quality finished"
    write_log("logs/step47_short_step_envelope_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
