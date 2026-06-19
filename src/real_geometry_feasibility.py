import csv
import json
import math
import os
from pathlib import Path

import numpy as np

from .fsi_config import FSIDriverConfig
from .fsi_driver import FSIDriver3D
from .geometry import GeometrySampler3D
from .geometry_config import GeometryConfig
from .lbm_fluid import LBMFluid3D
from .mpm_solid import MPMSolid3D
from .projection import MPMToLBMProjector3D
from .run_utils import make_all_fluid_geo
from .sim_config import UnifiedSimConfig


PROJECTION_FIELDS = [
    "candidate_id",
    "geometry_type",
    "n_grid",
    "projected_mass",
    "projected_volume_raw",
    "projected_volume_clamped",
    "max_phi_raw",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "has_nan",
    "has_inf",
    "projection_pass",
    "scope_note",
]

SHORT_DRIVER_FIELDS = [
    "candidate_id",
    "geometry_type",
    "geometry_source",
    "mode",
    "reaction_transfer_mode",
    "quality_check_enabled",
    "quality_check_strict",
    "quality_pass",
    "quality_severity",
    "quality_warnings_count",
    "quality_reasons_count",
    "quality_gate_strict",
    "quality_report_path",
    "driver_timing_path",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count_min",
    "bb_link_count_max",
    "active_reaction_particle_count_max",
    "area_scale_final",
    "area_scale_min",
    "area_scale_max",
    "raw_area_scale_final",
    "has_nan",
    "has_inf",
    "stable",
    "notes",
]


def run_projection_only_scale_case(geometry_config_path, n_grid, out_dir) -> dict:
    config = GeometryConfig.from_json(_resolve_path(geometry_config_path))
    sample = GeometrySampler3D(config).sample_particles()

    sim_config = UnifiedSimConfig(n_grid=int(n_grid), mpm_substeps_per_lbm_step=1)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    geo_path = out_path / f"{_candidate_id_from_path(geometry_config_path)}_{int(n_grid)}_all_fluid.dat"
    make_all_fluid_geo(str(geo_path), sim_config.n_grid)

    lbm = LBMFluid3D(sim_config.make_lbm_config())
    lbm.init_geo(str(geo_path))
    lbm.init_simulation()
    solid = MPMSolid3D(sim_config.make_mpm_config(gravity=(0.0, 0.0, 0.0)), config.n_particles)
    solid.init_from_numpy(sample["x"], sample["vol0"], sample["mass"])
    projector = MPMToLBMProjector3D(sim_config)
    projector.project(solid, lbm)

    stats = projector.get_stats()
    phi = lbm.solid_phi.to_numpy()
    row = {
        "candidate_id": _candidate_id_from_path(geometry_config_path),
        "geometry_type": config.geometry_type,
        "n_grid": int(n_grid),
        "projected_mass": float(stats["projected_mass"]),
        "projected_volume_raw": float(stats["projected_volume_raw"]),
        "projected_volume_clamped": float(stats["projected_volume_clamped"]),
        "max_phi_raw": float(stats["max_phi_raw"]),
        "active_cell_count": int(stats["active_cell_count"]),
        "solid_phi_min": float(np.min(phi)),
        "solid_phi_max": float(np.max(phi)),
        "has_nan": bool(np.isnan(phi).any() or _stats_has_nan(stats)),
        "has_inf": bool(np.isinf(phi).any() or _stats_has_inf(stats)),
        "scope_note": "Step 26 projection-only scale diagnostics; no FSI driver long-run and no real squid validation claim",
    }
    row["projection_pass"] = bool(
        row["projected_mass"] > 0.0
        and row["active_cell_count"] > 0
        and row["solid_phi_min"] >= 0.0
        and row["solid_phi_max"] <= 1.0
        and _finite_values(row, excluded=("candidate_id", "geometry_type", "scope_note"))
        and not row["has_nan"]
        and not row["has_inf"]
    )
    if not row["projection_pass"]:
        raise RuntimeError(f"Step 26 projection-only scale case failed: {row}")
    return row


def run_short_driver_case(driver_config_path, out_dir) -> dict:
    config = FSIDriverConfig.from_json(_resolve_path(driver_config_path))
    _enforce_short_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 26 driver case: {driver_config_path}")
    report_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    _write_json(timing_path, driver.performance_row())
    row = summarize_short_driver_diagnostics(config, diagnostics, driver, report_path)
    row["driver_timing_path"] = _relative_path(timing_path)
    assert_short_driver_row(row)
    return row


def summarize_short_driver_diagnostics(config, diagnostics, driver, quality_report_path) -> dict:
    quality = _read_json(quality_report_path)
    gate = quality["gate"]
    post_step_rows = [row for row in diagnostics if int(row["step"]) > 0]
    if not post_step_rows:
        raise RuntimeError("Step 26 short driver diagnostics missing post-step rows")

    area = _area_stats(driver, config)
    row = {
        "candidate_id": _candidate_id_from_path(config.geometry_config_path),
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "quality_check_enabled": bool(config.quality_check_enabled),
        "quality_check_strict": bool(config.quality_check_strict),
        "quality_pass": bool(gate.get("pass", False)),
        "quality_severity": gate.get("severity", ""),
        "quality_warnings_count": len(gate.get("warnings", [])),
        "quality_reasons_count": len(gate.get("reasons", [])),
        "quality_gate_strict": bool(gate.get("strict", False)),
        "quality_report_path": _relative_path(quality_report_path),
        "driver_timing_path": "",
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "completed_lbm_steps": max(int(item["step"]) for item in diagnostics),
        "total_mpm_substeps": max(int(item["total_mpm_substeps"]) for item in diagnostics),
        "rho_min_global": min(float(item["rho_min"]) for item in diagnostics),
        "rho_max_global": max(float(item["rho_max"]) for item in diagnostics),
        "lbm_max_v_global": max(float(item["lbm_max_v"]) for item in diagnostics),
        "mpm_min_J_global": min(float(item["mpm_min_J"]) for item in diagnostics),
        "mpm_max_speed_global": max(float(item["mpm_max_speed"]) for item in diagnostics),
        "projected_mass": max(float(item["projected_mass"]) for item in diagnostics),
        "active_cell_count": max(int(item["active_cell_count"]) for item in diagnostics),
        "cell_force_max_norm": max(float(item["cell_force_max_norm"]) for item in diagnostics),
        "hydro_force_max_norm": max(float(item["hydro_force_max_norm"]) for item in diagnostics),
        "bb_link_count_min": min(int(item["bb_link_count"]) for item in post_step_rows),
        "bb_link_count_max": max(int(item["bb_link_count"]) for item in post_step_rows),
        "active_reaction_particle_count_max": max(int(item["active_reaction_particle_count"]) for item in post_step_rows),
        "area_scale_final": area["area_scale_final"],
        "area_scale_min": area["area_scale_min"],
        "area_scale_max": area["area_scale_max"],
        "raw_area_scale_final": area["raw_area_scale_final"],
        "has_nan": False,
        "has_inf": False,
        "stable": True,
        "notes": "Step 26 very short controlled real geometry feasibility; not real squid validation",
    }
    row["has_nan"] = not _finite_values(row, excluded=_short_driver_string_fields())
    row["has_inf"] = row["has_nan"]
    row["stable"] = bool(not row["has_nan"] and not row["has_inf"])
    return row


def compare_step25_projection_smoke(step25_csv, step26_csv) -> dict:
    step25_rows = {row["candidate_id"]: row for row in _read_csv(step25_csv)}
    step26_rows = {
        row["candidate_id"]: row
        for row in _read_csv(step26_csv)
        if int(float(row["n_grid"])) == 32
    }
    rows = []
    for candidate_id, step25_row in sorted(step25_rows.items()):
        if candidate_id not in step26_rows:
            raise RuntimeError(f"missing Step 26 32^3 projection row for {candidate_id}")
        step26_row = step26_rows[candidate_id]
        row = {
            "candidate_id": candidate_id,
            "geometry_type": step26_row["geometry_type"],
            "projected_mass_delta": float(step26_row["projected_mass"]) - float(step25_row["projected_mass"]),
            "active_cell_count_delta": int(float(step26_row["active_cell_count"]))
            - int(float(step25_row["active_cell_count"])),
            "solid_phi_min_delta": float(step26_row["solid_phi_min"]) - float(step25_row["solid_phi_min"]),
            "solid_phi_max_delta": float(step26_row["solid_phi_max"]) - float(step25_row["solid_phi_max"]),
            "projection_pass_both": _as_bool(step25_row["projection_pass"]) and _as_bool(step26_row["projection_pass"]),
        }
        row["regression_pass"] = bool(
            abs(row["projected_mass_delta"]) <= 1.0e-6
            and row["active_cell_count_delta"] == 0
            and row["solid_phi_min_delta"] == 0.0
            and row["solid_phi_max_delta"] == 0.0
            and row["projection_pass_both"]
        )
        rows.append(row)
    return {
        "compared_row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["regression_pass"]),
        "rows": rows,
    }


def assert_short_driver_row(row):
    if not row["stable"]:
        raise RuntimeError(f"Step 26 short driver row is not stable: {row}")
    if row["quality_check_enabled"] is not True or row["quality_check_strict"] is not True:
        raise RuntimeError(f"Step 26 short driver row must use strict quality checks: {row}")
    if row["quality_gate_strict"] is not True or row["quality_pass"] is not True:
        raise RuntimeError(f"Step 26 strict quality gate failed: {row}")
    if row["quality_severity"] != "ok":
        raise RuntimeError(f"Step 26 quality severity must be ok: {row}")
    if int(row["quality_warnings_count"]) != 0 or int(row["quality_reasons_count"]) != 0:
        raise RuntimeError(f"Step 26 quality report must have zero warnings/reasons: {row}")
    if int(row["completed_lbm_steps"]) < 5 or int(row["total_mpm_substeps"]) < 25:
        raise RuntimeError(f"Step 26 driver row did not finish configured short run: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 26 driver density out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 26 driver velocity out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 26 driver MPM diagnostics out of range: {row}")
    if float(row["projected_mass"]) <= 0.0 or int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 26 driver projection diagnostics invalid: {row}")
    _assert_mode_specific(row)


def _assert_mode_specific(row):
    mode = row["mode"]
    transfer = row["reaction_transfer_mode"]
    if mode == "none":
        if float(row["cell_force_max_norm"]) != 0.0 or int(row["bb_link_count_max"]) != 0:
            raise RuntimeError(f"Step 26 none row has coupling side effects: {row}")
    if mode == "penalty":
        if float(row["cell_force_max_norm"]) <= 0.0 or float(row["hydro_force_max_norm"]) <= 0.0:
            raise RuntimeError(f"Step 26 penalty row lacks positive force diagnostics: {row}")
        if int(row["bb_link_count_max"]) != 0:
            raise RuntimeError(f"Step 26 penalty row must not use moving-boundary links: {row}")
    if mode == "moving_boundary":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError(f"Step 26 moving-boundary row must keep cell force at zero: {row}")
        if float(row["hydro_force_max_norm"]) <= 0.0:
            raise RuntimeError(f"Step 26 moving-boundary row lacks positive hydrodynamic force diagnostics: {row}")
        if int(row["bb_link_count_max"]) <= 0 or int(row["active_reaction_particle_count_max"]) <= 0:
            raise RuntimeError(f"Step 26 moving-boundary row lacks reaction diagnostics: {row}")
        if transfer == "link_area_experimental":
            if not (0.25 <= float(row["area_scale_final"]) <= 2.0):
                raise RuntimeError(f"Step 26 link-area row area scale out of range: {row}")


def _enforce_short_driver_config(config, config_path):
    if int(config.n_grid) != 48:
        raise RuntimeError(f"{config_path} must use n_grid=48")
    if int(config.n_lbm_steps) != 5 or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 5 LBM steps and 5 MPM substeps")
    if config.write_vtk or config.write_particles:
        raise RuntimeError(f"{config_path} must disable VTK and particle outputs")
    if not config.quality_check_enabled or not config.quality_check_strict:
        raise RuntimeError(f"{config_path} must enable strict quality checks")


def _area_stats(driver, config):
    if config.reaction_transfer_mode != "link_area_experimental":
        return {
            "area_scale_final": 1.0,
            "area_scale_min": 1.0,
            "area_scale_max": 1.0,
            "raw_area_scale_final": 1.0,
        }
    stats = driver.link_area_coupler.get_stats()
    return {
        "area_scale_final": float(stats["area_scale"]),
        "area_scale_min": float(stats["area_scale_min"]),
        "area_scale_max": float(stats["area_scale_max"]),
        "raw_area_scale_final": float(stats["raw_area_scale"]),
    }


def _candidate_id_from_path(path) -> str:
    name = Path(os.fspath(path)).stem
    for prefix in ("step26_real_candidate_", "step26_projection_", "step26_driver_"):
        if name.startswith(prefix):
            name = name[len(prefix) :]
    for suffix in ("_geometry", "_32", "_48", "_64", "_48_none", "_48_penalty", "_48_moving_boundary", "_48_link_area"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    if name.startswith("smoke_"):
        return "real_candidate_" + name
    if name.startswith("real_candidate_"):
        return name
    return name


def _finite_values(row, excluded=()) -> bool:
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def _short_driver_string_fields():
    return {
        "candidate_id",
        "geometry_type",
        "geometry_source",
        "mode",
        "reaction_transfer_mode",
        "quality_check_enabled",
        "quality_check_strict",
        "quality_pass",
        "quality_severity",
        "quality_gate_strict",
        "quality_report_path",
        "driver_timing_path",
        "has_nan",
        "has_inf",
        "stable",
        "notes",
    }


def _stats_has_nan(stats) -> bool:
    return any(np.isnan(float(value)) for value in stats.values())


def _stats_has_inf(stats) -> bool:
    return any(np.isinf(float(value)) for value in stats.values())


def _read_csv(path):
    with _resolve_path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_json(path):
    with _resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _relative_path(path) -> str:
    return os.path.relpath(_resolve_path(path), _repo_root()).replace("\\", "/")


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
