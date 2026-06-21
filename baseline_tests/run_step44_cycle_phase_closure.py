import os

from step44_common import STEP44_CONFIG_PATH, ROOT, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_update import compute_runtime_displaced_copy_rows, cycle_phase_closure_rows, summarize_cycle_phase_closure
    from src.diagnostic_geometry_update_config import DiagnosticGeometryUpdateConfig

    config = DiagnosticGeometryUpdateConfig.from_json(STEP44_CONFIG_PATH)
    runtime = compute_runtime_displaced_copy_rows(STEP44_CONFIG_PATH)
    rows = cycle_phase_closure_rows(runtime, config)
    summary = summarize_cycle_phase_closure(rows, config)
    if not summary["closure_pass"]:
        raise RuntimeError(f"Step 44 cycle phase closure failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_cycle_phase_closure"
    write_csv_rows(out_dir / "cycle_phase_closure.csv", rows)
    write_json(out_dir / "cycle_phase_closure.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 44 cycle phase closure finished"
    write_log("logs/step44_cycle_phase_closure.log", [marker, f"row_count={summary['row_count']}", f"closure_pass={summary['closure_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
