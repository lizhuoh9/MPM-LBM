import math

from src.mpm_lbm.sim.wall_velocity.config import EXPECTED_WALL_VELOCITY_ROW_COUNT, WallVelocityFieldConfig


def analyze_wall_velocity_quality(rows: list[dict], config: WallVelocityFieldConfig) -> dict:
    row_count_pass = len(rows) == EXPECTED_WALL_VELOCITY_ROW_COUNT
    finite_pass = all(_finite_row(row) and bool(row.get("finite_pass", False)) for row in rows)
    bounds_pass = all(bool(row.get("bounds_pass", False)) for row in rows)
    coverage_pass = all(int(row["active_cell_count"]) > 0 for row in rows)
    max_velocity_norm = max((float(row["velocity_norm_max"]) for row in rows), default=0.0)
    max_velocity_norm_pass = max_velocity_norm <= float(config.max_velocity_norm_allowed)
    diagnostic_only_pass = all(bool(row["diagnostic_only"]) for row in rows)
    no_lbm_update_pass = all(not bool(row["apply_to_lbm"]) and not bool(row["lbm_population_update_enabled"]) for row in rows)
    no_bounceback_update_pass = all(not bool(row["moving_bounceback_update_enabled"]) for row in rows)
    no_driver_integration_pass = all(not bool(row["driver_integration_enabled"]) for row in rows)
    expected_grid_size_count = len(config.grid_sizes)
    expected_phase_sample_count = len(config.phase_samples)
    expected_tracked_region_count = len(config.tracked_regions)
    summary = {
        "row_count": len(rows),
        "expected_row_count": EXPECTED_WALL_VELOCITY_ROW_COUNT,
        "row_count_pass": row_count_pass,
        "grid_size_count": len({int(row["grid_size"]) for row in rows}),
        "expected_grid_size_count": expected_grid_size_count,
        "phase_sample_count": len({float(row["phase"]) for row in rows}),
        "expected_phase_sample_count": expected_phase_sample_count,
        "tracked_region_count": len({row["region_id"] for row in rows}),
        "expected_tracked_region_count": expected_tracked_region_count,
        "finite_pass": finite_pass,
        "bounds_pass": bounds_pass,
        "coverage_pass": coverage_pass,
        "max_velocity_norm": max_velocity_norm,
        "max_velocity_norm_allowed": float(config.max_velocity_norm_allowed),
        "max_velocity_norm_pass": max_velocity_norm_pass,
        "diagnostic_only_pass": diagnostic_only_pass,
        "no_lbm_update_pass": no_lbm_update_pass,
        "no_bounceback_update_pass": no_bounceback_update_pass,
        "no_driver_integration_pass": no_driver_integration_pass,
        "apply_to_lbm_count": sum(1 for row in rows if bool(row["apply_to_lbm"])),
        "lbm_population_update_enabled_count": sum(1 for row in rows if bool(row["lbm_population_update_enabled"])),
        "moving_bounceback_update_enabled_count": sum(1 for row in rows if bool(row["moving_bounceback_update_enabled"])),
        "driver_integration_enabled_count": sum(1 for row in rows if bool(row["driver_integration_enabled"])),
    }
    summary["quality_pass"] = all(
        bool(summary[key])
        for key in (
            "row_count_pass",
            "finite_pass",
            "bounds_pass",
            "coverage_pass",
            "max_velocity_norm_pass",
            "diagnostic_only_pass",
            "no_lbm_update_pass",
            "no_bounceback_update_pass",
            "no_driver_integration_pass",
        )
    )
    return summary


def quality_summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def _finite_row(row: dict) -> bool:
    numeric_fields = [
        "grid_size",
        "phase",
        "active_cell_count",
        "sample_point_count",
        "velocity_norm_min",
        "velocity_norm_max",
        "velocity_norm_mean",
        "velocity_x_mean",
        "velocity_y_mean",
        "velocity_z_mean",
        "displacement_norm_max",
        "source_motion_velocity_norm_max",
        "mantle_radius_rate",
        "volume_rate",
        "aperture_rate",
    ]
    return all(math.isfinite(float(row[field])) for field in numeric_fields)
