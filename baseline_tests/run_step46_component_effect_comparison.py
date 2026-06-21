import os

from step46_common import ROOT, coupling_smoke_rows, write_csv_rows, write_json, write_log


COMPARISON_FIELDS = [
    "comparison",
    "left_row",
    "right_row",
    "projected_mass_delta",
    "active_cell_delta",
    "applied_velocity_delta",
    "hydro_force_delta",
    "bb_link_count_delta",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_diagnostics import compare_smoke_rows

    rows, summary = compare_smoke_rows(coupling_smoke_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 46 component effect comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step46_component_effect_comparison"
    write_csv_rows(out_dir / "component_effect_comparison.csv", rows, COMPARISON_FIELDS)
    write_json(out_dir / "component_effect_comparison.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 46 component effect comparison finished"
    write_log("logs/step46_component_effect_comparison.log", [marker, f"comparison_count={summary['comparison_count']}", f"comparison_pass_count={summary['comparison_pass_count']}"])
    print(f"comparison_count={summary['comparison_count']}")
    print(marker)


if __name__ == "__main__":
    main()
