import os

from step52_common import ROOT, closure_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_48_feasibility_diagnostics import summarize_48_cycle_closure

    rows = closure_rows()
    rows, summary = summarize_48_cycle_closure(rows)
    if not summary["closure_pass"]:
        raise RuntimeError(f"Step 52 cycle closure failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_cycle_closure"
    write_csv_rows(out_dir / "cycle_closure.csv", rows)
    write_json(out_dir / "cycle_closure.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 52 cycle closure finished"
    write_log("logs/step52_cycle_closure.log", [marker, f"row_count={summary['row_count']}", f"closure_pass={summary['closure_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
