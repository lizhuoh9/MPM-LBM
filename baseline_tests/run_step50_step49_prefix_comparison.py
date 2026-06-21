import os

from step50_common import ROOT, one_cycle_envelope_rows, read_json, write_csv_rows, write_json, write_log


FIELDS = [
    "row_pair",
    "step50_row",
    "step49_row",
    "matched_phases",
    "projected_mass_delta_max_abs",
    "active_cell_count_delta_max_abs",
    "applied_velocity_delta_max_abs",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import compare_step49_prefix

    step49_rows = read_json("outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.json")["rows"]
    rows, summary = compare_step49_prefix(step49_rows, one_cycle_envelope_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 50 Step 49 prefix comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_step49_prefix_comparison"
    write_csv_rows(out_dir / "step49_prefix_comparison.csv", rows, FIELDS)
    write_json(out_dir / "step49_prefix_comparison.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 Step 49 prefix comparison finished"
    write_log("logs/step50_step49_prefix_comparison.log", [marker, f"matched_phase_count={summary['matched_phase_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(f"matched_phase_count={summary['matched_phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
