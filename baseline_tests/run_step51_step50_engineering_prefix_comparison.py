import os

from step51_common import ROOT, read_json, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import compare_step50_engineering_prefix

    step50_rows = read_json("outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json")["rows"]
    step51_rows = transfer_comparison_rows()
    comparison_rows, summary = compare_step50_engineering_prefix(step50_rows, step51_rows)
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 51 Step 50 engineering prefix comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_step50_engineering_prefix_comparison"
    write_csv_rows(out_dir / "step50_engineering_comparison.csv", comparison_rows)
    write_json(out_dir / "step50_engineering_comparison.json", {"summary": summary, "rows": comparison_rows})
    marker = "[OK] Step 51 Step 50 engineering prefix comparison finished"
    write_log("logs/step51_step50_engineering_prefix_comparison.log", [marker, f"engineering_row_pair_count={summary['engineering_row_pair_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
