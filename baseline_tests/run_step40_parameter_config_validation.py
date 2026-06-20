import os

from step40_common import (
    ROOT,
    STEP40_APPLICATION_CONFIGS,
    STEP40_BOUNDARY_MOTION_CONFIG_PATH,
    STEP40_DRIVER_CONFIGS,
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
        raise RuntimeError(f"Step 40 parameter config validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step40_parameter_config_validation"
    write_csv_rows(out_dir / "parameter_config_validation.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "parameter_config_validation.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 40 parameter config validation finished"
    write_log("logs/step40_parameter_config_validation.log", [marker, f"validation_pass={summary['validation_pass']}"])
    print(f"validation_pass={summary['validation_pass']}")
    print(marker)


def validation_rows():
    rows = []
    for path in STEP40_APPLICATION_CONFIGS:
        config = read_json(path)
        rows.append(
            {
                "kind": "application",
                "path": path,
                "wall_velocity_scale": float(config["wall_velocity_scale"]),
                "wall_velocity_cap_lbm": float(config["wall_velocity_cap_lbm"]),
                "application_mode": config["application_mode"],
                "apply_to_lbm_solid_vel": bool(config["apply_to_lbm_solid_vel"]),
                "apply_to_lbm_populations": bool(config["apply_to_lbm_populations"]),
                "modify_bounceback_formula": bool(config["modify_bounceback_formula"]),
                "jet_model_enabled": bool(config["jet_model_enabled"]),
                "actuation_claim_enabled": bool(config["actuation_claim_enabled"]),
                "pass": bool(
                    config["application_mode"] == "solid_vel_experimental"
                    and config["target_lbm_field"] == "solid_vel"
                    and config["application_policy"] == "additive_capped"
                    and float(config["wall_velocity_cap_lbm"]) == 0.01
                    and config["apply_to_lbm_solid_vel"] is True
                    and config["apply_to_lbm_populations"] is False
                    and config["modify_bounceback_formula"] is False
                    and config["jet_model_enabled"] is False
                    and config["actuation_claim_enabled"] is False
                ),
            }
        )
    for path in STEP40_DRIVER_CONFIGS:
        config = read_json(path)
        experimental = config["wall_velocity_application_mode"] == "solid_vel_experimental"
        rows.append(
            {
                "kind": "driver",
                "path": path,
                "wall_velocity_scale": scale_from_config(config),
                "wall_velocity_cap_lbm": 0.01 if experimental else 0.0,
                "application_mode": config["wall_velocity_application_mode"],
                "apply_to_lbm_solid_vel": experimental,
                "apply_to_lbm_populations": False,
                "modify_bounceback_formula": False,
                "jet_model_enabled": False,
                "actuation_claim_enabled": False,
                "pass": bool(
                    config["coupling_mode"] == "moving_boundary"
                    and config["geometry_type"] == "squid_proxy"
                    and int(config["n_grid"]) == 48
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
                            and config["boundary_motion_config_path"] == STEP40_BOUNDARY_MOTION_CONFIG_PATH
                            and config["wall_velocity_application_config_path"] in STEP40_APPLICATION_CONFIGS
                        )
                    )
                ),
            }
        )
    return rows


def summarize(rows):
    application_rows = [row for row in rows if row["kind"] == "application"]
    driver_rows = [row for row in rows if row["kind"] == "driver"]
    scales = sorted(float(row["wall_velocity_scale"]) for row in application_rows)
    return {
        "application_config_count": len(application_rows),
        "driver_config_count": len(driver_rows),
        "scale_values": scales,
        "all_caps_are_001": all(float(row["wall_velocity_cap_lbm"]) == 0.01 for row in application_rows),
        "static_disabled_count": sum(1 for row in driver_rows if row["application_mode"] == "disabled"),
        "experimental_config_count": sum(1 for row in driver_rows if row["application_mode"] == "solid_vel_experimental"),
        "validation_pass": bool(
            len(application_rows) == 3
            and len(driver_rows) == 8
            and scales == [0.025, 0.05, 0.075]
            and all(row["pass"] for row in rows)
        ),
    }


def scale_from_config(config):
    path = config.get("wall_velocity_application_config_path")
    if not path:
        return 0.0
    if path.endswith("0025.json"):
        return 0.025
    if path.endswith("0050.json"):
        return 0.05
    if path.endswith("0075.json"):
        return 0.075
    raise RuntimeError(f"unsupported Step 40 application config path: {path}")


if __name__ == "__main__":
    main()
