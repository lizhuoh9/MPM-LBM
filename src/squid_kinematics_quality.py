import math


QUALITY_FIELDS = ["check", "pass", "value", "notes"]


def analyze_kinematics_schedule(rows: list[dict], config) -> dict:
    phases = [float(row["phase"]) for row in rows]
    analysis = {
        "row_count": len(rows),
        "expected_row_count": int(config.sample_count),
        "finite_pass": _finite_rows(rows),
        "bounds_pass": _bounds_pass(rows, config),
        "phase_monotonic_pass": all(phases[index] <= phases[index + 1] for index in range(max(0, len(phases) - 1))),
        "endpoint_repeatability_pass": _endpoint_repeatability(rows),
        "derivative_finite_pass": _derivative_finite_pass(rows),
        "contraction_volume_rate_pass": _contraction_volume_rate_pass(rows, config),
        "refill_volume_rate_pass": _refill_volume_rate_pass(rows, config),
        "funnel_aperture_bounds_pass": _funnel_aperture_bounds_pass(rows, config),
        "driver_integration_disabled_pass": all(not bool(row["driver_integration_enabled"]) for row in rows),
        "actuation_disabled_pass": all(not bool(row["actuation_enabled"]) for row in rows),
    }
    analysis["row_count_pass"] = analysis["row_count"] == analysis["expected_row_count"]
    analysis["quality_pass"] = all(
        bool(analysis[key])
        for key in (
            "row_count_pass",
            "finite_pass",
            "bounds_pass",
            "phase_monotonic_pass",
            "endpoint_repeatability_pass",
            "derivative_finite_pass",
            "contraction_volume_rate_pass",
            "refill_volume_rate_pass",
            "funnel_aperture_bounds_pass",
            "driver_integration_disabled_pass",
            "actuation_disabled_pass",
        )
    )
    return analysis


def quality_rows_from_analysis(analysis: dict) -> list[dict]:
    checks = [
        ("row_count_pass", analysis["row_count_pass"], analysis["row_count"], "row_count must match sample_count"),
        ("finite_pass", analysis["finite_pass"], analysis["finite_pass"], "schedule numeric fields must be finite"),
        ("bounds_pass", analysis["bounds_pass"], analysis["bounds_pass"], "mantle and cavity scales must stay inside configured bounds"),
        ("phase_monotonic_pass", analysis["phase_monotonic_pass"], analysis["phase_monotonic_pass"], "phase samples must be monotonic"),
        ("endpoint_repeatability_pass", analysis["endpoint_repeatability_pass"], analysis["endpoint_repeatability_pass"], "cycle endpoints must repeat rest values"),
        ("derivative_finite_pass", analysis["derivative_finite_pass"], analysis["derivative_finite_pass"], "first derivatives must be finite"),
        ("contraction_volume_rate_pass", analysis["contraction_volume_rate_pass"], analysis["contraction_volume_rate_pass"], "cavity volume must not increase during contraction"),
        ("refill_volume_rate_pass", analysis["refill_volume_rate_pass"], analysis["refill_volume_rate_pass"], "cavity volume must not decrease during refill"),
        ("funnel_aperture_bounds_pass", analysis["funnel_aperture_bounds_pass"], analysis["funnel_aperture_bounds_pass"], "funnel aperture must stay inside configured bounds"),
        ("driver_integration_disabled_pass", analysis["driver_integration_disabled_pass"], analysis["driver_integration_disabled_pass"], "Step 32 rows must not enable driver integration"),
        ("actuation_disabled_pass", analysis["actuation_disabled_pass"], analysis["actuation_disabled_pass"], "Step 32 rows must not enable actuation"),
        ("quality_pass", analysis["quality_pass"], analysis["quality_pass"], "all schedule quality checks must pass"),
    ]
    return [{"check": check, "pass": bool(passed), "value": value, "notes": notes} for check, passed, value, notes in checks]


def assert_kinematics_schedule_quality(analysis: dict) -> None:
    if not bool(analysis.get("quality_pass", False)):
        raise RuntimeError(f"Step 32 schedule quality failed: {analysis}")


def _finite_rows(rows: list[dict]) -> bool:
    numeric_fields = [
        "phase",
        "cycle_time_fraction",
        "mantle_radius_scale",
        "mantle_radius_rate",
        "cavity_volume_scale",
        "cavity_volume_rate",
        "funnel_aperture_scale",
        "funnel_aperture_rate",
        "ramp_weight",
    ]
    return all(math.isfinite(float(row[field])) for row in rows for field in numeric_fields)


def _bounds_pass(rows: list[dict], config) -> bool:
    tolerance = 1.0e-12
    for row in rows:
        mantle = float(row["mantle_radius_scale"])
        cavity = float(row["cavity_volume_scale"])
        if mantle < config.mantle_radius_scale_min - tolerance or mantle > config.mantle_radius_scale_rest + tolerance:
            return False
        if cavity < config.cavity_volume_scale_min - tolerance or cavity > config.cavity_volume_scale_rest + tolerance:
            return False
    return True


def _funnel_aperture_bounds_pass(rows: list[dict], config) -> bool:
    tolerance = 1.0e-12
    return all(
        config.funnel_aperture_scale_rest - tolerance <= float(row["funnel_aperture_scale"]) <= config.funnel_aperture_scale_max + tolerance
        for row in rows
    )


def _endpoint_repeatability(rows: list[dict]) -> bool:
    if not rows:
        return False
    first = rows[0]
    last = rows[-1]
    return all(
        abs(float(first[field]) - float(last[field])) <= 1.0e-12
        for field in ("mantle_radius_scale", "cavity_volume_scale", "funnel_aperture_scale")
    )


def _derivative_finite_pass(rows: list[dict]) -> bool:
    return all(
        math.isfinite(float(row[field]))
        for row in rows
        for field in ("mantle_radius_rate", "cavity_volume_rate", "funnel_aperture_rate")
    )


def _contraction_volume_rate_pass(rows: list[dict], config) -> bool:
    tolerance = 1.0e-9
    phase_tolerance = 1.0e-12
    selected = [
        row
        for row in rows
        if config.contraction_start_phase + phase_tolerance < float(row["phase"]) < config.contraction_end_phase - phase_tolerance
    ]
    return bool(selected) and all(float(row["cavity_volume_rate"]) <= tolerance for row in selected)


def _refill_volume_rate_pass(rows: list[dict], config) -> bool:
    tolerance = 1.0e-9
    phase_tolerance = 1.0e-12
    selected = [
        row
        for row in rows
        if config.refill_start_phase + phase_tolerance < float(row["phase"]) < config.refill_end_phase - phase_tolerance
    ]
    return bool(selected) and all(float(row["cavity_volume_rate"]) >= -tolerance for row in selected)
