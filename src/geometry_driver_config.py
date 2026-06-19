import json
import os
from pathlib import Path

from .fsi_config import FSIDriverConfig
from .geometry_candidate_manifest import load_candidate_descriptor, validate_candidate_descriptor
from .geometry_config import GeometryConfig


VALIDATION_SCOPE = "intake_qa_normalization_sampling_projection_only"
ARTIFACT_POLICY = "no_vtk_no_particles_no_large_raw_geometry"


def geometry_config_payload_from_candidate_descriptor(descriptor: dict) -> dict:
    payload = _validated_step26_descriptor(descriptor)
    geometry_config = {
        "geometry_type": payload["geometry_type"],
        "n_particles": int(payload["n_particles"]),
        "geometry_file": payload["source_file"],
        "normalize_to_domain": bool(payload["normalize_to_domain"]),
        "preserve_aspect_ratio": bool(payload["preserve_aspect_ratio"]),
        "padding": float(payload["padding"]),
        "quality_check_enabled": True,
        "quality_check_strict": True,
        "deterministic": True,
        "p_rho": float(payload.get("p_rho", 1.0)),
    }
    if payload["geometry_type"] == "mesh":
        geometry_config["mesh_inside_method"] = payload.get("mesh_inside_method", "ray_cast")
        geometry_config["mesh_voxel_resolution"] = int(payload.get("mesh_voxel_resolution", 32))
    if payload["geometry_type"] == "voxel":
        geometry_config["metadata_file"] = payload.get("metadata_file")
        geometry_config["voxel_threshold"] = float(payload.get("voxel_threshold", 0.5))

    GeometryConfig(**geometry_config)
    return geometry_config


def write_geometry_config_from_descriptor(descriptor_path: str, out_config_path: str) -> dict:
    descriptor = load_candidate_descriptor(descriptor_path)
    payload = geometry_config_payload_from_candidate_descriptor(descriptor)
    _write_json(out_config_path, payload)
    GeometryConfig.from_json(_resolve_path(out_config_path))
    return payload


def driver_config_payload_for_candidate(
    geometry_config_path: str,
    coupling_mode: str,
    reaction_transfer_mode: str,
    n_grid: int,
    n_lbm_steps: int,
    mpm_substeps_per_lbm_step: int,
) -> dict:
    geometry_config = GeometryConfig.from_json(_resolve_path(geometry_config_path))
    payload = {
        "coupling_mode": coupling_mode,
        "geometry_type": geometry_config.geometry_type,
        "geometry_config_path": _repo_relative_path(geometry_config_path),
        "n_grid": int(n_grid),
        "n_particles": int(geometry_config.n_particles),
        "n_lbm_steps": int(n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(mpm_substeps_per_lbm_step),
        "target_u_lbm": [0.003, 0.0, 0.0],
        "gravity": [0.0, 0.0, 0.0],
        "penalty_force_cap_lbm": 5.0e-5,
        "mb_force_cap_norm": 1.0e-5,
        "reaction_transfer_mode": reaction_transfer_mode,
        "link_area_policy": "inverse_length",
        "link_area_scale_min": 0.25,
        "link_area_scale_max": 2.0,
        "output_interval": int(n_lbm_steps),
        "write_vtk": False,
        "write_particles": False,
        "quality_check_enabled": True,
        "quality_check_strict": True,
    }
    FSIDriverConfig(**payload)
    _enforce_step26_driver_payload(payload)
    return payload


def _validated_step26_descriptor(descriptor: dict) -> dict:
    payload = validate_candidate_descriptor(descriptor)
    if payload["validation_scope"] != VALIDATION_SCOPE:
        raise ValueError(f"Step 26 descriptor validation_scope must be {VALIDATION_SCOPE}")
    if payload["quality_check_enabled"] is not True:
        raise ValueError("Step 26 descriptor must enable quality_check_enabled")
    if payload["quality_check_strict"] is not True:
        raise ValueError("Step 26 descriptor must enable quality_check_strict")
    if payload.get("artifact_policy") != ARTIFACT_POLICY:
        raise ValueError(f"Step 26 descriptor artifact_policy must be {ARTIFACT_POLICY}")
    return payload


def _enforce_step26_driver_payload(payload: dict):
    if payload["quality_check_enabled"] is not True or payload["quality_check_strict"] is not True:
        raise ValueError("Step 26 driver payload must preserve strict quality gate")
    if payload["write_vtk"] is not False or payload["write_particles"] is not False:
        raise ValueError("Step 26 driver payload must disable VTK and particle outputs")
    if int(payload["n_grid"]) != 48:
        raise ValueError("Step 26 driver payload must use 48^3 grid")
    if int(payload["n_lbm_steps"]) != 5 or int(payload["mpm_substeps_per_lbm_step"]) != 5:
        raise ValueError("Step 26 driver payload must stay very short: 5 LBM steps and 5 MPM substeps")
    if payload["coupling_mode"] != "moving_boundary" and payload["reaction_transfer_mode"] != "engineering":
        raise ValueError("non-moving-boundary Step 26 driver rows must use engineering reaction_transfer_mode")


def _write_json(path, data):
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _repo_relative_path(path) -> str:
    resolved = _resolve_path(path)
    return os.path.relpath(resolved, _repo_root()).replace("\\", "/")


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
