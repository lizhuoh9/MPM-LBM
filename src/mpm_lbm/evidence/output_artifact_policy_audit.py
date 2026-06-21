from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step70_output_artifact_policy_audit(
    root: Path,
    policy_path: str = "configs/step70_output_artifact_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [
        bool_policy_row("vtr_default_allowed", policy["vtr_default_allowed"], False),
        bool_policy_row("particle_npy_default_allowed", policy["particle_npy_default_allowed"], False),
        bool_policy_row("default_write_vtk_allowed", policy["default_write_vtk_allowed"], False),
        bool_policy_row("default_write_particles_allowed", policy["default_write_particles_allowed"], False),
        bool_policy_row("protected_external_edit_allowed", policy["external_taichi_lbm3d_edit_allowed"], False),
        bool_policy_row("protected_real_geometry_edit_allowed", policy["real_geometry_candidates_edit_allowed"], False),
        bool_policy_row("report_consistency_required", policy["report_consistency_guard_required"], True),
        bool_policy_row("artifact_manifest_required", policy["artifact_manifest_required"], True),
        bool_policy_row("private_absolute_paths_allowed", policy["private_absolute_paths_allowed"], False),
        bool_policy_row("driver_run_outputs_committable", policy["driver_run_outputs_committable"], False),
    ]
    forbidden_dirs = [path for path in policy["forbidden_step70_output_dirs"] if (root / path).exists()]
    protected_step70_files = protected_related_files(root, policy["protected_prefixes"])
    step70_related = step70_related_files(root)
    vtr_files = [path for path in step70_related if path.lower().endswith(".vtr")]
    particle_npy_files = [
        path for path in step70_related if path.lower().endswith(".npy") and "particle" in path.lower()
    ]
    rows.extend(absence_row("forbidden_step70_output_dir", path) for path in forbidden_dirs)
    rows.extend(absence_row("protected_step70_file", path) for path in protected_step70_files)
    rows.extend(absence_row("step70_vtr_file", path) for path in vtr_files)
    rows.extend(absence_row("step70_particle_npy_file", path) for path in particle_npy_files)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "vtr_default_allowed": bool(policy["vtr_default_allowed"]),
        "particle_npy_default_allowed": bool(policy["particle_npy_default_allowed"]),
        "protected_external_edit_allowed": bool(policy["external_taichi_lbm3d_edit_allowed"]),
        "protected_real_geometry_edit_allowed": bool(policy["real_geometry_candidates_edit_allowed"]),
        "report_consistency_required": bool(policy["report_consistency_guard_required"]),
        "artifact_manifest_required": bool(policy["artifact_manifest_required"]),
        "forbidden_step70_output_dir_count": len(forbidden_dirs),
        "protected_step70_file_count": len(protected_step70_files),
        "step70_vtr_count": len(vtr_files),
        "step70_particle_npy_count": len(particle_npy_files),
        "output_artifact_policy_audit_pass": False,
    }
    summary["output_artifact_policy_audit_pass"] = bool(
        all(row["pass"] for row in rows)
        and not summary["vtr_default_allowed"]
        and not summary["particle_npy_default_allowed"]
        and not summary["protected_external_edit_allowed"]
        and not summary["protected_real_geometry_edit_allowed"]
        and summary["report_consistency_required"]
        and summary["artifact_manifest_required"]
        and summary["forbidden_step70_output_dir_count"] == 0
        and summary["protected_step70_file_count"] == 0
        and summary["step70_vtr_count"] == 0
        and summary["step70_particle_npy_count"] == 0
    )
    return rows, summary


def bool_policy_row(name: str, actual: bool, expected: bool) -> dict:
    return {
        "check": name,
        "actual": bool(actual),
        "expected": bool(expected),
        "path": "",
        "pass": bool(actual) is bool(expected),
    }


def absence_row(name: str, path: str) -> dict:
    return {
        "check": name,
        "actual": True,
        "expected": False,
        "path": path,
        "pass": False,
    }


def step70_related_files(root: Path) -> list[str]:
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "step70" in rel.lower() or "api_config_freeze" in rel.lower():
            rows.append(rel)
    return sorted(rows)


def protected_related_files(root: Path, protected_prefixes: list[str]) -> list[str]:
    return [
        rel
        for rel in step70_related_files(root)
        if any(rel.startswith(prefix) for prefix in protected_prefixes)
    ]
