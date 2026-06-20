import os

from step41_common import (
    ROOT,
    SELECTED_CAP,
    SELECTED_SCALE,
    STEP41_APPLICATION_CONFIG_PATH,
    STEP41_BOUNDARY_MOTION_CONFIG_PATH,
    STEP41_DRIVER_CONFIGS,
    fieldnames_from_rows,
    read_json,
    write_csv_rows,
    write_json,
    write_log,
)


def main():
    os.chdir(ROOT)
    rows = validation_rows()
    summary = summarize(rows)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 41 selected parameter config validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_selected_parameter_config_validation"
    write_csv_rows(out_dir / "selected_parameter_config_validation.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "selected_parameter_config_validation.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 41 selected parameter config validation finished"
    write_log("logs/step41_selected_parameter_config_validation.log", [marker, f"validation_pass={summary['validation_pass']}"])
    print(f"validation_pass={summary['validation_pass']}")
    print(marker)


def validation_rows():
    rows = []
    application = read_json(STEP41_APPLICATION_CONFIG_PATH)
    rows.append(
        {
            "kind": "application",
            "path": STEP41_APPLICATION_CONFIG_PATH,
            "wall_velocity_scale": float(application["wall_velocity_scale"]),
            "wall_velocity_cap_lbm": float(application["wall_velocity_cap_lbm"]),
            "application_mode": application["application_mode"],
            "apply_to_lbm_solid_vel": bool(application["apply_to_lbm_solid_vel"]),
            "apply_to_lbm_populations": bool(application["apply_to_lbm_populations"]),
            "modify_bounceback_formula": bool(application["modify_bounceback_formula"]),
            "jet_model_enabled": bool(application["jet_model_enabled"]),
            "actuation_claim_enabled": bool(application["actuation_claim_enabled"]),
            "pass": bool(
                application["application_mode"] == "solid_vel_experimental"
                and application["target_lbm_field"] == "solid_vel"
                and application["application_policy"] == "additive_capped"
                and float(application["wall_velocity_scale"]) == SELECTED_SCALE
                and float(application["wall_velocity_cap_lbm"]) == SELECTED_CAP
                and application["apply_to_lbm_solid_vel"] is True
                and application["apply_to_lbm_populations"] is False
                and application["apply_to_mpm"] is False
                and application["apply_to_projector"] is False
                and application["modify_bounceback_formula"] is False
                and application["jet_model_enabled"] is False
                and application["actuation_claim_enabled"] is False
            ),
        }
    )
    for path in STEP41_DRIVER_CONFIGS:
        config = read_json(path)
        experimental = config["wall_velocity_application_mode"] == "solid_vel_experimental"
        rows.append(
            {
                "kind": "driver",
                "path": path,
                "wall_velocity_scale": SELECTED_SCALE if experimental else 0.0,
                "wall_velocity_cap_lbm": SELECTED_CAP if experimental else 0.0,
                "application_mode": config["wall_velocity_application_mode"],
                "apply_to_lbm_solid_vel": experimental,
                "apply_to_lbm_populations": False,
                "modify_bounceback_formula": False,
                "jet_model_enabled": False,
                "actuation_claim_enabled": False,
                "n_grid": int(config["n_grid"]),
                "n_lbm_steps": int(config["n_lbm_steps"]),
                "target_u_lbm_zero": tuple(config["target_u_lbm"]) == (0.0, 0.0, 0.0),
                "pass": bool(
                    config["coupling_mode"] == "moving_boundary"
                    and config["geometry_type"] == "squid_proxy"
                    and int(config["n_grid"]) == 64
                    and int(config["n_particles"]) == 4096
                    and int(config["n_lbm_steps"]) == 40
                    and int(config["mpm_substeps_per_lbm_step"]) == 5
                    and tuple(config["target_u_lbm"]) == (0.0, 0.0, 0.0)
                    and config["quality_check_enabled"] is True
                    and config["quality_check_strict"] is True
                    and config["write_vtk"] is False
                    and config["write_particles"] is False
                    and (
                        (
                            not experimental
                            and config["boundary_motion_mode"] == "static"
                            and config["wall_velocity_application_config_path"] is None
                        )
                        or (
                            experimental
                            and config["boundary_motion_mode"] == "prescribed_kinematic"
                            and config["boundary_motion_config_path"] == STEP41_BOUNDARY_MOTION_CONFIG_PATH
                            and config["wall_velocity_application_config_path"] == STEP41_APPLICATION_CONFIG_PATH
                        )
                    )
                ),
            }
        )
    return rows


def summarize(rows):
    application_rows = [row for row in rows if row["kind"] == "application"]
    driver_rows = [row for row in rows if row["kind"] == "driver"]
    return {
        "application_config_count": len(application_rows),
        "driver_config_count": len(driver_rows),
        "static_config_count": sum(1 for row in driver_rows if row["application_mode"] == "disabled"),
        "experimental_config_count": sum(1 for row in driver_rows if row["application_mode"] == "solid_vel_experimental"),
        "selected_wall_velocity_scale": SELECTED_SCALE,
        "wall_velocity_cap_lbm": SELECTED_CAP,
        "all_driver_n_grid_64": all(int(row["n_grid"]) == 64 for row in driver_rows),
        "all_driver_40_steps": all(int(row["n_lbm_steps"]) == 40 for row in driver_rows),
        "all_target_u_lbm_zero": all(row["target_u_lbm_zero"] for row in driver_rows),
        "validation_pass": bool(
            len(application_rows) == 1
            and len(driver_rows) == 4
            and sum(1 for row in driver_rows if row["application_mode"] == "disabled") == 2
            and sum(1 for row in driver_rows if row["application_mode"] == "solid_vel_experimental") == 2
            and all(row["pass"] for row in rows)
        ),
    }


if __name__ == "__main__":
    main()
