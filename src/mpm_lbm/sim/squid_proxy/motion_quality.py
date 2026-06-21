import math


QUALITY_FIELDS = ["check", "pass", "value", "notes"]


def analyze_motion_mapping(rows: list[dict], mapping_config) -> dict:
    sample_indices = {int(row["sample_index"]) for row in rows}
    region_ids = {row["region_id"] for row in rows}
    expected_row_count = len(sample_indices) * len(mapping_config.tracked_regions)
    mantle_rows = [row for row in rows if row["region_id"] == "mantle_outer"]
    cavity_rows = [row for row in rows if row["region_id"] == "mantle_cavity_proxy"]
    funnel_rows = [row for row in rows if row["region_id"] == "funnel_outlet_proxy"]
    analysis = {
        "row_count": len(rows),
        "expected_row_count": expected_row_count,
        "schedule_sample_count": len(sample_indices),
        "tracked_region_count": len(region_ids),
        "expected_tracked_region_count": len(mapping_config.tracked_regions),
        "row_count_pass": len(rows) == expected_row_count,
        "tracked_region_count_pass": region_ids == set(mapping_config.tracked_regions),
        "finite_pass": _finite_rows(rows),
        "bounds_pass": all(bool(row["bounds_pass"]) for row in rows),
        "mantle_motion_pass": _mantle_motion_pass(mantle_rows),
        "cavity_motion_pass": _cavity_motion_pass(cavity_rows),
        "funnel_motion_pass": _funnel_motion_pass(funnel_rows),
        "mantle_velocity_nonzero_during_cycle": any(float(row["velocity_norm_max"]) > 0.0 for row in mantle_rows),
        "cavity_volume_rate_nonzero_during_cycle": any(abs(float(row["volume_rate"])) > 0.0 for row in cavity_rows),
        "funnel_aperture_rate_nonzero_during_open_close": any(abs(float(row["aperture_rate"])) > 0.0 for row in funnel_rows),
        "driver_integration_disabled_pass": all(not bool(row["driver_integration_enabled"]) for row in rows),
        "lbm_wall_velocity_disabled_pass": all(not bool(row["lbm_wall_velocity_enabled"]) for row in rows),
        "jet_model_disabled_pass": all(not bool(row["jet_model_enabled"]) for row in rows),
        "actuation_disabled_pass": all(not bool(row["actuation_enabled"]) for row in rows),
    }
    analysis["quality_pass"] = all(
        bool(analysis[key])
        for key in (
            "row_count_pass",
            "tracked_region_count_pass",
            "finite_pass",
            "bounds_pass",
            "mantle_motion_pass",
            "cavity_motion_pass",
            "funnel_motion_pass",
            "mantle_velocity_nonzero_during_cycle",
            "cavity_volume_rate_nonzero_during_cycle",
            "funnel_aperture_rate_nonzero_during_open_close",
            "driver_integration_disabled_pass",
            "lbm_wall_velocity_disabled_pass",
            "jet_model_disabled_pass",
            "actuation_disabled_pass",
        )
    )
    return analysis


def quality_rows_from_motion_analysis(analysis: dict) -> list[dict]:
    checks = [
        ("row_count_pass", analysis["row_count_pass"], analysis["row_count"], "row_count must match samples times tracked regions"),
        ("tracked_region_count_pass", analysis["tracked_region_count_pass"], analysis["tracked_region_count"], "all tracked regions must be present"),
        ("finite_pass", analysis["finite_pass"], analysis["finite_pass"], "motion numeric fields must be finite"),
        ("bounds_pass", analysis["bounds_pass"], analysis["bounds_pass"], "motion proxy norms and scales must be bounded"),
        ("mantle_motion_pass", analysis["mantle_motion_pass"], analysis["mantle_motion_pass"], "mantle proxy motion diagnostics must be present"),
        ("cavity_motion_pass", analysis["cavity_motion_pass"], analysis["cavity_motion_pass"], "cavity proxy volume diagnostics must be present"),
        ("funnel_motion_pass", analysis["funnel_motion_pass"], analysis["funnel_motion_pass"], "funnel proxy aperture diagnostics must be present"),
        (
            "mantle_velocity_nonzero_during_cycle",
            analysis["mantle_velocity_nonzero_during_cycle"],
            analysis["mantle_velocity_nonzero_during_cycle"],
            "mantle velocity proxy must be nonzero during the prescribed cycle",
        ),
        (
            "cavity_volume_rate_nonzero_during_cycle",
            analysis["cavity_volume_rate_nonzero_during_cycle"],
            analysis["cavity_volume_rate_nonzero_during_cycle"],
            "cavity volume-rate proxy must be nonzero during the prescribed cycle",
        ),
        (
            "funnel_aperture_rate_nonzero_during_open_close",
            analysis["funnel_aperture_rate_nonzero_during_open_close"],
            analysis["funnel_aperture_rate_nonzero_during_open_close"],
            "funnel aperture-rate proxy must be nonzero during open/close phases",
        ),
        ("driver_integration_disabled_pass", analysis["driver_integration_disabled_pass"], analysis["driver_integration_disabled_pass"], "driver integration must stay disabled"),
        ("lbm_wall_velocity_disabled_pass", analysis["lbm_wall_velocity_disabled_pass"], analysis["lbm_wall_velocity_disabled_pass"], "LBM wall velocity must stay disabled"),
        ("jet_model_disabled_pass", analysis["jet_model_disabled_pass"], analysis["jet_model_disabled_pass"], "jet model must stay disabled"),
        ("actuation_disabled_pass", analysis["actuation_disabled_pass"], analysis["actuation_disabled_pass"], "actuation must stay disabled"),
        ("quality_pass", analysis["quality_pass"], analysis["quality_pass"], "all Step 33 motion quality checks must pass"),
    ]
    return [{"check": check, "pass": bool(passed), "value": value, "notes": notes} for check, passed, value, notes in checks]


def assert_motion_mapping_quality(analysis: dict) -> None:
    if not bool(analysis.get("quality_pass", False)):
        raise RuntimeError(f"Step 33 motion mapping quality failed: {analysis}")


def _finite_rows(rows: list[dict]) -> bool:
    numeric_fields = [
        "phase",
        "point_count",
        "displacement_norm_min",
        "displacement_norm_max",
        "displacement_norm_mean",
        "velocity_norm_min",
        "velocity_norm_max",
        "velocity_norm_mean",
        "mantle_radius_scale",
        "mantle_radius_rate",
        "volume_scale",
        "volume_rate",
        "aperture_scale",
        "aperture_rate",
    ]
    return all(math.isfinite(float(row[field])) for row in rows for field in numeric_fields)


def _mantle_motion_pass(rows: list[dict]) -> bool:
    return bool(rows) and all(row["motion_model"] == "radial_scale_proxy" for row in rows) and max(float(row["displacement_norm_max"]) for row in rows) > 0.0


def _cavity_motion_pass(rows: list[dict]) -> bool:
    return bool(rows) and all(row["motion_model"] == "volume_scale_proxy" for row in rows) and min(float(row["volume_scale"]) for row in rows) < max(float(row["volume_scale"]) for row in rows)


def _funnel_motion_pass(rows: list[dict]) -> bool:
    return bool(rows) and all(row["motion_model"] == "aperture_scale_proxy" for row in rows) and min(float(row["aperture_scale"]) for row in rows) < max(float(row["aperture_scale"]) for row in rows)
