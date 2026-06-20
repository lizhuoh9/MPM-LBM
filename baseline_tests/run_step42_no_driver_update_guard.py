import os

from step42_common import ROOT, check_row, load_displacement_config, make_displacement_rows, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    config = load_displacement_config()
    rows = make_displacement_rows()
    summary = {
        "guard_pass": True,
        "driver_update_count": sum(1 for row in rows if bool(row["apply_to_driver"])),
        "lbm_update_count": sum(1 for row in rows if bool(row["apply_to_lbm"])),
        "mpm_update_count": sum(1 for row in rows if bool(row["apply_to_mpm"])),
        "projection_update_count": sum(1 for row in rows if bool(row["apply_to_projection"])),
        "dynamic_solid_update_count": sum(1 for row in rows if bool(row["update_dynamic_solid"])),
        "displaced_particle_output_count": 0 if config.write_displaced_particles is False else 1,
        "dense_displacement_field_output_count": 0 if config.write_dense_displacement_field is False else 1,
        "fsidriver_integration_count": sum(1 for row in rows if bool(row["driver_integration_enabled"])),
        "apply_to_driver": bool(config.apply_to_driver),
        "apply_to_lbm": bool(config.apply_to_lbm),
        "apply_to_mpm": bool(config.apply_to_mpm),
        "apply_to_projection": bool(config.apply_to_projection),
        "update_dynamic_solid": bool(config.update_dynamic_solid),
        "driver_integration_enabled": bool(config.driver_integration_enabled),
    }
    summary["guard_pass"] = all(
        int(summary[key]) == 0
        for key in (
            "driver_update_count",
            "lbm_update_count",
            "mpm_update_count",
            "projection_update_count",
            "dynamic_solid_update_count",
            "displaced_particle_output_count",
            "dense_displacement_field_output_count",
            "fsidriver_integration_count",
        )
    )
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 42 no driver update guard failed: {summary}")
    guard_rows = [
        check_row("driver_update_count", summary["driver_update_count"] == 0, summary["driver_update_count"], "Step 42 must not update driver geometry"),
        check_row("lbm_update_count", summary["lbm_update_count"] == 0, summary["lbm_update_count"], "Step 42 must not update LBM state"),
        check_row("mpm_update_count", summary["mpm_update_count"] == 0, summary["mpm_update_count"], "Step 42 must not update MPM state"),
        check_row("projection_update_count", summary["projection_update_count"] == 0, summary["projection_update_count"], "Step 42 must not update projection state"),
        check_row("dynamic_solid_update_count", summary["dynamic_solid_update_count"] == 0, summary["dynamic_solid_update_count"], "Step 42 must not update dynamic_solid"),
        check_row("displaced_particle_output_count", summary["displaced_particle_output_count"] == 0, summary["displaced_particle_output_count"], "Step 42 must not write displaced particles"),
        check_row("dense_displacement_field_output_count", summary["dense_displacement_field_output_count"] == 0, summary["dense_displacement_field_output_count"], "Step 42 must not write dense displacement fields"),
        check_row("fsidriver_integration_count", summary["fsidriver_integration_count"] == 0, summary["fsidriver_integration_count"], "Step 42 must not integrate with FSIDriver3D"),
    ]

    out_dir = ROOT / "outputs" / "step42_no_driver_update_guard"
    write_csv_rows(out_dir / "no_driver_update_guard.csv", guard_rows, FIELDS)
    write_json(out_dir / "no_driver_update_guard.json", {"summary": summary, "rows": guard_rows})
    marker = "[OK] Step 42 no driver update guard finished"
    write_log("logs/step42_no_driver_update_guard.log", [marker, f"row_count={len(guard_rows)}", f"guard_pass={summary['guard_pass']}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
