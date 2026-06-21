import os

from step48_common import ROOT, ten_step_envelope_rows, write_csv_rows, write_json, write_log


COMPARISON_FIELDS = [
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
    from src.runtime_geometry_wall_velocity_10step_diagnostics import compare_ten_step_components

    rows, summary = compare_ten_step_components(ten_step_envelope_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 48 component effect 10-step envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step48_component_effect_10step_envelope"
    write_csv_rows(out_dir / "component_effect_10step_envelope.csv", rows, COMPARISON_FIELDS)
    write_json(out_dir / "component_effect_10step_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 48 component effect 10-step envelope finished"
    write_log("logs/step48_component_effect_10step_envelope.log", [marker, f"comparison_count={summary['comparison_count']}", f"comparison_pass_count={summary['comparison_pass_count']}"])
    print(f"comparison_count={summary['comparison_count']}")
    print(marker)


if __name__ == "__main__":
    main()
