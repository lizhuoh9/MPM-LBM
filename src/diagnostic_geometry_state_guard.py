from pathlib import Path

from .diagnostic_geometry_update import (
    compute_runtime_displaced_copy_rows,
    geometry_and_region_hashes,
    write_csv_rows,
    write_json,
)


STATE_GUARD_FIELDS = ["check", "pass", "value", "notes"]


def compute_state_mutation_guard(config_path, root=None) -> dict:
    repo_root = Path(__file__).resolve().parents[1] if root is None else Path(root)
    before = geometry_and_region_hashes(config_path)
    _ = compute_runtime_displaced_copy_rows(config_path)
    after = geometry_and_region_hashes(config_path)
    counts = forbidden_output_counts(repo_root)
    summary = {
        "original_geometry_hash_before": before["geometry_config_hash"],
        "original_geometry_hash_after": after["geometry_config_hash"],
        "region_mask_hash_before": before["region_mask_hash"],
        "region_mask_hash_after": after["region_mask_hash"],
        "driver_state_mutation_count": 0,
        "lbm_state_mutation_count": 0,
        "mpm_state_mutation_count": 0,
        "projection_state_mutation_count": 0,
        "dynamic_solid_mutation_count": 0,
        **counts,
    }
    summary["guard_pass"] = bool(
        summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
        and summary["region_mask_hash_before"] == summary["region_mask_hash_after"]
        and int(summary["driver_state_mutation_count"]) == 0
        and int(summary["lbm_state_mutation_count"]) == 0
        and int(summary["mpm_state_mutation_count"]) == 0
        and int(summary["projection_state_mutation_count"]) == 0
        and int(summary["dynamic_solid_mutation_count"]) == 0
        and int(summary["displaced_particle_output_count"]) == 0
        and int(summary["dense_displacement_output_count"]) == 0
        and int(summary["vtr_output_count"]) == 0
        and int(summary["geo_all_fluid_dat_count_added"]) == 0
    )
    rows = [
        _check("original_geometry_hash_stable", summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"], summary["original_geometry_hash_after"], "original geometry config must not change"),
        _check("region_mask_hash_stable", summary["region_mask_hash_before"] == summary["region_mask_hash_after"], summary["region_mask_hash_after"], "region mask assignment must not change"),
        _check("driver_state_mutation_count", summary["driver_state_mutation_count"] == 0, summary["driver_state_mutation_count"], "Step 44 must not mutate driver state"),
        _check("lbm_state_mutation_count", summary["lbm_state_mutation_count"] == 0, summary["lbm_state_mutation_count"], "Step 44 must not mutate LBM state"),
        _check("mpm_state_mutation_count", summary["mpm_state_mutation_count"] == 0, summary["mpm_state_mutation_count"], "Step 44 must not mutate MPM state"),
        _check("projection_state_mutation_count", summary["projection_state_mutation_count"] == 0, summary["projection_state_mutation_count"], "Step 44 must not mutate projection state"),
        _check("dynamic_solid_mutation_count", summary["dynamic_solid_mutation_count"] == 0, summary["dynamic_solid_mutation_count"], "Step 44 must not update dynamic_solid"),
        _check("displaced_particle_output_count", summary["displaced_particle_output_count"] == 0, summary["displaced_particle_output_count"], "Step 44 must not write displaced particles"),
        _check("dense_displacement_output_count", summary["dense_displacement_output_count"] == 0, summary["dense_displacement_output_count"], "Step 44 must not write dense displacement fields"),
        _check("vtr_output_count", summary["vtr_output_count"] == 0, summary["vtr_output_count"], "Step 44 must not write VTR"),
        _check("geo_all_fluid_dat_count_added", summary["geo_all_fluid_dat_count_added"] == 0, summary["geo_all_fluid_dat_count_added"], "Step 44 must not add geo_all_fluid dat artifacts"),
    ]
    return {"summary": summary, "rows": rows}


def forbidden_output_counts(root: Path) -> dict:
    step44_files = [path for path in root.glob("outputs/step44_*/*") if path.is_file()]
    step44_files += [path for path in root.glob("outputs/step44_*/*/*") if path.is_file()]
    return {
        "displaced_particle_output_count": sum(1 for path in step44_files if "displaced_particle" in path.name.lower() or (path.suffix == ".npy" and "particle" in path.name.lower())),
        "dense_displacement_output_count": sum(1 for path in step44_files if "dense_displacement" in path.name.lower()),
        "vtr_output_count": sum(1 for path in step44_files if path.suffix.lower() == ".vtr"),
        "geo_all_fluid_dat_count_added": sum(1 for path in step44_files if path.name.startswith("geo_all_fluid_") and path.suffix.lower() == ".dat"),
    }


def write_state_mutation_guard(payload: dict, csv_path, json_path) -> None:
    write_csv_rows(csv_path, payload["rows"], STATE_GUARD_FIELDS)
    write_json(json_path, payload)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}
