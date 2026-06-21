from __future__ import annotations

import json
from pathlib import Path


def build_geo_path_naming_audit(
    root: Path,
    policy_path: str = "configs/step59_geo_path_naming_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [geo_path_row(root, item) for item in policy["cases"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "constructor_created_file_count": sum(1 for row in rows if row["output_dir_exists_after"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "geo_path_naming_audit_pass": False,
    }
    summary["geo_path_naming_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["constructor_created_file_count"] == 0
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def geo_path_row(root: Path, item: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    n_grid = int(item["n_grid"])
    expected_filename = item["expected_filename"]
    out_dir = root / "outputs" / "step59_geo_path_naming_audit" / f"constructor_probe_n{n_grid}"
    output_dir_exists_before = out_dir.exists()
    driver = FSIDriver3D(
        FSIDriverConfig(n_grid=n_grid, n_lbm_steps=1, write_vtk=False, write_particles=False),
        out_dir=str(out_dir),
    )
    output_dir_exists_after = out_dir.exists()
    actual_filename = Path(driver.geo_path).name
    geo_path = Path(driver.geo_path)
    try:
        recorded_geo_path = geo_path.relative_to(root).as_posix()
    except ValueError:
        recorded_geo_path = geo_path.name
    passed = bool(
        actual_filename == expected_filename
        and not output_dir_exists_before
        and not output_dir_exists_after
    )
    return {
        "n_grid": n_grid,
        "expected_filename": expected_filename,
        "actual_filename": actual_filename,
        "geo_path": recorded_geo_path,
        "output_dir_exists_before": output_dir_exists_before,
        "output_dir_exists_after": output_dir_exists_after,
        "pass": passed,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
