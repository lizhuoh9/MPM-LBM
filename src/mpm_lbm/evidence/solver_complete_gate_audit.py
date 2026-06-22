from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step75_solver_complete_gate_audit(
    root: Path,
    policy_path: str = "configs/step75_solver_complete_gate_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    precondition = read_json(root / policy["precondition_artifact_path"])["summary"]
    activation = read_json(root / policy["activation_gate_artifact_path"])["summary"]
    campaign = read_json(root / policy["campaign_policy_artifact_path"])["summary"]
    rows = [
        bool_row("precondition_artifact_audit_pass", precondition["precondition_artifact_audit_pass"], True),
        bool_row("activation_gate_closure_audit_pass", activation["activation_gate_closure_audit_pass"], True),
        bool_row("post_gate_campaign_policy_audit_pass", campaign["post_gate_campaign_policy_audit_pass"], True),
        bool_row("activation_allowed_count", activation["activation_allowed_count"], 0),
        bool_row("activation_feature_count_in_first_campaign", campaign["activation_feature_count_in_first_campaign"], 0),
        bool_row("runtime_geometry_enabled_in_next_step", campaign["runtime_geometry_enabled"], False),
        bool_row("wall_velocity_enabled_in_next_step", campaign["wall_velocity_enabled"], False),
        bool_row("real_geometry_enabled_in_next_step", campaign["real_geometry_enabled"], False),
        bool_row("squid_proxy_enabled_in_next_step", campaign["squid_proxy_enabled"], False),
        bool_row("vtr_output_allowed_in_next_step", campaign["write_vtk"], False),
        bool_row("particle_npy_output_allowed_in_next_step", campaign["write_particles"], False),
    ]
    summary = {
        "activation_features_allowed_in_next_step": [],
        "allowed_next_step": policy["allowed_next_step"],
        "allowed_next_step_scope": policy["allowed_next_step_scope"],
        "gate_status": policy["expected_gate_status"],
        "particle_npy_output_allowed": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "physical_validation_claim": False,
        "post_gate_simulation_allowed": True,
        "production_readiness_claim": False,
        "real_geometry_activation_allowed": False,
        "row_count": len(rows),
        "runtime_geometry_activation_allowed": False,
        "solver_complete_gate_audit_pass": False,
        "squid_proxy_activation_allowed": False,
        "vtr_output_allowed": False,
        "wall_velocity_activation_allowed": False,
    }
    summary["solver_complete_gate_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["gate_status"] == "ready_for_step76_rebaseline_only"
        and summary["post_gate_simulation_allowed"] is True
        and summary["allowed_next_step"] == "Step76"
        and summary["allowed_next_step_scope"] == "minimal safe rebaseline only"
        and summary["activation_features_allowed_in_next_step"] == []
        and summary["runtime_geometry_activation_allowed"] is False
        and summary["wall_velocity_activation_allowed"] is False
        and summary["real_geometry_activation_allowed"] is False
        and summary["squid_proxy_activation_allowed"] is False
        and summary["vtr_output_allowed"] is False
        and summary["particle_npy_output_allowed"] is False
        and summary["production_readiness_claim"] is False
        and summary["physical_validation_claim"] is False
    )
    return rows, summary


def bool_row(check: str, actual, expected) -> dict:
    return {"actual": actual, "check": check, "expected": expected, "pass": actual == expected}
