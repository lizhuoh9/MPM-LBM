import os

from step50_common import ROOT, one_cycle_envelope_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "comparison",
    "left_row",
    "right_row",
    "projected_mass_delta_max_abs",
    "active_cell_delta_max_abs",
    "applied_velocity_delta_max_abs",
    "hydro_force_delta_max_abs",
    "bb_link_count_delta_max_abs",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import compare_one_cycle_components

    rows, summary = compare_one_cycle_components(one_cycle_envelope_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 50 component effect one-cycle envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_component_effect_one_cycle_envelope"
    write_csv_rows(out_dir / "component_effect_one_cycle_envelope.csv", rows, FIELDS)
    write_json(out_dir / "component_effect_one_cycle_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 component effect one-cycle envelope finished"
    write_log("logs/step50_component_effect_one_cycle_envelope.log", [marker, f"comparison_count={summary['comparison_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(f"comparison_count={summary['comparison_count']}")
    print(marker)


if __name__ == "__main__":
    main()
