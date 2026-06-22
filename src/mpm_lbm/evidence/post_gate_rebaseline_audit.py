from __future__ import annotations

import json
from pathlib import Path

from .post_gate_rebaseline_runner import step76_rebaseline_row_pass


def build_step76_post_gate_rebaseline_audit(
    root: Path,
    matrix_artifact_path: str = "outputs/step76_post_gate_rebaseline_matrix/post_gate_rebaseline_matrix.json",
    acceptance_policy_path: str = "configs/step76_rebaseline_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    payload = read_json(root / matrix_artifact_path)
    policy = read_json(root / acceptance_policy_path)
    rows = [audit_row(row, policy) for row in payload["rows"]]
    required_names = set(policy["required_row_names"])
    row_names = {row["row_name"] for row in rows}
    summary = {
        "activation_feature_count": sum(int(row["activation_feature_count"]) for row in rows),
        "canonical_module_count": sum(
            1 for row in rows if row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        ),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "missing_required_rows": sorted(required_names - row_names),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "post_gate_rebaseline_audit_pass": False,
        "required_row_count": len(required_names),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
    }
    summary["post_gate_rebaseline_audit_pass"] = bool(
        summary["row_count"] == summary["required_row_count"]
        and summary["row_count"] == summary["pass_count"]
        and summary["missing_required_rows"] == []
        and summary["driver_run_called_count"] == summary["row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["canonical_module_count"] == summary["row_count"]
        and summary["legacy_driver_module_used_count"] == 0
        and summary["activation_feature_count"] == 0
    )
    return rows, summary


def audit_row(row: dict, policy: dict) -> dict:
    passed = bool(row["stable"] and step76_rebaseline_row_pass(row, policy))
    return {
        "activation_feature_count": int(row["activation_feature_count"]),
        "canonical_driver_module": row["canonical_driver_module"],
        "completed_lbm_steps": int(row["completed_lbm_steps"]),
        "diagnostics_row_count": int(row["diagnostics_row_count"]),
        "driver_run_called": bool(row["driver_run_called"]),
        "has_inf": bool(row["has_inf"]),
        "has_nan": bool(row["has_nan"]),
        "legacy_driver_module_used_as_implementation": bool(row["legacy_driver_module_used_as_implementation"]),
        "n_grid": int(row["n_grid"]),
        "n_particles": int(row["n_particles"]),
        "pass": passed,
        "post_gate_simulation_allowed": bool(row["post_gate_simulation_allowed"]),
        "row_name": row["row_name"],
        "stable": bool(row["stable"]),
        "total_mpm_substeps": int(row["total_mpm_substeps"]),
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
