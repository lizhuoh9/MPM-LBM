from dataclasses import replace
import csv
import json
import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import (  # noqa: E402
    FSIDiagnostics3D,
    FSIDriver3D,
    FSIDriverConfig,
    GeometryConfig,
    GeometryQualityGate,
    GeometrySampler3D,
    LBMFluid3D,
    MPMToLBMProjector3D,
    MPMSolid3D,
    UnifiedSimConfig,
    analyze_geometry_config,
)
from src.run_utils import assert_no_nan_inf_array, make_all_fluid_geo, save_csv_rows  # noqa: E402


MESH_QUALITY_FIELDS = [
    "case",
    "geometry_type",
    "quality_kind",
    "pass",
    "severity",
    "vertices_count",
    "faces_count",
    "bounds_min_x",
    "bounds_min_y",
    "bounds_min_z",
    "bounds_max_x",
    "bounds_max_y",
    "bounds_max_z",
    "bounds_span_x",
    "bounds_span_y",
    "bounds_span_z",
    "has_finite_vertices",
    "has_valid_face_indices",
    "duplicate_vertex_count",
    "degenerate_face_count",
    "zero_area_face_count",
    "boundary_edge_count",
    "nonmanifold_edge_count",
    "is_watertight_proxy",
    "surface_area",
    "volume_signed",
    "volume_abs",
    "orientation_consistent_proxy",
    "euler_characteristic",
    "stable",
    "notes",
]


VOXEL_QUALITY_FIELDS = [
    "case",
    "geometry_type",
    "quality_kind",
    "pass",
    "severity",
    "shape_x",
    "shape_y",
    "shape_z",
    "occupied_count",
    "occupied_fraction",
    "empty",
    "bounds_index_min_x",
    "bounds_index_min_y",
    "bounds_index_min_z",
    "bounds_index_max_x",
    "bounds_index_max_y",
    "bounds_index_max_z",
    "bbox_size_x",
    "bbox_size_y",
    "bbox_size_z",
    "touches_domain_boundary",
    "connected_component_count",
    "largest_component_size",
    "largest_component_fraction",
    "surface_voxel_count",
    "interior_voxel_count",
    "stable",
    "notes",
]


BAD_GEOMETRY_FIELDS = [
    "case",
    "geometry_type",
    "quality_kind",
    "strict_pass",
    "expected_failure",
    "loader_expected_failure",
    "severity",
    "boundary_edge_count",
    "nonmanifold_edge_count",
    "degenerate_face_count",
    "occupied_count",
    "connected_component_count",
    "reasons",
    "stable",
    "notes",
]


RESOLUTION_SENSITIVITY_FIELDS = [
    "case",
    "geometry_type",
    "particles_per_axis_hint",
    "mesh_voxel_resolution",
    "geometry_volume",
    "projected_mass",
    "relative_mass_error",
    "active_cell_count",
    "occupied_count",
    "stable",
    "notes",
]


DRIVER_QUALITY_FIELDS = [
    "case",
    "geometry_type",
    "geometry_source",
    "mode",
    "reaction_transfer_mode",
    "quality_gate_pass",
    "quality_gate_severity",
    "n_grid",
    "n_particles",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "stable",
    "notes",
]


def load_geometry_config(relative_path):
    return GeometryConfig.from_json(os.path.join(ROOT, relative_path))


def load_driver_config(relative_path):
    return FSIDriverConfig.from_json(os.path.join(ROOT, relative_path))


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    save_csv_rows(normalized, csv_path, fieldnames=fieldnames)

    payload = {"columns": np.asarray(fieldnames)}
    for string_key in (
        "case",
        "geometry_type",
        "quality_kind",
        "severity",
        "geometry_source",
        "mode",
        "reaction_transfer_mode",
        "quality_gate_severity",
        "stable",
        "notes",
        "reasons",
    ):
        if any(string_key in row for row in normalized):
            payload[string_key + "s"] = np.asarray([str(row.get(string_key, "")) for row in normalized])

    for field in fieldnames:
        values = [row.get(field, "") for row in normalized]
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(npz_path, **payload)


def quality_row(case, config, strict=False):
    report = analyze_geometry_config(config)
    gate = GeometryQualityGate(strict=strict).evaluate(report)
    row = {"case": case}
    row.update(report)
    row["pass"] = bool(gate["pass"])
    row["severity"] = gate["severity"]
    return row, {"report": report, "gate": gate}


def bad_geometry_row(case, config):
    report = analyze_geometry_config(config)
    gate = GeometryQualityGate(strict=True).evaluate(report)
    loader_expected_failure = bool(report.get("loader_error", ""))
    row = {
        "case": case,
        "geometry_type": report.get("geometry_type", config.geometry_type),
        "quality_kind": report.get("quality_kind", ""),
        "strict_pass": bool(gate["pass"]),
        "expected_failure": bool(not gate["pass"] or loader_expected_failure),
        "loader_expected_failure": loader_expected_failure,
        "severity": gate["severity"],
        "boundary_edge_count": int(report.get("boundary_edge_count", 0)),
        "nonmanifold_edge_count": int(report.get("nonmanifold_edge_count", 0)),
        "degenerate_face_count": int(report.get("degenerate_face_count", 0)),
        "occupied_count": int(report.get("occupied_count", 0)),
        "connected_component_count": int(report.get("connected_component_count", 0)),
        "reasons": "; ".join(gate["reasons"]),
        "stable": True,
        "notes": "expected strict quality-gate failure for intentionally bad Step 22 fixture",
    }
    return row, {"report": report, "gate": gate}


def build_projection_harness(out_dir, n_particles=4096, n_grid=32):
    os.makedirs(out_dir, exist_ok=True)
    sim = UnifiedSimConfig(n_grid=n_grid, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=5)
    geo_path = os.path.join(out_dir, f"geo_all_fluid_{n_grid}.dat")
    make_all_fluid_geo(geo_path, n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(gravity=(0.0, 0.0, 0.0), box_min=(0.25, 0.25, 0.25), box_max=(0.75, 0.75, 0.75)),
        n_particles=n_particles,
    )
    projector = MPMToLBMProjector3D(sim)
    return {"sim": sim, "lbm": lbm, "solid": solid, "projector": projector}


def run_resolution_projection_case(case, config, harness):
    sampler = GeometrySampler3D(config)
    cloud = sampler.sample_particles()
    x = np.asarray(cloud["x"])
    mass = np.asarray(cloud["mass"], dtype=np.float64)
    assert_no_nan_inf_array("particles_x", x)
    assert_no_nan_inf_array("particle_mass", mass)

    solid = harness["solid"]
    lbm = harness["lbm"]
    projector = harness["projector"]
    solid.init_from_numpy(cloud["x"], cloud["vol0"], cloud["mass"])
    projector.project(solid, lbm)
    stats = projector.get_stats()
    projected_mass = float(stats["projected_mass"])
    particle_mass_sum = float(np.sum(mass))
    relative_mass_error = abs(projected_mass - particle_mass_sum) / max(particle_mass_sum, 1.0e-12)
    occupied_count = int(sampler.voxelize(32)["occupied_count"])

    row = {
        "case": case,
        "geometry_type": config.geometry_type,
        "particles_per_axis_hint": int(config.particles_per_axis_hint),
        "mesh_voxel_resolution": int(config.mesh_voxel_resolution),
        "geometry_volume": float(cloud["geometry_volume"]),
        "projected_mass": projected_mass,
        "relative_mass_error": float(relative_mass_error),
        "active_cell_count": int(stats["active_cell_count"]),
        "occupied_count": occupied_count,
        "stable": True,
        "notes": "Step 22 sampling and projection resolution sensitivity",
    }
    assert_resolution_row(row)
    return row


def run_driver_quality_case(case, config, out_dir):
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for {case}")
    if driver.geometry_quality_report is None:
        raise RuntimeError(f"missing geometry quality report for {case}")
    gate = driver.geometry_quality_report["gate"]
    row = summarize_driver_quality_case(case, config, diagnostics, gate)
    assert_driver_quality_row(row)
    return row


def summarize_driver_quality_case(case, config, diagnostics, gate):
    return {
        "case": case,
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path or config.geometry_type,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "quality_gate_pass": bool(gate["pass"]),
        "quality_gate_severity": gate["severity"],
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "completed_lbm_steps": max(int(row["step"]) for row in diagnostics),
        "total_mpm_substeps": max(int(row["total_mpm_substeps"]) for row in diagnostics),
        "rho_min": min(float(row["rho_min"]) for row in diagnostics),
        "rho_max": max(float(row["rho_max"]) for row in diagnostics),
        "lbm_max_v": max(float(row["lbm_max_v"]) for row in diagnostics),
        "mpm_min_J": min(float(row["mpm_min_J"]) for row in diagnostics),
        "mpm_max_speed": max(float(row["mpm_max_speed"]) for row in diagnostics),
        "projected_mass": max(float(row["projected_mass"]) for row in diagnostics),
        "active_cell_count": max(int(row["active_cell_count"]) for row in diagnostics),
        "cell_force_max_norm": max(float(row["cell_force_max_norm"]) for row in diagnostics),
        "hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in diagnostics),
        "bb_link_count": max(int(row["bb_link_count"]) for row in diagnostics),
        "stable": True,
        "notes": "Step 22 driver quality gate smoke; no new FSI physics",
    }


def assert_resolution_row(row):
    _assert_row_finite(row, excluded=("case", "geometry_type", "stable", "notes"))
    if float(row["geometry_volume"]) <= 0.0:
        raise RuntimeError(f"geometry_volume must be positive: {row}")
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")


def assert_driver_quality_row(row):
    _assert_row_finite(
        row,
        excluded=(
            "case",
            "geometry_type",
            "geometry_source",
            "mode",
            "reaction_transfer_mode",
            "quality_gate_pass",
            "quality_gate_severity",
            "stable",
            "notes",
        ),
    )
    if not _as_bool(row["quality_gate_pass"]):
        raise RuntimeError(f"quality gate failed unexpectedly: {row}")
    if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
        raise RuntimeError(f"rho outside accepted range: {row}")
    if float(row["lbm_max_v"]) >= 0.1:
        raise RuntimeError(f"lbm_max_v exceeded accepted range: {row}")
    if float(row["mpm_min_J"]) <= 0.0:
        raise RuntimeError(f"mpm_min_J became non-positive: {row}")
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")


def replace_geometry_config(config, **kwargs):
    return replace(config, **kwargs)


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
