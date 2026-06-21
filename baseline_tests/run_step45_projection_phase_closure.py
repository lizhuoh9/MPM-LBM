import os

from step45_common import ROOT, STEP45_CONFIG_PATH, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection import compute_runtime_projection_rows
    from src.runtime_geometry_projection_consistency import projection_phase_closure_rows, summarize_projection_phase_closure

    runtime_rows = compute_runtime_projection_rows(STEP45_CONFIG_PATH)
    rows = projection_phase_closure_rows(runtime_rows)
    summary = summarize_projection_phase_closure(rows)
    if not summary["closure_pass"]:
        raise RuntimeError(f"Step 45 projection phase closure failed: {summary}")
    out_dir = ROOT / "outputs" / "step45_projection_phase_closure"
    write_csv_rows(out_dir / "projection_phase_closure.csv", rows)
    write_json(out_dir / "projection_phase_closure.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 45 projection phase closure finished"
    write_log("logs/step45_projection_phase_closure.log", [marker, f"row_count={summary['row_count']}", f"closure_pass={summary['closure_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
