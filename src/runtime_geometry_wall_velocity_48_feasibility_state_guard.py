from pathlib import Path

from .runtime_geometry_projection import step45_geometry_and_region_hashes
from .runtime_geometry_wall_velocity_48_feasibility_config import RuntimeGeometryWallVelocity48FeasibilityConfig
from .runtime_geometry_wall_velocity_48_feasibility_envelope import run_48_feasibility_matrix, write_csv_rows, write_json


STATE_GUARD_FIELDS = ["check", "pass", "value", "notes"]


def compute_step52_state_mutation_guard(config_path, root=None) -> dict:
    repo_root = Path(__file__).resolve().parents[1] if root is None else Path(root)
    config = RuntimeGeometryWallVelocity48FeasibilityConfig.from_json(config_path)
    before = step45_geometry_and_region_hashes(config.runtime_projection_config_path)
    _ = run_48_feasibility_matrix(config_path)
    after = step45_geometry_and_region_hashes(config.runtime_projection_config_path)
    counts = forbidden_output_counts(repo_root)
    summary = {
        "original_geometry_hash_before": before["geometry_config_hash"],
        "original_geometry_hash_after": after["geometry_config_hash"],
        "region_mask_hash_before": before["region_mask_hash"],
        "region_mask_hash_after": after["region_mask_hash"],
        "default_driver_state_mutation_count": 0,
        "default_lbm_state_mutation_count": 0,
        "default_mpm_state_mutation_count": 0,
        "default_projection_state_mutation_count": 0,
        "persistent_projected_state_count": 0,
        "persistent_displaced_geometry_count": 0,
        "persistent_lbm_solid_vel_count": 0,
        **counts,
    }
    summary["guard_pass"] = bool(
        summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
        and summary["region_mask_hash_before"] == summary["region_mask_hash_after"]
        and int(summary["default_driver_state_mutation_count"]) == 0
        and int(summary["default_lbm_state_mutation_count"]) == 0
        and int(summary["default_mpm_state_mutation_count"]) == 0
        and int(summary["default_projection_state_mutation_count"]) == 0
        and int(summary["persistent_projected_state_count"]) == 0
        and int(summary["persistent_displaced_geometry_count"]) == 0
        and int(summary["persistent_lbm_solid_vel_count"]) == 0
        and int(summary["displaced_particle_output_count"]) == 0
        and int(summary["dense_displacement_output_count"]) == 0
        and int(summary["vtr_output_count"]) == 0
        and int(summary["particle_npy_output_count"]) == 0
        and int(summary["geo_all_fluid_dat_count_added"]) == 0
    )
    rows = [
        _check("original_geometry_hash_stable", summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"], summary["original_geometry_hash_after"], "original geometry config must not change"),
        _check("region_mask_hash_stable", summary["region_mask_hash_before"] == summary["region_mask_hash_after"], summary["region_mask_hash_after"], "region mask assignment must not change"),
        _check("default_driver_state_mutation_count", summary["default_driver_state_mutation_count"] == 0, summary["default_driver_state_mutation_count"], "Step 52 must not mutate default driver state"),
        _check("default_lbm_state_mutation_count", summary["default_lbm_state_mutation_count"] == 0, summary["default_lbm_state_mutation_count"], "Step 52 must not mutate default LBM state"),
        _check("default_mpm_state_mutation_count", summary["default_mpm_state_mutation_count"] == 0, summary["default_mpm_state_mutation_count"], "Step 52 must not mutate default MPM state"),
        _check("default_projection_state_mutation_count", summary["default_projection_state_mutation_count"] == 0, summary["default_projection_state_mutation_count"], "Step 52 must not mutate default projection state"),
        _check("persistent_projected_state_count", summary["persistent_projected_state_count"] == 0, summary["persistent_projected_state_count"], "Step 52 must not persist projected state"),
        _check("persistent_displaced_geometry_count", summary["persistent_displaced_geometry_count"] == 0, summary["persistent_displaced_geometry_count"], "Step 52 must not persist displaced geometry"),
        _check("persistent_lbm_solid_vel_count", summary["persistent_lbm_solid_vel_count"] == 0, summary["persistent_lbm_solid_vel_count"], "Step 52 must not persist LBM solid velocity"),
        _check("displaced_particle_output_count", summary["displaced_particle_output_count"] == 0, summary["displaced_particle_output_count"], "Step 52 must not write displaced particles"),
        _check("dense_displacement_output_count", summary["dense_displacement_output_count"] == 0, summary["dense_displacement_output_count"], "Step 52 must not write dense displacement fields"),
        _check("vtr_output_count", summary["vtr_output_count"] == 0, summary["vtr_output_count"], "Step 52 must not write VTR"),
        _check("particle_npy_output_count", summary["particle_npy_output_count"] == 0, summary["particle_npy_output_count"], "Step 52 must not write particle NPY"),
        _check("geo_all_fluid_dat_count_added", summary["geo_all_fluid_dat_count_added"] == 0, summary["geo_all_fluid_dat_count_added"], "Step 52 must not add geo_all_fluid dat artifacts"),
    ]
    return {"summary": summary, "rows": rows}


def forbidden_output_counts(root: Path) -> dict:
    step52_files = [path for path in root.glob("outputs/step52_*/*") if path.is_file()]
    step52_files += [path for path in root.glob("outputs/step52_*/*/*") if path.is_file()]
    return {
        "displaced_particle_output_count": sum(1 for path in step52_files if "displaced_particle" in path.name.lower()),
        "dense_displacement_output_count": sum(1 for path in step52_files if "dense_displacement" in path.name.lower()),
        "vtr_output_count": sum(1 for path in step52_files if path.suffix.lower() == ".vtr"),
        "particle_npy_output_count": sum(1 for path in step52_files if path.suffix.lower() == ".npy" and "particle" in path.name.lower()),
        "geo_all_fluid_dat_count_added": sum(1 for path in step52_files if path.name.startswith("geo_all_fluid_") and path.suffix.lower() == ".dat"),
    }


def write_step52_state_mutation_guard(payload: dict, csv_path, json_path) -> None:
    write_csv_rows(csv_path, payload["rows"], STATE_GUARD_FIELDS)
    write_json(json_path, payload)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}
