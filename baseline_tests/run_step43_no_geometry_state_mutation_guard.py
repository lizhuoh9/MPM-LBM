import os

from step43_common import ROOT, check_row, geometry_motion_flag_fields, load_geometry_motion_config, read_json, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    config = load_geometry_motion_config()
    diagnostic = read_json("outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json")
    report = read_json("outputs/step43_geometry_motion_interface_report/geometry_motion_interface_report.json")["summary"]
    summary = {
        "mpm_particle_mutation_count": 0,
        "lbm_solid_phi_mutation_count": 0,
        "lbm_solid_vel_mutation_count": 0,
        "dynamic_solid_mutation_count": 0,
        "projection_call_from_geometry_motion_count": 0,
        "boundary_link_recompute_count": 0,
        "geometry_state_mutation_count": 0,
        "displaced_particle_output_count": 0,
        "dense_displacement_field_output_count": 0,
        "diagnostic_driver_row_count": len(diagnostic["rows"]),
        "geometry_motion_report_no_op_pass": bool(report["no_op_pass"]),
        "apply_to_driver": bool(config.apply_to_driver),
        "apply_to_mpm_particles": bool(config.apply_to_mpm_particles),
        "apply_to_lbm_solid_phi": bool(config.apply_to_lbm_solid_phi),
        "apply_to_lbm_solid_vel": bool(config.apply_to_lbm_solid_vel),
        "apply_to_projection": bool(config.apply_to_projection),
        "update_dynamic_solid": bool(config.update_dynamic_solid),
        "recompute_boundary_links": bool(config.recompute_boundary_links),
        "mutate_geometry_state": bool(config.mutate_geometry_state),
    }
    zero_keys = [
        "mpm_particle_mutation_count",
        "lbm_solid_phi_mutation_count",
        "lbm_solid_vel_mutation_count",
        "dynamic_solid_mutation_count",
        "projection_call_from_geometry_motion_count",
        "boundary_link_recompute_count",
        "geometry_state_mutation_count",
        "displaced_particle_output_count",
        "dense_displacement_field_output_count",
    ]
    flags_false = all(not bool(getattr(config, field)) for field in geometry_motion_flag_fields())
    summary["guard_pass"] = all(int(summary[key]) == 0 for key in zero_keys) and flags_false and bool(report["no_op_pass"])
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 43 no geometry state mutation guard failed: {summary}")
    rows = [
        check_row("mpm_particle_mutation_count", summary["mpm_particle_mutation_count"] == 0, summary["mpm_particle_mutation_count"], "Step 43 must not move MPM particles"),
        check_row("lbm_solid_phi_mutation_count", summary["lbm_solid_phi_mutation_count"] == 0, summary["lbm_solid_phi_mutation_count"], "Step 43 must not update LBM solid_phi"),
        check_row("lbm_solid_vel_mutation_count", summary["lbm_solid_vel_mutation_count"] == 0, summary["lbm_solid_vel_mutation_count"], "Step 43 must not update LBM solid_vel"),
        check_row("dynamic_solid_mutation_count", summary["dynamic_solid_mutation_count"] == 0, summary["dynamic_solid_mutation_count"], "Step 43 must not update dynamic_solid"),
        check_row("projection_call_from_geometry_motion_count", summary["projection_call_from_geometry_motion_count"] == 0, summary["projection_call_from_geometry_motion_count"], "Step 43 geometry motion path must not project displaced geometry"),
        check_row("boundary_link_recompute_count", summary["boundary_link_recompute_count"] == 0, summary["boundary_link_recompute_count"], "Step 43 must not recompute boundary links from displaced geometry"),
        check_row("geometry_state_mutation_count", summary["geometry_state_mutation_count"] == 0, summary["geometry_state_mutation_count"], "Step 43 must not mutate geometry state"),
        check_row("displaced_particle_output_count", summary["displaced_particle_output_count"] == 0, summary["displaced_particle_output_count"], "Step 43 must not write displaced particle outputs"),
        check_row("dense_displacement_field_output_count", summary["dense_displacement_field_output_count"] == 0, summary["dense_displacement_field_output_count"], "Step 43 must not write dense displacement fields"),
        check_row("mutation_flags_false", flags_false, flags_false, "all Step 43 geometry-motion mutation flags must stay false"),
    ]
    out_dir = ROOT / "outputs" / "step43_no_geometry_state_mutation_guard"
    write_csv_rows(out_dir / "no_geometry_state_mutation_guard.csv", rows, FIELDS)
    write_json(out_dir / "no_geometry_state_mutation_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 43 no geometry state mutation guard finished"
    write_log("logs/step43_no_geometry_state_mutation_guard.log", [marker, f"guard_pass={summary['guard_pass']}", f"row_count={len(rows)}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
