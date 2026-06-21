import hashlib
import json
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D
from src.mpm_lbm.sim.geometry.candidate_manifest import candidate_manifest_row, load_candidate_descriptor, validate_candidate_descriptor
from src.mpm_lbm.sim.geometry.normalization import (
    geometry_config_from_descriptor,
    normalize_mesh_candidate,
    normalize_voxel_candidate,
    write_normalization_report,
)
from src.mpm_lbm.sim.geometry.quality import GeometryQualityGate, analyze_geometry_config


def run_candidate_intake(descriptor_path, out_dir) -> dict:
    descriptor = _load_valid_descriptor(descriptor_path)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    row = candidate_manifest_row(descriptor_path, root=_repo_root())
    quality = run_candidate_quality_check(descriptor_path, out_path / descriptor["candidate_id"])
    normalization = _normalization_for_descriptor(descriptor)
    normalization_path = out_path / descriptor["candidate_id"] / "normalization_report.json"
    write_normalization_report(normalization, normalization_path)
    summary = {
        "candidate_id": descriptor["candidate_id"],
        "geometry_type": descriptor["geometry_type"],
        "manifest_pass": bool(row["manifest_pass"]),
        "quality_pass": bool(quality["quality_pass"]),
        "quality_severity": quality["quality_severity"],
        "normalization_pass": bool(normalization["normalized_inside_domain"]),
        "source_file": row["source_file_redacted"],
        "normalization_report_path": _relative_path(normalization_path),
        "quality_report_path": quality["quality_report_path"],
        "scope_note": "Step 25 intake only; no FSI driver validation and no real squid validation claim",
    }
    _write_json(out_path / descriptor["candidate_id"] / "intake_summary.json", summary)
    return summary


def run_candidate_quality_check(descriptor_path, out_dir) -> dict:
    descriptor = _load_valid_descriptor(descriptor_path)
    config = geometry_config_from_descriptor(descriptor)
    report = analyze_geometry_config(config)
    gate = GeometryQualityGate(strict=True).evaluate(report)
    payload = {"report": report, "gate": gate}

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    report_path = out_path / "geometry_quality_report.json"
    _write_json(report_path, payload)
    if gate.get("pass") is not True or gate.get("severity") != "ok":
        raise RuntimeError(f"candidate quality gate failed for {descriptor['candidate_id']}: {gate}")
    return {
        "candidate_id": descriptor["candidate_id"],
        "geometry_type": descriptor["geometry_type"],
        "quality_kind": report.get("quality_kind", ""),
        "quality_pass": bool(gate["pass"]),
        "quality_severity": gate["severity"],
        "quality_warnings_count": len(gate.get("warnings", [])),
        "quality_reasons_count": len(gate.get("reasons", [])),
        "quality_report_path": _relative_path(report_path),
        "vertices_count": int(report.get("vertices_count", 0)),
        "faces_count": int(report.get("faces_count", 0)),
        "has_valid_face_indices": bool(report.get("has_valid_face_indices", False)),
        "degenerate_face_count": int(report.get("degenerate_face_count", 0)),
        "boundary_edge_count": int(report.get("boundary_edge_count", 0)),
        "nonmanifold_edge_count": int(report.get("nonmanifold_edge_count", 0)),
        "occupied_count": int(report.get("occupied_count", 0)),
        "connected_component_count": int(report.get("connected_component_count", 0)),
        "largest_component_fraction": float(report.get("largest_component_fraction", 0.0)),
        "touches_domain_boundary": bool(report.get("touches_domain_boundary", False)),
    }


def run_candidate_sampling_reproducibility(descriptor_path, out_dir) -> dict:
    descriptor = _load_valid_descriptor(descriptor_path)
    config = geometry_config_from_descriptor(descriptor)
    first = GeometrySampler3D(config).sample_particles()
    second = GeometrySampler3D(config).sample_particles()
    row = _sampling_row(descriptor, first, second)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    _write_json(out_path / f"{descriptor['candidate_id']}_sampling_reproducibility.json", row)
    if not row["reproducibility_pass"]:
        raise RuntimeError(f"sampling reproducibility failed for {descriptor['candidate_id']}: {row}")
    return row


def run_candidate_projection_smoke(descriptor_path, out_dir) -> dict:
    descriptor = _load_valid_descriptor(descriptor_path)
    config = geometry_config_from_descriptor(descriptor)
    sample = GeometrySampler3D(config).sample_particles()

    import taichi as ti

    from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D
    from src.mpm_lbm.sim.mpm.solid import MPMSolid3D
    from src.mpm_lbm.sim.coupling.projection import MPMToLBMProjector3D
    from src.mpm_lbm.sim.io.run_utils import make_all_fluid_geo
    from src.mpm_lbm.sim.drivers.sim_config import UnifiedSimConfig

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    try:
        ti.init(arch=ti.cpu, random_seed=0, print_ir=False, offline_cache=False, log_level=ti.ERROR)
    except RuntimeError:
        ti.reset()
        ti.init(arch=ti.cpu, random_seed=0, print_ir=False, offline_cache=False, log_level=ti.ERROR)

    sim_config = UnifiedSimConfig(n_grid=32, mpm_substeps_per_lbm_step=1)
    geo_path = out_path / f"{descriptor['candidate_id']}_all_fluid.dat"
    make_all_fluid_geo(str(geo_path), sim_config.n_grid)
    lbm = LBMFluid3D(sim_config.make_lbm_config())
    lbm.init_geo(str(geo_path))
    lbm.init_simulation()

    solid = MPMSolid3D(sim_config.make_mpm_config(gravity=(0.0, 0.0, 0.0)), int(descriptor["n_particles"]))
    solid.init_from_numpy(sample["x"], sample["vol0"], sample["mass"])
    projector = MPMToLBMProjector3D(sim_config)
    projector.project(solid, lbm)
    stats = projector.get_stats()
    phi = lbm.solid_phi.to_numpy()
    row = {
        "candidate_id": descriptor["candidate_id"],
        "geometry_type": descriptor["geometry_type"],
        "projected_mass": float(stats["projected_mass"]),
        "projected_volume_raw": float(stats["projected_volume_raw"]),
        "projected_volume_clamped": float(stats["projected_volume_clamped"]),
        "max_phi_raw": float(stats["max_phi_raw"]),
        "active_cell_count": int(stats["active_cell_count"]),
        "solid_phi_min": float(np.min(phi)),
        "solid_phi_max": float(np.max(phi)),
        "has_nan": bool(np.isnan(phi).any() or any(np.isnan(float(v)) for v in stats.values())),
        "has_inf": bool(np.isinf(phi).any() or any(np.isinf(float(v)) for v in stats.values())),
        "scope_note": "projection-only smoke diagnostics; no FSI driver long-run and no real squid validation claim",
    }
    row["projection_pass"] = bool(
        row["projected_mass"] > 0.0
        and row["active_cell_count"] > 0
        and row["solid_phi_min"] >= 0.0
        and row["solid_phi_max"] <= 1.0
        and not row["has_nan"]
        and not row["has_inf"]
    )
    _write_json(out_path / f"{descriptor['candidate_id']}_projection_smoke.json", row)
    if not row["projection_pass"]:
        raise RuntimeError(f"projection smoke failed for {descriptor['candidate_id']}: {row}")
    ti.reset()
    return row


def _load_valid_descriptor(descriptor_path) -> dict:
    return validate_candidate_descriptor(load_candidate_descriptor(descriptor_path), descriptor_path=descriptor_path)


def _normalization_for_descriptor(descriptor):
    if descriptor["geometry_type"] == "mesh":
        return normalize_mesh_candidate(descriptor)
    if descriptor["geometry_type"] == "voxel":
        return normalize_voxel_candidate(descriptor)
    raise ValueError(f"unsupported geometry_type: {descriptor['geometry_type']}")


def _sampling_row(descriptor, first, second) -> dict:
    mass_sum_first = float(np.sum(first["mass"]))
    mass_sum_second = float(np.sum(second["mass"]))
    rel_mass_error = abs(mass_sum_first - mass_sum_second) / max(abs(mass_sum_first), 1.0e-12)
    row = {
        "candidate_id": descriptor["candidate_id"],
        "geometry_type": descriptor["geometry_type"],
        "particle_count_first": int(len(first["x"])),
        "particle_count_second": int(len(second["x"])),
        "geometry_volume_first": float(first["geometry_volume"]),
        "geometry_volume_second": float(second["geometry_volume"]),
        "mass_sum_first": mass_sum_first,
        "mass_sum_second": mass_sum_second,
        "sampled_position_hash_first": _array_hash(first["x"]),
        "sampled_position_hash_second": _array_hash(second["x"]),
        "vol0_hash_first": _array_hash(first["vol0"]),
        "vol0_hash_second": _array_hash(second["vol0"]),
        "mass_hash_first": _array_hash(first["mass"]),
        "mass_hash_second": _array_hash(second["mass"]),
        "relative_mass_error": float(rel_mass_error),
    }
    row["reproducibility_pass"] = bool(
        row["particle_count_first"] == row["particle_count_second"]
        and row["geometry_volume_first"] == row["geometry_volume_second"]
        and row["mass_sum_first"] == row["mass_sum_second"]
        and row["sampled_position_hash_first"] == row["sampled_position_hash_second"]
        and row["vol0_hash_first"] == row["vol0_hash_second"]
        and row["mass_hash_first"] == row["mass_hash_second"]
        and np.isfinite(row["relative_mass_error"])
    )
    return row


def _array_hash(values) -> str:
    arr = np.ascontiguousarray(values)
    return hashlib.sha256(arr.tobytes()).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _relative_path(path) -> str:
    return os.path.relpath(path, _repo_root()).replace("\\", "/")


def _write_json(path, data):
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
