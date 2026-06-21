import os

from step46_common import ROOT, coupling_smoke_rows, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_diagnostics import summarize_coupling_smoke_quality

    summary = summarize_coupling_smoke_quality(coupling_smoke_rows())
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 46 coupling smoke quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step46_coupling_smoke_quality"
    rows = summary_rows(summary)
    write_csv_rows(out_dir / "coupling_smoke_quality.csv", rows, ["metric", "value"])
    write_json(out_dir / "coupling_smoke_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 46 coupling smoke quality finished"
    write_log("logs/step46_coupling_smoke_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
