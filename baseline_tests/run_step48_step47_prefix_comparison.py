import os

from step48_common import ROOT, read_json, ten_step_envelope_rows, write_csv_rows, write_json, write_log


PREFIX_FIELDS = [
    "row_pair",
    "step48_row",
    "step47_row",
    "matched_phases",
    "projected_mass_delta_max_abs",
    "active_cell_count_delta_max_abs",
    "applied_velocity_delta_max_abs",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_10step_diagnostics import compare_step47_prefix

    step47_rows = read_json("outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.json")["rows"]
    rows, summary = compare_step47_prefix(step47_rows, ten_step_envelope_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 48 Step 47 prefix comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step48_step47_prefix_comparison"
    write_csv_rows(out_dir / "step47_prefix_comparison.csv", rows, PREFIX_FIELDS)
    write_json(out_dir / "step47_prefix_comparison.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 48 Step 47 prefix comparison finished"
    write_log("logs/step48_step47_prefix_comparison.log", [marker, f"row_pair_count={summary['row_pair_count']}", f"comparison_pass_count={summary['comparison_pass_count']}"])
    print(f"row_pair_count={summary['row_pair_count']}")
    print(marker)


if __name__ == "__main__":
    main()
