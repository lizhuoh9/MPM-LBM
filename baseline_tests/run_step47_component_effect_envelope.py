import os

from step47_common import ROOT, short_step_envelope_rows, write_csv_rows, write_json, write_log


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
    from src.runtime_geometry_wall_velocity_envelope_diagnostics import compare_short_step_components

    rows, summary = compare_short_step_components(short_step_envelope_rows())
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 47 component effect envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step47_component_effect_envelope"
    write_csv_rows(out_dir / "component_effect_envelope.csv", rows, COMPARISON_FIELDS)
    write_json(out_dir / "component_effect_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 47 component effect envelope finished"
    write_log("logs/step47_component_effect_envelope.log", [marker, f"comparison_count={summary['comparison_count']}", f"comparison_pass_count={summary['comparison_pass_count']}"])
    print(f"comparison_count={summary['comparison_count']}")
    print(marker)


if __name__ == "__main__":
    main()
