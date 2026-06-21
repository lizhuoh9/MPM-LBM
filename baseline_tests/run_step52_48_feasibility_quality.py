import os

from step52_common import ROOT, closure_rows, feasibility_rows, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_48_feasibility_diagnostics import summarize_48_feasibility_quality

    rows = feasibility_rows()
    closures = closure_rows()
    summary = summarize_48_feasibility_quality(rows, closures)
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 52 48 feasibility quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_48_feasibility_quality"
    write_csv_rows(out_dir / "feasibility_quality.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "feasibility_quality.json", {"summary": summary})
    marker = "[OK] Step 52 48 feasibility quality finished"
    write_log("logs/step52_48_feasibility_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
