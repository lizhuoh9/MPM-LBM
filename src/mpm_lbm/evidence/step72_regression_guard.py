from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig


def build_step72_step71_regression_guard(
    root: Path,
    policy_path: str = "configs/step72_step71_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    artifact_check_names = {check["check"] for check in policy["step71_artifact_checks"]}
    rows = [artifact_row(root, check) for check in policy["step71_artifact_checks"]]
    default_config = FSIDriverConfig()
    rows.extend(
        [
            {
                "check": "current_fsidriver_write_vtk_default",
                "summary_key": "FSIDriverConfig.write_vtk",
                "actual": default_config.write_vtk,
                "expected": policy["required_current_defaults"]["FSIDriverConfig.write_vtk"],
                "pass": default_config.write_vtk is policy["required_current_defaults"]["FSIDriverConfig.write_vtk"],
            },
            {
                "check": "current_fsidriver_write_particles_default",
                "summary_key": "FSIDriverConfig.write_particles",
                "actual": default_config.write_particles,
                "expected": policy["required_current_defaults"]["FSIDriverConfig.write_particles"],
                "pass": default_config.write_particles is policy["required_current_defaults"]["FSIDriverConfig.write_particles"],
            },
        ]
    )
    tau_payload = read_json(root / "outputs/step71_tau_convention_decision_audit/tau_convention_decision.json")
    rows.append(
        {
            "check": "step71_tau_decision_preserved",
            "summary_key": "tau_convention_decision",
            "actual": tau_payload["summary"]["tau_convention_decision"],
            "expected": policy["required_tau_decision"],
            "pass": tau_payload["summary"]["tau_convention_decision"] == policy["required_tau_decision"],
        }
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step71_artifact_check_count": len(policy["step71_artifact_checks"]),
        "step71_artifact_pass_count": sum(1 for row in rows if row["check"] in artifact_check_names and row["pass"]),
        "current_fsidriver_default_write_vtk": bool(default_config.write_vtk),
        "current_fsidriver_default_write_particles": bool(default_config.write_particles),
        "step72_step71_regression_guard_pass": False,
    }
    summary["step72_step71_regression_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["current_fsidriver_default_write_vtk"] is False
        and summary["current_fsidriver_default_write_particles"] is False
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    payload = read_json(root / check["artifact_path"])
    actual = payload.get("summary", payload).get(check["summary_key"])
    return {
        "check": check["check"],
        "summary_key": check["summary_key"],
        "actual": actual,
        "expected": check["expected"],
        "pass": actual == check["expected"],
    }
