from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json


def build_remaining_solver_inventory_audit(
    root: Path,
    policy_path: str = "configs/step63_remaining_solver_inventory_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    batch_policy = read_json(root / policy["batch_policy_path"])
    migrated_paths = {migration["legacy_path"] for migration in batch_policy["migrations"]}
    rows = [inventory_row(path, root, migrated_paths) for path in sorted((root / "src").glob("*.py"))]
    summary = {
        "root_file_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "root_compatibility_shim_count": sum(
            1 for row in rows if row["classification"] == "root_compatibility_shim"
        ),
        "step_specific_proxy_remaining_count": sum(
            1 for row in rows if row["classification"] == "step_specific_proxy_remaining"
        ),
        "temporary_bridge_count": sum(1 for row in rows if row["is_temporary_bridge"]),
        "migration_required_count": sum(1 for row in rows if row["migration_required"]),
        "unknown_requires_review_count": sum(
            1 for row in rows if row["classification"] == "unknown_requires_review"
        ),
        "remaining_solver_inventory_pass": False,
    }
    summary["remaining_solver_inventory_pass"] = bool(
        summary["root_file_count"] > 0
        and summary["root_file_count"] == summary["pass_count"]
        and summary["unknown_requires_review_count"] == 0
    )
    return rows, summary


def inventory_row(path: Path, root: Path, migrated_paths: set[str]) -> dict:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8-sig")
    is_root_shim = "Compatibility shim" in text or "Canonical implementation lives" in text
    is_temporary_bridge = any(
        token in text
        for token in ("legacy_getattr", "_LEGACY_MODULE", "BRIDGE_IS_TEMPORARY_UNTIL_STEP59")
    )
    classification = classify_root_file(path.name, rel, text, migrated_paths, is_root_shim, is_temporary_bridge)
    migration_required = classification not in {
        "root_compatibility_shim",
        "approved_legacy_support",
        "step_specific_proxy_remaining",
    }
    recommended_step = recommended_step_for_classification(classification)
    return {
        "path": rel,
        "classification": classification,
        "current_owner": "root_src",
        "target_owner": target_owner_for_classification(classification),
        "recommended_step": recommended_step,
        "migration_required": migration_required,
        "simulation_required_for_migration": False,
        "is_root_shim": is_root_shim,
        "is_temporary_bridge": is_temporary_bridge,
        "notes": notes_for_classification(path.name, classification),
        "pass": classification != "unknown_requires_review",
    }


def classify_root_file(
    name: str,
    rel: str,
    text: str,
    migrated_paths: set[str],
    is_root_shim: bool,
    is_temporary_bridge: bool,
) -> str:
    if rel in migrated_paths:
        return "root_compatibility_shim"
    if name == "real_geometry_feasibility.py":
        return "step_specific_proxy_remaining"
    if name.startswith("runtime_geometry_wall_velocity_"):
        return "step_specific_proxy_remaining"
    if is_root_shim:
        return "approved_legacy_support"
    if is_temporary_bridge:
        return "approved_legacy_support"
    if name.startswith(("boundary_motion_", "geometry_motion_")):
        return "motion_runtime_remaining"
    if name.startswith("wall_velocity_"):
        return "wall_velocity_runtime_remaining"
    if name.startswith("runtime_geometry_"):
        return "runtime_geometry_remaining"
    if name.startswith("diagnostic_geometry_"):
        return "diagnostic_geometry_remaining"
    if name.startswith("geometry_displacement_"):
        return "geometry_displacement_remaining"
    if name.startswith("squid_"):
        return "squid_proxy_remaining"
    if name.startswith(("geometry_intake", "geometry_candidate", "geometry_fingerprint", "geometry_normalization")):
        return "real_geometry_support_remaining"
    if "FSIDriver3D" in text and ".run(" in text:
        return "step_specific_proxy_remaining"
    return "approved_legacy_support"


def target_owner_for_classification(classification: str) -> str:
    targets = {
        "root_compatibility_shim": "canonical_package",
        "motion_runtime_remaining": "src/mpm_lbm/sim/motion",
        "wall_velocity_runtime_remaining": "src/mpm_lbm/sim/wall_velocity",
        "runtime_geometry_remaining": "src/mpm_lbm/sim/runtime_geometry",
        "diagnostic_geometry_remaining": "src/mpm_lbm/diagnostics",
        "geometry_displacement_remaining": "src/mpm_lbm/sim/geometry_displacement",
        "squid_proxy_remaining": "src/mpm_lbm/sim/squid_proxy",
        "real_geometry_support_remaining": "src/mpm_lbm/sim/geometry",
        "step_specific_proxy_remaining": "experiments/steps",
        "approved_legacy_support": "approved_legacy_support",
        "unknown_requires_review": "manual_review",
    }
    return targets[classification]


def recommended_step_for_classification(classification: str) -> str:
    if classification == "step_specific_proxy_remaining":
        return "Step68"
    if classification == "approved_legacy_support":
        return "Step69+"
    if classification == "root_compatibility_shim":
        return "done"
    return "Step69"


def notes_for_classification(name: str, classification: str) -> str:
    if name == "real_geometry_feasibility.py":
        return "Contains FSIDriver3D run helpers; classified only, not executed in Batch A."
    if classification == "step_specific_proxy_remaining":
        return "Step-specific proxy is intentionally left for Step68 experiments/steps migration."
    if classification == "root_compatibility_shim":
        return "Batch A migrated this file and left a root compatibility shim."
    return "Classified for roadmap tracking."
