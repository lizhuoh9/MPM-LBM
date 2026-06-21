from __future__ import annotations

import json
from pathlib import Path


def build_step68_step_specific_proxy_policy_audit(
    root: Path,
    policy_path: str = "configs/step68_step_specific_proxy_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    inventory = read_json(root / policy["inventory_source"])
    inventory_rows = [
        row
        for row in inventory["rows"]
        if row["classification"] == "step_specific_proxy_remaining"
        and row["target_owner"] == "experiments/steps"
        and row["recommended_step"] == "Step68"
    ]
    inventory_paths = {row["path"] for row in inventory_rows}
    policy_paths = {migration["legacy_path"] for migration in policy["migrations"]}
    missing_inventory_paths = sorted(inventory_paths - policy_paths)
    extra_policy_paths = sorted(policy_paths - inventory_paths)
    rows = [
        policy_row(migration, inventory_paths, inventory_rows)
        for migration in policy["migrations"]
    ]
    summary = {
        "inventory_source": policy["inventory_source"],
        "inventory_step_specific_proxy_remaining_count": len(inventory_rows),
        "policy_migration_count": len(policy["migrations"]),
        "missing_inventory_paths": missing_inventory_paths,
        "extra_policy_paths": extra_policy_paths,
        "missing_inventory_path_count": len(missing_inventory_paths),
        "extra_policy_path_count": len(extra_policy_paths),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "runtime_code_changed": bool(policy["runtime_code_changed"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "step68_proxy_policy_audit_pass": False,
    }
    summary["step68_proxy_policy_audit_pass"] = bool(
        summary["inventory_step_specific_proxy_remaining_count"] == policy["expected_inventory_count"]
        and summary["policy_migration_count"] == summary["inventory_step_specific_proxy_remaining_count"]
        and summary["missing_inventory_path_count"] == 0
        and summary["extra_policy_path_count"] == 0
        and summary["row_count"] == summary["pass_count"]
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def policy_row(migration: dict, inventory_paths: set[str], inventory_rows: list[dict]) -> dict:
    matching = next((row for row in inventory_rows if row["path"] == migration["legacy_path"]), {})
    in_inventory = migration["legacy_path"] in inventory_paths
    target_owner_ok = matching.get("target_owner") == "experiments/steps"
    recommended_step_ok = matching.get("recommended_step") == "Step68"
    passed = bool(in_inventory and target_owner_ok and recommended_step_ok)
    return {
        "legacy_path": migration["legacy_path"],
        "experiment_path": migration["experiment_path"],
        "package": migration["package"],
        "in_inventory": in_inventory,
        "target_owner": matching.get("target_owner", ""),
        "target_owner_ok": target_owner_ok,
        "recommended_step": matching.get("recommended_step", ""),
        "recommended_step_ok": recommended_step_ok,
        "pass": passed,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
