from __future__ import annotations

import math
from pathlib import Path

from experiments.steps.step53_support_scaling_audit.config import (
    SupportScalingAuditConfig,
    load_metric_semantics_policy,
    load_reference_artifacts_config,
)
from experiments.steps.step53_support_scaling_audit.diagnostics import (
    all_ratio_fields_finite,
    finite_values,
    max_step_value,
    ratio,
    row_by_name,
    step_by_phase,
)


def load_bundle(root: Path, config_path: str):
    config = SupportScalingAuditConfig.from_json(root / config_path)
    references = load_reference_artifacts_config(root, config)
    policy = load_metric_semantics_policy(root, config)
    payloads = {
        name: _read_json(root / path)
        for name, path in references.items()
        if name.endswith("_path") and str(path).lower().endswith(".json")
    }
    return config, references, policy, payloads


def reference_validation_rows(root: Path, config_path: str) -> tuple[list[dict], dict]:
    config, references, policy, payloads = load_bundle(root, config_path)
    rows = []
    rows.append(_check_row("audit_id_expected", config.audit_id == "step53_controlled_48_support_scaling_active_cell_semantics", config.audit_id, "Step 53 audit id must be stable"))
    rows.append(_check_row("diagnostic_only", config.diagnostic_only is True, config.diagnostic_only, "Step 53 must be diagnostic-only"))
    rows.append(_check_row("post_processing_only", config.post_processing_only is True, config.post_processing_only, "Step 53 must be post-processing only"))
    rows.append(_check_row("no_new_solver_rows", config.requires_new_solver_rows is False, config.requires_new_solver_rows, "Step 53 must not require new solver rows"))
    rows.append(_check_row("no_new_transfer_mode", config.introduces_new_transfer_mode is False, config.introduces_new_transfer_mode, "Step 53 must not introduce a new transfer mode"))
    rows.append(_check_row("mutation_flags_false", config.mutation_flags_false(), config.mutation_flags_false(), "all mutation and heavy-output flags must be false"))
    rows.append(_check_row("phase_count_expected", config.phase_count == 40, config.phase_count, "Step 53 must audit forty phases"))
    rows.append(_check_row("phase_sequence_starts_at_0", float(config.phase_sequence[0]) == 0.0, config.phase_sequence[0], "phase sequence must start at 0.0"))
    rows.append(_check_row("phase_sequence_ends_at_0975", float(config.phase_sequence[-1]) == 0.975, config.phase_sequence[-1], "phase sequence must end at 0.975"))

    for key, value in references.items():
        if key.endswith("_path"):
            path = root / value
            rows.append(_check_row(f"{key}_exists", path.is_file(), value, "referenced artifact must exist"))
            rows.append(_check_row(f"{key}_readable", key in payloads or path.suffix.lower() == ".md", value, "referenced artifact must be readable"))

    step51 = payloads["step51_transfer_matrix_path"]
    step52 = payloads["step52_feasibility_matrix_path"]
    scaling = payloads["step52_scaling_comparison_path"]
    rows.extend(
        [
            _check_row("step51_combined_row_exists", _has_row(step51["rows"], config.step51_combined_row_name), config.step51_combined_row_name, "Step 51 engineering combined row must exist"),
            _check_row("step52_combined_row_exists", _has_row(step52["rows"], config.step52_combined_row_name), config.step52_combined_row_name, "Step 52 engineering combined row must exist"),
            _check_row("step52_static_row_exists", _has_row(step52["rows"], config.step52_static_row_name), config.step52_static_row_name, "Step 52 static row must exist"),
            _check_row("step52_scaling_pass", scaling["summary"]["scaling_pass"] is True, scaling["summary"]["scaling_pass"], "accepted Step 52 scaling comparison must be green"),
            _check_row("active_cell_growth_must_be_reported", policy["active_cell_count_growth_must_be_reported"] is True, policy["active_cell_count_growth_must_be_reported"], "active-cell growth observation must be reported"),
            _check_row("applied_cell_growth_required", policy["applied_cell_count_growth_required"] is True, policy["applied_cell_count_growth_required"], "applied wall-cell support growth is required"),
            _check_row("claim_policy_false", _claim_policy_false(policy), True, "no physical or production claims are allowed"),
        ]
    )

    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "audit_id": config.audit_id,
        "diagnostic_only": config.diagnostic_only,
        "post_processing_only": config.post_processing_only,
        "no_new_solver_rows": not config.requires_new_solver_rows,
        "no_new_transfer_mode": not config.introduces_new_transfer_mode,
        "phase_count": config.phase_count,
        "reference_validation_pass": False,
    }
    summary["reference_validation_pass"] = bool(summary["row_count"] == summary["pass_count"])
    return rows, summary


def phasewise_support_scaling_rows(root: Path, config_path: str) -> tuple[list[dict], dict]:
    config, _, _, payloads = load_bundle(root, config_path)
    step51_row = row_by_name(payloads["step51_transfer_matrix_path"]["rows"], config.step51_combined_row_name)
    step52_row = row_by_name(payloads["step52_feasibility_matrix_path"]["rows"], config.step52_combined_row_name)
    step51_by_phase = step_by_phase(step51_row)
    step52_by_phase = step_by_phase(step52_row)
    rows = []
    for phase in config.phase_sequence:
        left = step51_by_phase[float(phase)]
        right = step52_by_phase[float(phase)]
        row = {
            "phase": float(phase),
            "active_cell_count_32": int(left["active_cell_count"]),
            "active_cell_count_48": int(right["active_cell_count"]),
            "applied_cell_count_32": int(left["applied_cell_count"]),
            "applied_cell_count_48": int(right["applied_cell_count"]),
            "bb_link_count_32": int(left["bb_link_count"]),
            "bb_link_count_48": int(right["bb_link_count"]),
            "projected_mass_32": float(left["projected_mass"]),
            "projected_mass_48": float(right["projected_mass"]),
            "projected_mass_delta_48_minus_32": float(right["projected_mass"]) - float(left["projected_mass"]),
            "rho_min_32": float(left["rho_min"]),
            "rho_min_48": float(right["rho_min"]),
            "rho_max_32": float(left["rho_max"]),
            "rho_max_48": float(right["rho_max"]),
            "lbm_max_v_32": float(left["lbm_max_v"]),
            "lbm_max_v_48": float(right["lbm_max_v"]),
            "hydro_force_norm_32": float(left["hydro_force_max_norm"]),
            "hydro_force_norm_48": float(right["hydro_force_max_norm"]),
            "impulse_proxy_32": float(left["impulse_proxy_norm"]),
            "impulse_proxy_48": float(right["impulse_proxy_norm"]),
        }
        row["active_cell_count_ratio_48_vs_32"] = ratio(row["active_cell_count_48"], row["active_cell_count_32"])
        row["active_cell_count_delta_48_minus_32"] = row["active_cell_count_48"] - row["active_cell_count_32"]
        row["applied_cell_count_ratio_48_vs_32"] = ratio(row["applied_cell_count_48"], row["applied_cell_count_32"])
        row["applied_cell_count_delta_48_minus_32"] = row["applied_cell_count_48"] - row["applied_cell_count_32"]
        row["bb_link_count_ratio_48_vs_32"] = ratio(row["bb_link_count_48"], row["bb_link_count_32"])
        row["bb_link_count_delta_48_minus_32"] = row["bb_link_count_48"] - row["bb_link_count_32"]
        row["hydro_force_ratio_48_vs_32"] = ratio(row["hydro_force_norm_48"], row["hydro_force_norm_32"])
        row["impulse_proxy_ratio_48_vs_32"] = ratio(row["impulse_proxy_48"], row["impulse_proxy_32"])
        row["all_values_finite"] = finite_values(row)
        row["all_ratios_finite"] = all_ratio_fields_finite(row)
        rows.append(row)
    summary = summarize_phasewise_rows(config, rows)
    return rows, summary


def summarize_phasewise_rows(config: SupportScalingAuditConfig, rows: list[dict]) -> dict:
    active_32 = max(int(row["active_cell_count_32"]) for row in rows)
    active_48 = max(int(row["active_cell_count_48"]) for row in rows)
    applied_32 = max(int(row["applied_cell_count_32"]) for row in rows)
    applied_48 = max(int(row["applied_cell_count_48"]) for row in rows)
    bb_32 = max(int(row["bb_link_count_32"]) for row in rows)
    bb_48 = max(int(row["bb_link_count_48"]) for row in rows)
    summary = {
        "phase_count": config.phase_count,
        "matched_phase_count": len(rows),
        "phase_sequence_starts_at_0": bool(rows and float(rows[0]["phase"]) == 0.0),
        "phase_sequence_ends_at_0975": bool(rows and float(rows[-1]["phase"]) == 0.975),
        "all_values_finite": all(bool(row["all_values_finite"]) for row in rows),
        "all_ratios_finite": all(bool(row["all_ratios_finite"]) for row in rows),
        "active_cell_count_32": active_32,
        "active_cell_count_48": active_48,
        "active_cell_count_ratio_48_vs_32": ratio(active_48, active_32),
        "active_cell_count_growth_observed": active_48 > active_32,
        "active_cell_count_non_decreasing": active_48 >= active_32,
        "applied_cell_count_32": applied_32,
        "applied_cell_count_48": applied_48,
        "applied_cell_count_ratio_48_vs_32": ratio(applied_48, applied_32),
        "applied_cell_count_growth_observed": applied_48 > applied_32,
        "bb_link_count_32": bb_32,
        "bb_link_count_48": bb_48,
        "bb_link_count_ratio_48_vs_32": ratio(bb_48, bb_32),
        "rho_min_48": min(float(row["rho_min_48"]) for row in rows),
        "rho_max_48": max(float(row["rho_max_48"]) for row in rows),
        "lbm_max_v_48": max(float(row["lbm_max_v_48"]) for row in rows),
        "hydro_force_max_norm_32": max(float(row["hydro_force_norm_32"]) for row in rows),
        "hydro_force_max_norm_48": max(float(row["hydro_force_norm_48"]) for row in rows),
        "impulse_proxy_32": max(float(row["impulse_proxy_32"]) for row in rows),
        "impulse_proxy_48": max(float(row["impulse_proxy_48"]) for row in rows),
        "force_impulse_ratios_finite": True,
        "force_impulse_interpretation": "diagnostic_proxy_only",
        "grid_convergence_claim": False,
        "physical_validation_claim": False,
        "production_readiness_claim": False,
    }
    summary["hydro_force_ratio_48_vs_32"] = ratio(summary["hydro_force_max_norm_48"], summary["hydro_force_max_norm_32"])
    summary["impulse_proxy_ratio_48_vs_32"] = ratio(summary["impulse_proxy_48"], summary["impulse_proxy_32"])
    summary["force_impulse_ratios_finite"] = bool(
        math.isfinite(float(summary["hydro_force_ratio_48_vs_32"]))
        and math.isfinite(float(summary["impulse_proxy_ratio_48_vs_32"]))
    )
    summary["phasewise_audit_pass"] = bool(
        int(summary["matched_phase_count"]) == 40
        and summary["phase_sequence_starts_at_0"]
        and summary["phase_sequence_ends_at_0975"]
        and summary["all_values_finite"]
        and summary["all_ratios_finite"]
        and summary["active_cell_count_non_decreasing"]
        and summary["applied_cell_count_growth_observed"]
        and int(summary["bb_link_count_48"]) > 0
        and float(summary["rho_min_48"]) > 0.95
        and float(summary["rho_max_48"]) < 1.05
        and float(summary["lbm_max_v_48"]) < 0.1
        and summary["force_impulse_ratios_finite"]
    )
    return summary


def active_cell_semantics_rows(root: Path, config_path: str) -> tuple[list[dict], dict]:
    _, _, policy, payloads = load_bundle(root, config_path)
    scaling_row = payloads["step52_scaling_comparison_path"]["rows"][0]
    active_32 = int(scaling_row["active_cell_count_32"])
    active_48 = int(scaling_row["active_cell_count_48"])
    status = "non_decreasing_but_not_resolution_scaling"
    row = {
        "metric": "active_cell_count",
        "active_cell_count_32": active_32,
        "active_cell_count_48": active_48,
        "active_cell_count_ratio": ratio(active_48, active_32),
        "active_cell_count_growth_observed": bool(active_48 > active_32),
        "active_cell_count_non_decreasing": bool(active_48 >= active_32),
        "active_cell_count_used_as_grid_convergence_metric": False,
        "active_cell_count_growth_required_for_pass": False,
        "active_cell_growth_failure_is_step53_failure": False,
        "active_cell_semantics_status": status,
        "step54_link_area_allowed": True,
        "step54_block_reason": "",
        "grid_convergence_claim": False,
        "physical_validation_claim": False,
        "production_readiness_claim": False,
        "notes": "diagnostic projected support is non-decreasing but not a resolution-scaling metric",
    }
    row["semantics_pass"] = bool(
        row["active_cell_count_non_decreasing"]
        and row["active_cell_count_used_as_grid_convergence_metric"] is False
        and row["active_cell_count_growth_required_for_pass"] is False
        and status in policy["allowed_active_cell_semantics_status"]
        and row["grid_convergence_claim"] is False
        and row["physical_validation_claim"] is False
        and row["production_readiness_claim"] is False
    )
    summary = {
        "row_count": 1,
        "active_cell_count_32": active_32,
        "active_cell_count_48": active_48,
        "active_cell_count_ratio": row["active_cell_count_ratio"],
        "active_cell_count_growth_observed": row["active_cell_count_growth_observed"],
        "active_cell_count_non_decreasing": row["active_cell_count_non_decreasing"],
        "active_cell_count_used_as_grid_convergence_metric": False,
        "active_cell_count_growth_required_for_pass": False,
        "active_cell_semantics_status": status,
        "step54_link_area_allowed": True,
        "grid_convergence_claim": False,
        "physical_validation_claim": False,
        "production_readiness_claim": False,
        "semantics_pass": row["semantics_pass"],
    }
    return [row], summary


def applied_wall_support_rows(root: Path, config_path: str) -> tuple[list[dict], dict]:
    config, _, policy, payloads = load_bundle(root, config_path)
    scaling_row = payloads["step52_scaling_comparison_path"]["rows"][0]
    active_32 = int(scaling_row["active_cell_count_32"])
    active_48 = int(scaling_row["active_cell_count_48"])
    applied_32 = int(scaling_row["applied_cell_count_32"])
    applied_48 = int(scaling_row["applied_cell_count_48"])
    row = {
        "metric": "applied_cell_count",
        "applied_cell_count_32": applied_32,
        "applied_cell_count_48": applied_48,
        "applied_cell_count_ratio_48_vs_32": ratio(applied_48, applied_32),
        "applied_cell_count_growth_observed": applied_48 > applied_32,
        "applied_cell_support_growth_pass": applied_48 > applied_32,
        "applied_cell_fraction_32": applied_32 / float(config.step51_grid ** 3),
        "applied_cell_fraction_48": applied_48 / float(config.step52_grid ** 3),
        "applied_cell_count_per_active_cell_32": ratio(applied_32, active_32),
        "applied_cell_count_per_active_cell_48": ratio(applied_48, active_48),
        "applied_cell_growth_is_physical_validation": False,
        "wall_support_growth_claim": policy["wall_support_growth_claim"],
    }
    row["applied_cell_fraction_ratio"] = ratio(row["applied_cell_fraction_48"], row["applied_cell_fraction_32"])
    row["audit_pass"] = bool(
        applied_32 == 648
        and applied_48 == 2136
        and row["applied_cell_count_growth_observed"]
        and math.isfinite(float(row["applied_cell_count_ratio_48_vs_32"]))
        and float(row["applied_cell_count_ratio_48_vs_32"]) > 1.0
        and row["applied_cell_growth_is_physical_validation"] is False
        and row["wall_support_growth_claim"] == "diagnostic_only"
    )
    summary = dict(row)
    summary["row_count"] = 1
    summary["applied_wall_support_audit_pass"] = bool(row["audit_pass"])
    return [row], summary


def bounceback_support_rows(root: Path, config_path: str) -> tuple[list[dict], dict]:
    _, _, policy, payloads = load_bundle(root, config_path)
    scaling_row = payloads["step52_scaling_comparison_path"]["rows"][0]
    bb_32 = int(scaling_row["bb_link_count_32"])
    bb_48 = int(scaling_row["bb_link_count_48"])
    status = "non_decreasing_but_not_area_convergence"
    row = {
        "metric": "bb_link_count",
        "bb_link_count_32": bb_32,
        "bb_link_count_48": bb_48,
        "bb_link_count_ratio": ratio(bb_48, bb_32),
        "bb_link_growth_observed": bb_48 > bb_32,
        "bb_link_non_decreasing": bb_48 >= bb_32,
        "bb_link_used_as_area_convergence_metric": False,
        "bb_link_support_status": status,
    }
    row["audit_pass"] = bool(
        bb_48 > 0
        and row["bb_link_non_decreasing"]
        and row["bb_link_used_as_area_convergence_metric"] is False
        and status in policy["allowed_bb_link_support_status"]
    )
    summary = dict(row)
    summary["row_count"] = 1
    summary["bounceback_support_audit_pass"] = bool(row["audit_pass"])
    return [row], summary


def step52_regression_rows(root: Path, config_path: str) -> tuple[list[dict], dict]:
    _, references, _, payloads = load_bundle(root, config_path)
    report_path = root / references["step52_report_path"]
    matrix_summary = payloads["step52_feasibility_matrix_path"]["summary"]
    scaling_summary = payloads["step52_scaling_comparison_path"]["summary"]
    state_summary = payloads["step52_state_guard_path"]["summary"]
    artifact_summary = payloads["step52_artifact_summary_path"]
    step51_regression = payloads["step52_step51_regression_guard_path"]["summary"]
    rows = [
        _check_row("step52_report_exists", report_path.is_file(), references["step52_report_path"], "Step 52 report must remain present"),
        _check_row("step52_matrix_row_count", int(matrix_summary["row_count"]) == 2, matrix_summary["row_count"], "Step 52 matrix must still have two rows"),
        _check_row("step52_matrix_stable_count", int(matrix_summary["stable_count"]) == 2, matrix_summary["stable_count"], "Step 52 matrix must still be stable"),
        _check_row("step52_scaling_pass", scaling_summary["scaling_pass"] is True, scaling_summary["scaling_pass"], "Step 52 scaling comparison must remain green"),
        _check_row("step52_active_cell_growth_reported", "active_cell_count_growth_observed" in scaling_summary, scaling_summary.get("active_cell_count_growth_observed"), "Step 52 active-cell growth observation must remain explicit"),
        _check_row("step52_applied_cell_growth_observed", scaling_summary["applied_cell_count_growth_observed"] is True, scaling_summary["applied_cell_count_growth_observed"], "Step 52 applied wall-cell support growth must remain true"),
        _check_row("step52_state_guard_pass", state_summary["guard_pass"] is True, state_summary["guard_pass"], "Step 52 state mutation guard must remain green"),
        _check_row("step52_artifact_budget_pass", artifact_summary["artifact_budget_pass"] is True, artifact_summary["artifact_budget_pass"], "Step 52 artifact budget must remain green"),
        _check_row("step51_regression_evidence_green", step51_regression["regression_pass"] is True, step51_regression["regression_pass"], "Step 51 evidence through Step 52 must remain green"),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
    }
    summary["regression_pass"] = bool(summary["row_count"] == summary["pass_count"])
    return rows, summary


def _read_json(path: Path) -> dict:
    import json

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _check_row(check: str, passed: bool, value, notes: str) -> dict:
    return {"check": check, "pass": bool(passed), "value": value, "notes": notes}


def _has_row(rows: list[dict], row_name: str) -> bool:
    return any(row["row_name"] == row_name for row in rows)


def _claim_policy_false(policy: dict) -> bool:
    return (
        policy["active_cell_count_is_grid_convergence_metric"] is False
        and policy["grid_convergence_claim_allowed"] is False
        and policy["physical_validation_claim_allowed"] is False
        and policy["production_readiness_claim_allowed"] is False
        and policy["applied_cell_growth_is_physical_validation"] is False
        and policy["bb_link_used_as_area_convergence_metric"] is False
        and policy["force_impulse_interpretation"] == "diagnostic_proxy_only"
    )
