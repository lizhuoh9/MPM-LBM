import csv
from dataclasses import replace
import json
import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import FSIDriver3D, FSIDriverConfig  # noqa: E402
from src.geometry_config import GeometryConfig  # noqa: E402
from src.geometry_quality import GeometryQualityGate, analyze_geometry_config  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


STEP24_CONFIGS = [
    "configs/step24_strict_voxel_sphere_48_moving_boundary.json",
    "configs/step24_strict_voxel_sphere_48_link_area.json",
    "configs/step24_strict_mesh_cube_48_moving_boundary.json",
    "configs/step24_strict_mesh_cube_48_link_area.json",
    "configs/step24_strict_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step24_strict_mesh_ellipsoid_48_link_area.json",
    "configs/step24_strict_voxel_sphere_64_moving_boundary.json",
    "configs/step24_strict_mesh_cube_64_moving_boundary.json",
    "configs/step24_strict_mesh_cube_64_link_area.json",
]


STEP24_DRIVER_FIELDS = [
    "case",
    "geometry_type",
    "geometry_source",
    "quality_kind",
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
    "stable",
    "notes",
]


STEP24_OUTPUT_ROOTS = [
    "outputs/step24_strict_voxel_sphere_48_long",
    "outputs/step24_strict_mesh_cube_48_long",
    "outputs/step24_strict_mesh_ellipsoid_48_long",
    "outputs/step24_strict_imported_geometry_64_feasibility",
]


STEP24_DRIVER_CSVS = [
    "outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv",
    "outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv",
]


def load_driver_config(relative_path):
    return FSIDriverConfig.from_json(os.path.join(ROOT, relative_path))


def read_csv_rows(path):
    resolved = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with open(resolved, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    resolved = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with open(resolved, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_log(relative_path, lines):
    path = os.path.join(ROOT, relative_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    normalized = [str(line).rstrip() for line in lines]
    with open(path, "w", encoding="utf-8") as f:
        for line in normalized:
            f.write(line + "\n")


def write_step24_rows(rows, csv_path, npz_path):
    write_rows_csv_npz(rows, csv_path, npz_path, STEP24_DRIVER_FIELDS)


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    save_csv_rows(normalized, csv_path, fieldnames=fieldnames)

    payload = {"columns": np.asarray(fieldnames)}
    for field in fieldnames:
        values = [row.get(field, "") for row in normalized]
        if _is_string_field(field, values):
            payload[field + "s"] = np.asarray([str(value) for value in values])
            continue
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            payload[field + "s"] = np.asarray([str(value) for value in values])
    np.savez(npz_path, **payload)


def make_strict_quality_gated_config(base_config_path, out_config_path, n_lbm_steps, mpm_substeps):
    data = read_json(base_config_path)
    updated = dict(data)
    updated["quality_check_enabled"] = True
    updated["quality_check_strict"] = True
    updated["write_vtk"] = False
    updated["write_particles"] = False
    updated["n_lbm_steps"] = int(n_lbm_steps)
    updated["mpm_substeps_per_lbm_step"] = int(mpm_substeps)

    out_path = os.path.join(ROOT, out_config_path)
    write_json(out_path, updated)
    return updated


def enforce_step24_config(config, config_path):
    if not config.quality_check_enabled:
        raise RuntimeError(f"{config_path} must set quality_check_enabled=true")
    if not config.quality_check_strict:
        raise RuntimeError(f"{config_path} must set quality_check_strict=true")
    if config.write_vtk or config.write_particles:
        raise RuntimeError(f"{config_path} must disable write_vtk and write_particles")
    if config.coupling_mode != "moving_boundary":
        raise RuntimeError(f"{config_path} must use coupling_mode=moving_boundary")
    if config.reaction_transfer_mode not in {"engineering", "link_area_experimental"}:
        raise RuntimeError(f"{config_path} has invalid reaction_transfer_mode")
    if config.reaction_transfer_mode == "link_area_experimental":
        if config.link_area_policy != "inverse_length":
            raise RuntimeError(f"{config_path} link-area rows must use inverse_length policy")
        if float(config.link_area_scale_min) != 0.25 or float(config.link_area_scale_max) != 2.0:
            raise RuntimeError(f"{config_path} link-area rows must preserve area scale bounds [0.25, 2.0]")
    if config.n_grid not in {48, 64}:
        raise RuntimeError(f"{config_path} n_grid must be 48 or 64")
    if int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} n_particles must be 4096")
    if int(config.n_grid) == 48:
        if int(config.n_lbm_steps) < 30 or int(config.mpm_substeps_per_lbm_step) < 10:
            raise RuntimeError(f"{config_path} 48^3 rows must use at least 30 LBM steps and 10 MPM substeps")
    if int(config.n_grid) == 64:
        if int(config.n_lbm_steps) < 5 or int(config.mpm_substeps_per_lbm_step) < 5:
            raise RuntimeError(f"{config_path} 64^3 rows must use at least 5 LBM steps and 5 MPM substeps")
    if not config.geometry_config_path:
        raise RuntimeError(f"{config_path} must reference an imported geometry config")
    if "external/taichi_LBM3D" in config_path.replace("\\", "/"):
        raise RuntimeError(f"{config_path} must not live under external/taichi_LBM3D")


def run_strict_config_paths(case, config_paths, out_dir, csv_name, npz_name):
    rows = []
    for relative_path in config_paths:
        config = load_driver_config(relative_path)
        row = run_strict_quality_gated_driver_case(
            relative_path,
            case,
            config,
            os.path.join(out_dir, case_output_name(case, config)),
        )
        rows.append(row)
        print(_format_driver_row(row))

    write_step24_rows(rows, os.path.join(out_dir, csv_name), os.path.join(out_dir, npz_name))
    if not all(_as_bool(row["stable"]) for row in rows):
        raise RuntimeError(f"not all Step 24 rows are stable for {case}")
    return rows


def run_mixed_strict_config_paths(case_config_paths, out_dir, csv_name, npz_name):
    rows = []
    for case, relative_path in case_config_paths:
        config = load_driver_config(relative_path)
        row = run_strict_quality_gated_driver_case(
            relative_path,
            case,
            config,
            os.path.join(out_dir, case_output_name(case, config)),
        )
        rows.append(row)
        print(_format_driver_row(row))

    write_step24_rows(rows, os.path.join(out_dir, csv_name), os.path.join(out_dir, npz_name))
    if not all(_as_bool(row["stable"]) for row in rows):
        raise RuntimeError("not all Step 24 mixed driver rows are stable")
    return rows


def run_strict_quality_gated_driver_case(config_path, case, config, out_dir):
    enforce_step24_config(config, config_path)
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for {case}/{config.coupling_mode}")

    report_path = os.path.join(out_dir, "geometry_quality_report.json")
    report_payload = collect_geometry_quality_report(out_dir)
    timing_path = os.path.join(out_dir, "driver_timing.json")
    write_json(timing_path, driver.performance_row())
    row = summarize_long_run_row(case, config, diagnostics, driver, report_payload, report_path, timing_path)
    assert_step24_row_stable(row)
    return row


def collect_geometry_quality_report(out_dir):
    report_path = os.path.join(out_dir, "geometry_quality_report.json")
    if not os.path.isfile(report_path):
        raise RuntimeError(f"missing geometry_quality_report.json under {out_dir}")
    payload = read_json(report_path)
    if "report" not in payload or "gate" not in payload:
        raise RuntimeError(f"invalid quality report payload: {report_path}")
    if payload["gate"].get("strict") is not True:
        raise RuntimeError(f"Step 24 report must be strict: {report_path}")
    return payload


def summarize_long_run_row(case, config, diagnostics, driver, report_payload, report_path, timing_path):
    gate = report_payload["gate"]
    report = report_payload["report"]
    post_step_rows = [row for row in diagnostics if int(row["step"]) > 0]
    if not post_step_rows:
        raise RuntimeError(f"missing post-step diagnostics for {case}")

    area_stats = _area_stats(driver, config)
    row = {
        "case": case,
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path or config.geometry_type,
        "quality_kind": report.get("quality_kind", ""),
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "quality_check_enabled": bool(config.quality_check_enabled),
        "quality_check_strict": bool(config.quality_check_strict),
        "quality_pass": bool(gate.get("pass", False)),
        "quality_severity": gate.get("severity", ""),
        "quality_warnings_count": len(gate.get("warnings", [])),
        "quality_reasons_count": len(gate.get("reasons", [])),
        "quality_gate_strict": bool(gate.get("strict", False)),
        "quality_report_path": _relative_path(report_path),
        "driver_timing_path": _relative_path(timing_path),
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "completed_lbm_steps": max(int(row["step"]) for row in diagnostics),
        "total_mpm_substeps": max(int(row["total_mpm_substeps"]) for row in diagnostics),
        "rho_min_global": min(float(row["rho_min"]) for row in diagnostics),
        "rho_max_global": max(float(row["rho_max"]) for row in diagnostics),
        "lbm_max_v_global": max(float(row["lbm_max_v"]) for row in diagnostics),
        "mpm_min_J_global": min(float(row["mpm_min_J"]) for row in diagnostics),
        "mpm_max_speed_global": max(float(row["mpm_max_speed"]) for row in diagnostics),
        "projected_mass": max(float(row["projected_mass"]) for row in diagnostics),
        "active_cell_count": max(int(row["active_cell_count"]) for row in diagnostics),
        "cell_force_max_norm": max(float(row["cell_force_max_norm"]) for row in diagnostics),
        "hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in diagnostics),
        "bb_link_count_min": min(int(row["bb_link_count"]) for row in post_step_rows),
        "bb_link_count_max": max(int(row["bb_link_count"]) for row in post_step_rows),
        "active_reaction_particle_count_max": max(int(row["active_reaction_particle_count"]) for row in post_step_rows),
        "area_scale_final": area_stats["area_scale_final"],
        "area_scale_min": area_stats["area_scale_min"],
        "area_scale_max": area_stats["area_scale_max"],
        "raw_area_scale_final": area_stats["raw_area_scale_final"],
        "stable": True,
        "notes": "Step 24 strict quality-gated synthetic imported geometry long-run validation; no new FSI physics",
    }
    return row


def assert_step24_row_stable(row):
    _assert_row_finite(
        row,
        excluded=(
            "case",
            "geometry_type",
            "geometry_source",
            "quality_kind",
            "mode",
            "reaction_transfer_mode",
            "quality_check_enabled",
            "quality_check_strict",
            "quality_pass",
            "quality_severity",
            "quality_gate_strict",
            "quality_report_path",
            "driver_timing_path",
            "stable",
            "notes",
        ),
    )
    if not _as_bool(row["stable"]):
        raise RuntimeError(f"unstable Step 24 driver row: {row}")
    if not _as_bool(row["quality_check_enabled"]) or not _as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 24 row must use strict quality checks: {row}")
    if not _as_bool(row["quality_gate_strict"]):
        raise RuntimeError(f"Step 24 row must have gate.strict=true: {row}")
    if not _as_bool(row["quality_pass"]):
        raise RuntimeError(f"quality gate failed unexpectedly: {row}")
    if row["quality_severity"] != "ok":
        raise RuntimeError(f"unexpected strict quality severity: {row}")
    if int(row["quality_reasons_count"]) != 0 or int(row["quality_warnings_count"]) != 0:
        raise RuntimeError(f"strict quality report must have no reasons or warnings: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"rho outside accepted range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"lbm_max_v exceeded accepted range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0:
        raise RuntimeError(f"mpm_min_J became non-positive: {row}")
    if float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"mpm_max_speed exceeded accepted range: {row}")
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")
    if int(row["completed_lbm_steps"]) < int(row["n_lbm_steps"]):
        raise RuntimeError(f"row did not complete configured LBM steps: {row}")
    expected_mpm_substeps = int(row["n_lbm_steps"]) * int(row["mpm_substeps_per_lbm_step"])
    if int(row["total_mpm_substeps"]) < expected_mpm_substeps:
        raise RuntimeError(f"row did not complete configured MPM substeps: {row}")
    if float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("Step 24 moving_boundary row must keep cell_force at zero")
    if int(row["bb_link_count_min"]) <= 0 or int(row["bb_link_count_max"]) <= 0:
        raise RuntimeError(f"moving_boundary row must record positive bounce-back links: {row}")
    if int(row["active_reaction_particle_count_max"]) <= 0:
        raise RuntimeError(f"moving_boundary row must record active reaction particles: {row}")
    if row["reaction_transfer_mode"] == "engineering":
        if float(row["area_scale_final"]) != 1.0:
            raise RuntimeError(f"engineering row must record neutral area scale: {row}")
    if row["reaction_transfer_mode"] == "link_area_experimental":
        if not (float(row["area_scale_min"]) >= 0.25 and float(row["area_scale_max"]) <= 2.0):
            raise RuntimeError(f"link-area bounds are outside expected range: {row}")
        if not (0.25 <= float(row["area_scale_final"]) <= 2.0):
            raise RuntimeError(f"link-area final scale is outside expected bounds: {row}")
    if not os.path.isfile(os.path.join(ROOT, row["quality_report_path"])):
        raise RuntimeError(f"missing quality report path: {row['quality_report_path']}")
    if not os.path.isfile(os.path.join(ROOT, row["driver_timing_path"])):
        raise RuntimeError(f"missing driver timing path: {row['driver_timing_path']}")


def make_nonstrict_quality_report_for_config(config_path, out_path):
    config = load_driver_config(config_path)
    if not config.geometry_config_path:
        raise RuntimeError(f"{config_path} does not reference imported geometry")
    geometry_config = GeometryConfig.from_json(os.path.join(ROOT, config.geometry_config_path))
    nonstrict_config = replace(geometry_config, quality_check_enabled=True, quality_check_strict=False)
    report = analyze_geometry_config(nonstrict_config)
    gate = GeometryQualityGate(strict=False).evaluate(report)
    payload = {"report": report, "gate": gate}
    write_json(out_path, payload)
    return payload


def read_step24_driver_rows():
    rows = []
    for csv_path in STEP24_DRIVER_CSVS:
        rows.extend(read_csv_rows(csv_path))
    return rows


def quality_report_paths_from_rows(rows):
    return [os.path.join(ROOT, row["quality_report_path"]) for row in rows]


def case_output_name(case, config):
    return f"{case}_{config.n_grid}_{config.coupling_mode}_{config.reaction_transfer_mode}"


def driver_output_dir(root, row):
    return os.path.join(
        ROOT,
        root,
        f"{row['case']}_{int(float(row['n_grid']))}_{row['mode']}_{row['reaction_transfer_mode']}",
    )


def row_key(row):
    return (
        row["case"],
        row["mode"],
        row["reaction_transfer_mode"],
        int(float(row["n_grid"])),
    )


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


def _format_driver_row(row):
    return (
        f"case={row['case']}, transfer={row['reaction_transfer_mode']}, "
        f"strict={row['quality_check_strict']}, n_grid={row['n_grid']}, "
        f"rho=[{float(row['rho_min_global']):.9e}, {float(row['rho_max_global']):.9e}], "
        f"lbm_max_v={float(row['lbm_max_v_global']):.9e}, "
        f"mpm_min_J={float(row['mpm_min_J_global']):.9e}, "
        f"bb_links=[{row['bb_link_count_min']}, {row['bb_link_count_max']}], "
        f"stable={row['stable']}"
    )


def _assert_row_finite(row, excluded=()):
    values = []
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        values.append(float(value))
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"row contains NaN or Inf: {row}")


def _is_string_field(field, values):
    if field in {
        "case",
        "geometry_type",
        "geometry_source",
        "quality_kind",
        "mode",
        "reaction_transfer_mode",
        "quality_severity",
        "quality_report_path",
        "driver_timing_path",
        "notes",
    }:
        return True
    for value in values:
        if value == "":
            continue
        try:
            _bool_to_float(value)
        except (TypeError, ValueError):
            return True
    return False


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")
