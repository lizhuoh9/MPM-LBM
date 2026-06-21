from __future__ import annotations

import ast
import importlib
from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import batch_symbol_pairs, output_snapshot, read_json


def build_batch_behavior_preservation_audit(root: Path, policy_path: str) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [
        policy_boolean_row("runtime_code_changed", False, bool(policy["runtime_code_changed"])),
        policy_boolean_row("solver_behavior_changed", False, bool(policy["solver_behavior_changed"])),
        policy_boolean_row("physics_feature_expansion", False, bool(policy["physics_feature_expansion"])),
        policy_boolean_row("no_runtime_execution", True, bool(policy["no_runtime_execution"])),
        policy_boolean_row("no_solver_activation", True, bool(policy["no_solver_activation"])),
        import_side_effect_row(root, policy),
        symbol_identity_row(policy),
        forbidden_driver_call_row(root, policy),
        forbidden_output_dirs_absent_row(root),
        real_geometry_feasibility_classification_row(root),
    ]
    summary = {
        "policy_id": policy["policy_id"],
        "step": int(policy["step"]),
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "solver_object_construction_required": False,
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "batch_behavior_preservation_audit_pass": False,
    }
    summary["batch_behavior_preservation_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and not summary["solver_object_construction_required"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def policy_boolean_row(check: str, expected: bool, actual: bool) -> dict:
    return {
        "check": check,
        "expected": expected,
        "actual": actual,
        "pass": expected is actual,
        "notes": "policy-level behavior preservation flag",
    }


def import_side_effect_row(root: Path, policy: dict) -> dict:
    before = output_snapshot(root)
    modules = sorted(
        {migration["canonical_module"] for migration in policy["migrations"]}
        | {migration["legacy_module"] for migration in policy["migrations"]}
    )
    errors = []
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - written into artifact rows
            errors.append(f"{module_name}: {type(exc).__name__}: {exc}")
    after = output_snapshot(root)
    return {
        "check": "imports_do_not_create_outputs",
        "expected": True,
        "actual": before == after and not errors,
        "pass": before == after and not errors,
        "notes": "; ".join(errors),
    }


def symbol_identity_row(policy: dict) -> dict:
    pairs = batch_symbol_pairs(policy)
    same_object_count = 0
    errors = []
    for pair in pairs:
        try:
            canonical_module = importlib.import_module(pair["canonical_module"])
            legacy_module = importlib.import_module(pair["legacy_module"])
            if getattr(canonical_module, pair["symbol"]) is getattr(legacy_module, pair["symbol"]):
                same_object_count += 1
        except Exception as exc:  # pragma: no cover - written into artifact rows
            errors.append(f"{pair['symbol']}: {type(exc).__name__}: {exc}")
    passed = bool(pairs and same_object_count == len(pairs) and not errors)
    return {
        "check": "legacy_and_canonical_symbols_same_object",
        "expected": len(pairs),
        "actual": same_object_count,
        "pass": passed,
        "notes": "; ".join(errors),
    }


def forbidden_driver_call_row(root: Path, policy: dict) -> dict:
    hits = []
    for migration in policy["migrations"]:
        path = root / migration["canonical_path"]
        if path.is_file():
            hits.extend(forbidden_driver_calls(path))
    return {
        "check": "canonical_modules_have_no_driver_calls",
        "expected": 0,
        "actual": len(hits),
        "pass": len(hits) == 0,
        "notes": "; ".join(hits),
    }


def forbidden_output_dirs_absent_row(root: Path) -> dict:
    forbidden_dirs = [root / "outputs" / f"step{step}_driver_runs" for step in range(63, 68)]
    existing = [path.relative_to(root).as_posix() for path in forbidden_dirs if path.exists()]
    return {
        "check": "step63_67_driver_output_dirs_absent",
        "expected": 0,
        "actual": len(existing),
        "pass": not existing,
        "notes": "; ".join(existing),
    }


def real_geometry_feasibility_classification_row(root: Path) -> dict:
    source = root / "src" / "real_geometry_feasibility.py"
    experiment = root / "experiments" / "steps" / "real_geometry_feasibility" / "feasibility.py"
    forbidden_target = root / "src" / "mpm_lbm" / "sim" / "geometry" / "real_geometry_feasibility.py"
    text = source.read_text(encoding="utf-8-sig") if source.is_file() else ""
    experiment_text = experiment.read_text(encoding="utf-8-sig") if experiment.is_file() else ""
    source_is_shim = "Compatibility shim" in text and "experiments.steps.real_geometry_feasibility.feasibility" in text
    classified_in_source = "FSIDriver3D" in text and ".run(" in text
    classified_in_experiment = "FSIDriver3D" in experiment_text and ".run(" in experiment_text
    classified_as_runner = classified_in_source or (source_is_shim and classified_in_experiment)
    passed = bool(source.is_file() and classified_as_runner and not forbidden_target.exists())
    return {
        "check": "real_geometry_feasibility_classified_not_moved_to_sim",
        "expected": "step_specific_or_experiment_runner",
        "actual": "step_specific_or_experiment_runner" if classified_as_runner else "unclassified",
        "pass": passed,
        "notes": "Batch A classified this existing file; Step68 may move it to experiments/steps while keeping it out of sim.",
    }


def forbidden_driver_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr not in {"run", "step_once", "initialize"}:
                continue
            if is_driver_receiver(node.func.value):
                hits.append(f"{path.as_posix()}:{node.lineno}:{attr}")
    return hits


def is_driver_receiver(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return node.id == "driver"
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            return func.id == "FSIDriver3D"
        if isinstance(func, ast.Attribute):
            return func.attr == "FSIDriver3D"
    return False
