from __future__ import annotations

import json
from pathlib import Path

from .canonical_driver_smoke_runner import smoke_row_pass


def build_canonical_driver_smoke_audit(
    root: Path,
    matrix_artifact_path: str = "outputs/step59_canonical_driver_smoke_matrix/smoke_matrix.json",
    acceptance_policy_path: str = "configs/step59_smoke_acceptance_policy.json",
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
        "canonical_module_count": sum(
            1 for row in rows if row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        ),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "canonical_driver_smoke_audit_pass": False,
    }
    summary["canonical_driver_smoke_audit_pass"] = bool(
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
    passed = bool(row["stable"] and smoke_row_pass(row, policy))
    return {
        "row_name": row["row_name"],
        "coupling_mode": row["coupling_mode"],
        "reaction_transfer_mode": row["reaction_transfer_mode"],
        "driver_run_called": bool(row["driver_run_called"]),
        "stable": bool(row["stable"]),
        "canonical_driver_module": row["canonical_driver_module"],
        "legacy_driver_module_used_as_implementation": bool(row["legacy_driver_module_used_as_implementation"]),
        "completed_lbm_steps": int(row["completed_lbm_steps"]),
        "total_mpm_substeps": int(row["total_mpm_substeps"]),
        "diagnostics_row_count": int(row["diagnostics_row_count"]),
        "rho_min": float(row["rho_min"]),
        "rho_max": float(row["rho_max"]),
        "lbm_max_v": float(row["lbm_max_v"]),
        "mpm_min_J": float(row["mpm_min_J"]),
        "has_nan": bool(row["has_nan"]),
        "has_inf": bool(row["has_inf"]),
        "pass": passed,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
