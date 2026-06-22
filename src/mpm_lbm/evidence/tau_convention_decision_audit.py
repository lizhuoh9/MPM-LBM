from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text
from src.mpm_lbm.sim.lbm import relaxation_semantics


def build_step71_tau_convention_decision_audit(
    root: Path,
    policy_path: str = "configs/step71_tau_convention_decision_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    summary_payload = relaxation_semantics.relaxation_semantics_summary(policy["legacy_probe_input"])
    fluid_source = read_text(root / "src/mpm_lbm/sim/lbm/fluid.py")
    legacy_tau = relaxation_semantics.tau_from_legacy_external_solver_parameter(policy["legacy_probe_input"])
    standard_tau = relaxation_semantics.tau_from_lattice_kinematic_viscosity(policy["standard_probe_input"])
    default_convention = getattr(relaxation_semantics, "DEFAULT_TAU_CONVENTION", None)
    legacy_constant = getattr(relaxation_semantics, "LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER", None)
    standard_constant = getattr(relaxation_semantics, "STANDARD_LATTICE_KINEMATIC_VISCOSITY", None)
    rows = [
        value_row("tau_convention_decision", policy["tau_convention_decision"], "preserve_legacy_external_solver_parameter_for_now"),
        value_row("default_solver_tau_formula", policy["default_solver_tau_formula"], "tau_from_legacy_external_solver_parameter"),
        float_row("legacy_tau_probe", legacy_tau, policy["legacy_probe_expected_tau"]),
        float_row("standard_tau_probe", standard_tau, policy["standard_probe_expected_tau"]),
        value_row("summary_default_solver_formula", summary_payload["default_solver_formula"], "legacy_external_solver_parameter"),
        bool_row("summary_standard_lattice_viscosity_is_default", summary_payload["standard_lattice_viscosity_is_default"], False),
        bool_row("summary_physical_viscosity_validation_claim", summary_payload["physical_viscosity_validation_claim"], False),
        bool_row("policy_future_standard_tau_migration_requires_baseline_rerun", policy["future_standard_tau_migration_requires_baseline_rerun"], True),
        bool_row("policy_solver_numerical_behavior_changed", policy["solver_numerical_behavior_changed"], False),
        value_row("default_tau_convention_constant", default_convention, "legacy_external_solver_relaxation_parameter"),
        value_row("legacy_tau_convention_constant", legacy_constant, "legacy_external_solver_relaxation_parameter"),
        value_row("standard_tau_convention_constant", standard_constant, "standard_lattice_kinematic_viscosity"),
        bool_row("fluid_source_uses_legacy_helper", "tau_from_legacy_external_solver_parameter" in fluid_source, True),
        bool_row("fluid_source_avoids_hardcoded_legacy_formula", "self.niu / 3.0 + 0.5" in fluid_source, False),
        bool_row("fluid_source_avoids_standard_tau_default", "tau_from_lattice_kinematic_viscosity" in fluid_source, False),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "tau_convention_decision": policy["tau_convention_decision"],
        "default_solver_tau_formula": policy["default_solver_tau_formula"],
        "legacy_tau_for_0_1": legacy_tau,
        "standard_tau_for_0_1": standard_tau,
        "standard_lattice_viscosity_is_default": bool(summary_payload["standard_lattice_viscosity_is_default"]),
        "physical_viscosity_validation_claim": bool(summary_payload["physical_viscosity_validation_claim"]),
        "future_standard_tau_migration_requires_baseline_rerun": bool(policy["future_standard_tau_migration_requires_baseline_rerun"]),
        "solver_numerical_behavior_changed": bool(policy["solver_numerical_behavior_changed"]),
        "tau_convention_decision_audit_pass": False,
    }
    summary["tau_convention_decision_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["legacy_tau_for_0_1"] == policy["legacy_probe_expected_tau"]
        and summary["standard_tau_for_0_1"] == policy["standard_probe_expected_tau"]
        and summary["standard_lattice_viscosity_is_default"] is False
        and summary["physical_viscosity_validation_claim"] is False
        and summary["future_standard_tau_migration_requires_baseline_rerun"] is True
        and summary["solver_numerical_behavior_changed"] is False
    )
    return rows, summary


def bool_row(check: str, actual, expected) -> dict:
    return {
        "check": check,
        "actual": bool(actual),
        "expected": bool(expected),
        "pass": bool(actual) is bool(expected),
    }


def value_row(check: str, actual, expected) -> dict:
    return {
        "check": check,
        "actual": "" if actual is None else str(actual),
        "expected": str(expected),
        "pass": actual == expected,
    }


def float_row(check: str, actual: float, expected: float) -> dict:
    return {
        "check": check,
        "actual": actual,
        "expected": expected,
        "pass": abs(float(actual) - float(expected)) <= 1.0e-15,
    }
