from __future__ import annotations

import ast
import json
from pathlib import Path


def build_step68_experiment_boundary_audit(
    root: Path,
    policy_path: str = "configs/step68_experiment_boundary_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    migration_policy = read_json(root / policy["migration_policy_path"])
    executable_files = step68_executable_files(root, policy)
    rows = [boundary_row(path, root) for path in executable_files]
    quarantined_path = root / policy["quarantined_driver_helper_path"]
    quarantined_helper_hits = forbidden_driver_calls(quarantined_path) if quarantined_path.is_file() else []
    protected_hits = protected_status_hits(root, policy)
    driver_dirs = [path for path in policy["forbidden_output_dirs"] if (root / path).exists()]
    vtr_hits = list((root / "outputs").glob("step68*/**/*.vtr")) if (root / "outputs").exists() else []
    particle_npy_hits = [
        path for path in (root / "outputs").glob("step68*/**/*.npy") if "particle" in path.name.lower()
    ] if (root / "outputs").exists() else []
    real_geometry_under_sim = root / "src" / "mpm_lbm" / "sim" / "geometry" / "real_geometry_feasibility.py"
    experiment_paths = [root / migration["experiment_path"] for migration in migration_policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "driver_run_call_count": sum(int(row["driver_run_call_count"]) for row in rows),
        "driver_initialize_call_count": sum(int(row["driver_initialize_call_count"]) for row in rows),
        "driver_step_once_call_count": sum(int(row["driver_step_once_call_count"]) for row in rows),
        "quarantined_driver_helper_count": len(quarantined_helper_hits),
        "quarantined_driver_helper_executed": False,
        "step68_driver_run_output_dir_count": len(driver_dirs),
        "step68_vtr_count": len(vtr_hits),
        "step68_particle_npy_count": len(particle_npy_hits),
        "protected_external_edit_count": protected_hits["external"],
        "protected_real_geometry_candidate_edit_count": protected_hits["real_geometry"],
        "real_geometry_feasibility_under_sim": real_geometry_under_sim.exists(),
        "experiment_file_count": sum(1 for path in experiment_paths if path.is_file()),
        "runtime_code_changed": bool(policy["runtime_code_changed"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "experiment_boundary_audit_pass": False,
    }
    summary["experiment_boundary_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["driver_run_call_count"] == 0
        and summary["driver_initialize_call_count"] == 0
        and summary["driver_step_once_call_count"] == 0
        and not summary["quarantined_driver_helper_executed"]
        and summary["step68_driver_run_output_dir_count"] == 0
        and summary["step68_vtr_count"] == 0
        and summary["step68_particle_npy_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and not summary["real_geometry_feasibility_under_sim"]
        and summary["experiment_file_count"] == len(migration_policy["migrations"])
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def step68_executable_files(root: Path, policy: dict) -> list[Path]:
    files = set()
    for pattern in policy["scan_globs"]:
        for path in root.glob(pattern):
            if path.is_file():
                files.add(path)
    return sorted(files)


def boundary_row(path: Path, root: Path) -> dict:
    hits = forbidden_driver_calls(path)
    run_hits = [hit for hit in hits if hit.endswith(":run")]
    initialize_hits = [hit for hit in hits if hit.endswith(":initialize")]
    step_once_hits = [hit for hit in hits if hit.endswith(":step_once")]
    return {
        "path": path.relative_to(root).as_posix(),
        "driver_run_call_count": len(run_hits),
        "driver_initialize_call_count": len(initialize_hits),
        "driver_step_once_call_count": len(step_once_hits),
        "driver_call_hits": hits,
        "pass": not hits,
    }


def forbidden_driver_calls(path: Path) -> list[str]:
    if not path.is_file():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"run", "initialize", "step_once"}:
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "driver":
            hits.append(f"{path.as_posix()}:{node.lineno}:{node.func.attr}")
        elif isinstance(node.func.value, ast.Call) and is_fsi_driver_constructor(node.func.value):
            hits.append(f"{path.as_posix()}:{node.lineno}:{node.func.attr}")
    return hits


def is_fsi_driver_constructor(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name):
        return node.func.id == "FSIDriver3D"
    if isinstance(node.func, ast.Attribute):
        return node.func.attr == "FSIDriver3D"
    return False


def protected_status_hits(root: Path, policy: dict) -> dict[str, int]:
    counts = {"external": 0, "real_geometry": 0}
    for prefix in policy["protected_prefixes"]:
        protected = root / prefix
        if not protected.exists():
            continue
        marker = "external" if "external/taichi_LBM3D" in prefix else "real_geometry"
        step68_hits = [path for path in protected.rglob("*") if path.is_file() and "step68" in path.as_posix().lower()]
        counts[marker] += len(step68_hits)
    return counts


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
