from __future__ import annotations

import json
from pathlib import Path

from .canonical_driver_32_duration_runner import duration_32_row_pass


def build_canonical_driver_32_duration_audit(
    root: Path,
    matrix_artifact_path: str = "outputs/step62_32_duration_matrix/duration_32_matrix.json",
    acceptance_policy_path: str = "configs/step62_duration_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    payload = read_json(root / matrix_artifact_path)
    policy = read_json(root / acceptance_policy_path)
    rows = [audit_row(row, policy) for row in payload["rows"]]
    required_names = set(policy["required_row_names"])
    row_names = {row["row_name"] for row in rows}
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_row_count": len(required_names),
        "missing_required_rows": sorted(required_names - row_names),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "runtime_warning_count": sum(1 for row in rows if row["runtime_warning"]),
        "runtime_hard_limit_exceeded_count": sum(1 for row in rows if row["runtime_hard_limit_exceeded"]),
        "soft_rho_min_warning_count": sum(1 for row in rows if row["soft_rho_min_warning"]),
        "soft_rho_max_warning_count": sum(1 for row in rows if row["soft_rho_max_warning"]),
        "canonical_module_count": sum(
            1 for row in rows if row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        ),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "duration_32_audit_pass": False,
    }
    summary["duration_32_audit_pass"] = bool(
        summary["row_count"] == summary["required_row_count"]
        and summary["row_count"] == summary["pass_count"]
        and summary["missing_required_rows"] == []
        and summary["driver_run_called_count"] == summary["row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["canonical_module_count"] == summary["row_count"]
        and summary["legacy_driver_module_used_count"] == 0
    )
    return rows, summary


def audit_row(row: dict, policy: dict) -> dict:
    passed = bool(row["stable"] and duration_32_row_pass(row, policy))
    return {
        "row_name": row["row_name"],
        "coupling_mode": row["coupling_mode"],
        "reaction_transfer_mode": row["reaction_transfer_mode"],
        "driver_run_called": bool(row["driver_run_called"]),
        "stable": bool(row["stable"]),
        "runtime_warning": bool(row["runtime_warning"]),
        "canonical_driver_module": row["canonical_driver_module"],
        "legacy_driver_module_used_as_implementation": bool(row["legacy_driver_module_used_as_implementation"]),
        "n_grid": int(row["n_grid"]),
        "n_particles": int(row["n_particles"]),
        "completed_lbm_steps": int(row["completed_lbm_steps"]),
        "total_mpm_substeps": int(row["total_mpm_substeps"]),
        "diagnostics_row_count": int(row["diagnostics_row_count"]),
        "rho_min_min": float(row["rho_min_min"]),
        "rho_max_max": float(row["rho_max_max"]),
        "lbm_max_v_max": float(row["lbm_max_v_max"]),
        "mpm_min_J_min": float(row["mpm_min_J_min"]),
        "bb_link_count_max": int(row["bb_link_count_max"]),
        "elapsed_seconds": float(row["elapsed_seconds"]),
        "runtime_hard_limit_exceeded": bool(row["runtime_hard_limit_exceeded"]),
        "soft_rho_min_warning": bool(row["soft_rho_min_warning"]),
        "soft_rho_max_warning": bool(row["soft_rho_max_warning"]),
        "has_nan": bool(row["has_nan"]),
        "has_inf": bool(row["has_inf"]),
        "pass": passed,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
