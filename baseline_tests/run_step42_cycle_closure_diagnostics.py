import os

from step42_common import ROOT, make_displacement_rows, write_csv_rows, write_json, write_log
from src.geometry_displacement_consistency import CYCLE_FIELDS, assert_cycle_closure, cycle_closure_rows


def main():
    os.chdir(ROOT)
    rows, summary = cycle_closure_rows(make_displacement_rows())
    assert_cycle_closure(summary)

    out_dir = ROOT / "outputs" / "step42_cycle_closure_diagnostics"
    write_csv_rows(out_dir / "cycle_closure_diagnostics.csv", rows, CYCLE_FIELDS)
    write_json(out_dir / "cycle_closure_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 42 cycle closure diagnostics finished"
    write_log("logs/step42_cycle_closure_diagnostics.log", [marker, f"row_count={summary['row_count']}", f"cycle_closure_pass={summary['cycle_closure_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
