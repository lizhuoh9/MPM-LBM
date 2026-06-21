import os

from step49_common import ROOT, read_json, twenty_step_envelope_rows, write_csv_rows, write_json, write_log


PREFIX_FIELDS = [
    "row_pair",
    "step49_row",
    "step48_row",
    "matched_phases",
    "projected_mass_delta_max_abs",
    "active_cell_count_delta_max_abs",
    "applied_velocity_delta_max_abs",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_diagnostics import compare_step48_prefix

    step48_rows = read_json("outputs/step48_10step_envelope_matrix/ten_step_envelope_matrix.json")["rows"]
    rows, summary = compare_step48_prefix(step48_rows, twenty_step_envelope_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 49 Step 48 prefix comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_step48_prefix_comparison"
    write_csv_rows(out_dir / "step48_prefix_comparison.csv", rows, PREFIX_FIELDS)
    write_json(out_dir / "step48_prefix_comparison.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 49 Step 48 prefix comparison finished"
    write_log("logs/step49_step48_prefix_comparison.log", [marker, f"row_pair_count={summary['row_pair_count']}", f"comparison_pass_count={summary['comparison_pass_count']}"])
    print(f"row_pair_count={summary['row_pair_count']}")
    print(marker)


if __name__ == "__main__":
    main()
