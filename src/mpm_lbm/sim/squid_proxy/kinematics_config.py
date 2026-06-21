from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


@dataclass(frozen=True)
class SquidKinematicsScheduleConfig:
    schedule_id: str
    region_config_path: str
    geometry_config_path: str
    cycle_period_steps: int
    sample_count: int
    contraction_start_phase: float
    contraction_end_phase: float
    refill_start_phase: float
    refill_end_phase: float
    ramp_fraction: float
    mantle_radius_scale_rest: float
    mantle_radius_scale_min: float
    cavity_volume_scale_rest: float
    cavity_volume_scale_min: float
    funnel_aperture_scale_rest: float
    funnel_aperture_scale_max: float
    funnel_open_phase_start: float
    funnel_open_phase_end: float
    deterministic: bool
    driver_integration_enabled: bool = False
    actuation_enabled: bool = False
    scope_note: str = "schedule contract only; no driver integration"

    def __post_init__(self):
        for field in (
            "cycle_period_steps",
            "sample_count",
        ):
            object.__setattr__(self, field, int(getattr(self, field)))
        for field in (
            "contraction_start_phase",
            "contraction_end_phase",
            "refill_start_phase",
            "refill_end_phase",
            "ramp_fraction",
            "mantle_radius_scale_rest",
            "mantle_radius_scale_min",
            "cavity_volume_scale_rest",
            "cavity_volume_scale_min",
            "funnel_aperture_scale_rest",
            "funnel_aperture_scale_max",
            "funnel_open_phase_start",
            "funnel_open_phase_end",
        ):
            object.__setattr__(self, field, float(getattr(self, field)))
        object.__setattr__(self, "deterministic", bool(self.deterministic))
        object.__setattr__(self, "driver_integration_enabled", bool(self.driver_integration_enabled))
        object.__setattr__(self, "actuation_enabled", bool(self.actuation_enabled))

    @classmethod
    def from_json(cls, path):
        with Path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        return asdict(self)


def validate_kinematics_schedule_config(config: SquidKinematicsScheduleConfig, root=None) -> list[dict]:
    root_path = Path.cwd() if root is None else Path(root)
    rows = [
        _check("schedule_id_present", bool(config.schedule_id), config.schedule_id, "schedule_id must be nonempty"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("cycle_period_positive", config.cycle_period_steps > 0, config.cycle_period_steps, "cycle_period_steps must be positive"),
        _check(
            "sample_count_sufficient",
            config.sample_count >= config.cycle_period_steps + 1,
            config.sample_count,
            "sample_count must include at least one full closed cycle",
        ),
        _check("phase_values_finite", _phase_values_finite(config), _phase_payload(config), "phase values must be finite"),
        _check("phase_values_bounded", _phase_values_bounded(config), _phase_payload(config), "phase values must be in [0, 1]"),
        _check(
            "contraction_range_valid",
            config.contraction_start_phase < config.contraction_end_phase,
            [config.contraction_start_phase, config.contraction_end_phase],
            "contraction_start_phase must be less than contraction_end_phase",
        ),
        _check(
            "refill_range_valid",
            config.refill_start_phase == config.contraction_end_phase and config.refill_start_phase < config.refill_end_phase,
            [config.refill_start_phase, config.refill_end_phase],
            "refill must start at contraction_end_phase and end later",
        ),
        _check("cycle_endpoint_valid", config.refill_end_phase == 1.0, config.refill_end_phase, "refill_end_phase must close the cycle at 1.0"),
        _check("ramp_fraction_valid", 0.0 <= config.ramp_fraction <= 0.5, config.ramp_fraction, "ramp_fraction must be in [0, 0.5]"),
        _check(
            "mantle_scale_range_valid",
            0.0 < config.mantle_radius_scale_min <= config.mantle_radius_scale_rest,
            [config.mantle_radius_scale_min, config.mantle_radius_scale_rest],
            "mantle radius scale range must be positive and ordered",
        ),
        _check(
            "cavity_scale_range_valid",
            0.0 < config.cavity_volume_scale_min <= config.cavity_volume_scale_rest,
            [config.cavity_volume_scale_min, config.cavity_volume_scale_rest],
            "cavity volume scale range must be positive and ordered",
        ),
        _check(
            "funnel_scale_range_valid",
            0.0 <= config.funnel_aperture_scale_rest <= config.funnel_aperture_scale_max,
            [config.funnel_aperture_scale_rest, config.funnel_aperture_scale_max],
            "funnel aperture scale range must be nonnegative and ordered",
        ),
        _check(
            "funnel_open_window_valid",
            config.funnel_open_phase_start < config.funnel_open_phase_end,
            [config.funnel_open_phase_start, config.funnel_open_phase_end],
            "funnel open start must be less than end",
        ),
        _check("deterministic_enabled", config.deterministic is True, config.deterministic, "schedule must be deterministic"),
        _check(
            "driver_integration_disabled",
            config.driver_integration_enabled is False,
            config.driver_integration_enabled,
            "Step 32 must not integrate kinematics into the driver",
        ),
        _check("actuation_disabled", config.actuation_enabled is False, config.actuation_enabled, "Step 32 must not enable actuation"),
        _check(
            "scope_note_valid",
            "schedule contract only" in config.scope_note and "no driver integration" in config.scope_note,
            config.scope_note,
            "scope_note must state schedule-only and no driver integration",
        ),
    ]
    return rows


def summarize_config_validation(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
    }


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path: str) -> bool:
    path = Path(os.fspath(relative_path))
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def _phase_payload(config: SquidKinematicsScheduleConfig) -> list[float]:
    return [
        config.contraction_start_phase,
        config.contraction_end_phase,
        config.refill_start_phase,
        config.refill_end_phase,
        config.funnel_open_phase_start,
        config.funnel_open_phase_end,
    ]


def _phase_values_finite(config: SquidKinematicsScheduleConfig) -> bool:
    return all(math.isfinite(value) for value in _phase_payload(config))


def _phase_values_bounded(config: SquidKinematicsScheduleConfig) -> bool:
    return all(0.0 <= value <= 1.0 for value in _phase_payload(config))
