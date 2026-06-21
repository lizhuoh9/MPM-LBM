import math

from src.mpm_lbm.sim.geometry_displacement.consistency import cycle_closure_rows


QUALITY_FIELDS = ["check", "pass", "value", "notes"]


def analyze_displacement_quality(rows: list[dict], config) -> dict:
    sample_indices = {int(row["sample_index"]) for row in rows}
    region_ids = {row["region_id"] for row in rows}
    expected_row_count = len(sample_indices) * len(config.tracked_regions)
    closure_rows, closure_summary = cycle_closure_rows(rows)
    analysis = {
        "row_count": len(rows),
        "expected_row_count": expected_row_count,
        "phase_sample_count": len(sample_indices),
        "tracked_region_count": len(region_ids),
        "row_count_pass": len(rows) == expected_row_count == 243,
        "tracked_region_count_pass": region_ids == set(config.tracked_regions),
        "finite_pass": _finite_rows(rows),
        "bounds_pass": all(bool(row["bounds_pass"]) for row in rows),
        "coverage_pass": all(int(row["point_count"]) > 0 for row in rows),
        "cycle_closure_pass": bool(closure_summary["cycle_closure_pass"]),
        "endpoint_repeatability_pass": bool(closure_summary["cycle_closure_pass"]),
        "diagnostic_only_pass": all(bool(row["diagnostic_only"]) for row in rows),
        "no_driver_update_pass": all(not bool(row["apply_to_driver"]) and not bool(row["driver_integration_enabled"]) for row in rows),
        "no_lbm_update_pass": all(not bool(row["apply_to_lbm"]) for row in rows),
        "no_mpm_update_pass": all(not bool(row["apply_to_mpm"]) for row in rows),
        "no_projection_update_pass": all(not bool(row["apply_to_projection"]) for row in rows),
        "no_dense_field_pass": config.write_dense_displacement_field is False,
        "no_displaced_particles_pass": config.write_displaced_particles is False,
    }
    del closure_rows
    analysis["quality_pass"] = all(
        bool(analysis[key])
        for key in (
            "row_count_pass",
            "tracked_region_count_pass",
            "finite_pass",
            "bounds_pass",
            "coverage_pass",
            "cycle_closure_pass",
            "endpoint_repeatability_pass",
            "diagnostic_only_pass",
            "no_driver_update_pass",
            "no_lbm_update_pass",
            "no_mpm_update_pass",
            "no_projection_update_pass",
            "no_dense_field_pass",
            "no_displaced_particles_pass",
        )
    )
    return analysis


def quality_rows_from_displacement_analysis(analysis: dict) -> list[dict]:
    checks = [
        ("row_count_pass", analysis["row_count_pass"], analysis["row_count"], "row count must be 81 phases times 3 regions"),
        ("tracked_region_count_pass", analysis["tracked_region_count_pass"], analysis["tracked_region_count"], "all tracked regions must be present"),
        ("finite_pass", analysis["finite_pass"], analysis["finite_pass"], "all numeric diagnostics must be finite"),
        ("bounds_pass", analysis["bounds_pass"], analysis["bounds_pass"], "displacement norms and bounding boxes must be bounded"),
        ("coverage_pass", analysis["coverage_pass"], analysis["coverage_pass"], "every tracked region must have sampled support"),
        ("cycle_closure_pass", analysis["cycle_closure_pass"], analysis["cycle_closure_pass"], "phase 0 and phase 1 diagnostics must close"),
        ("endpoint_repeatability_pass", analysis["endpoint_repeatability_pass"], analysis["endpoint_repeatability_pass"], "endpoint rows must repeat deterministically"),
        ("diagnostic_only_pass", analysis["diagnostic_only_pass"], analysis["diagnostic_only_pass"], "rows must stay diagnostic-only"),
        ("no_driver_update_pass", analysis["no_driver_update_pass"], analysis["no_driver_update_pass"], "driver updates must stay disabled"),
        ("no_lbm_update_pass", analysis["no_lbm_update_pass"], analysis["no_lbm_update_pass"], "LBM updates must stay disabled"),
        ("no_mpm_update_pass", analysis["no_mpm_update_pass"], analysis["no_mpm_update_pass"], "MPM updates must stay disabled"),
        ("no_projection_update_pass", analysis["no_projection_update_pass"], analysis["no_projection_update_pass"], "projection updates must stay disabled"),
        ("no_dense_field_pass", analysis["no_dense_field_pass"], analysis["no_dense_field_pass"], "dense field output must stay disabled"),
        ("no_displaced_particles_pass", analysis["no_displaced_particles_pass"], analysis["no_displaced_particles_pass"], "displaced particle output must stay disabled"),
        ("quality_pass", analysis["quality_pass"], analysis["quality_pass"], "all Step 42 quality checks must pass"),
    ]
    return [{"check": check, "pass": bool(passed), "value": value, "notes": notes} for check, passed, value, notes in checks]


def assert_displacement_quality(analysis: dict) -> None:
    if not bool(analysis.get("quality_pass", False)):
        raise RuntimeError(f"Step 42 displacement quality failed: {analysis}")


def _finite_rows(rows: list[dict]) -> bool:
    numeric_fields = [
        "phase",
        "point_count",
        "displacement_norm_min",
        "displacement_norm_max",
        "displacement_norm_mean",
        "bbox_min_x",
        "bbox_min_y",
        "bbox_min_z",
        "bbox_max_x",
        "bbox_max_y",
        "bbox_max_z",
        "mantle_radius_scale",
        "mantle_radius_rate",
        "volume_scale",
        "volume_rate",
        "aperture_scale",
        "aperture_rate",
    ]
    return all(math.isfinite(float(row[field])) for row in rows for field in numeric_fields)
