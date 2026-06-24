from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step103_common import (
    ALLOWED_CLAIM,
    read_json,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step103_fluent_reference_loader import load_step103_fluent_reference_status


def build_step103_fluent_solver_gap_comparison(
    root: Path,
    policy_path: str = "configs/step103_fluent_solver_comparison_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    smoke = read_json(root / policy["smoke_matrix_artifact_path"])
    smoke_summary = smoke["summary"]
    smoke_row = smoke["rows"][0]
    reference = load_step103_fluent_reference_status(root, policy["fluent_reference_csv_schema_path"])
    gaps = list(policy["required_capability_gaps"])
    rows = [gap_row(name) for name in gaps]
    summary = {
        **reference,
        "allowed_claim": ALLOWED_CLAIM,
        "capability_gap_count": len(gaps),
        "comparison_status": policy["comparison_status_when_no_equivalent_monitor"],
        "direct_quantitative_equivalence_allowed": bool(policy["direct_quantitative_equivalence_allowed"]),
        "gap_conformal_mesh_equivalence": "conformal_mesh_equivalence" in gaps,
        "gap_dimensional_velocity_mapping": "dimensional_velocity_mapping" in gaps,
        "gap_dimensionality_equivalence": "dimensionality_equivalence" in gaps,
        "gap_dynamic_mesh_equivalence": "dynamic_mesh_equivalence" in gaps,
        "gap_exact_flap_tip_displacement": "exact_flap_tip_displacement" in gaps,
        "gap_linear_elasticity_equivalence": "linear_elasticity_equivalence" in gaps,
        "official_case_dimensionality": policy["official_case_dimensionality"],
        "official_dynamic_mesh": bool(policy["official_dynamic_mesh"]),
        "official_fluent_files_used_as_runtime_input": bool(smoke_row["official_fluent_files_used_as_runtime_input"]),
        "official_monitor_quantity": policy["official_monitor_quantity"],
        "official_structural_model": policy["official_structural_model"],
        "our_equivalent_flap_tip_displacement_available": bool(
            smoke_row["our_equivalent_flap_tip_displacement_available"]
        ),
        "our_geometry_mutation_enabled": bool(policy["our_geometry_mutation_enabled"]),
        "our_solver_dimensionality": policy["our_solver_dimensionality"],
        "our_solver_has_inf": bool(smoke_row["has_inf"]),
        "our_solver_has_nan": bool(smoke_row["has_nan"]),
        "our_solver_run_stable": bool(smoke_row["stable"]),
        "our_structural_model_equivalent": bool(policy["our_structural_model_equivalent"]),
        "smoke_matrix_pass": bool(smoke_summary["step103_fluent_inspired_duct_flap_proxy_smoke_matrix_pass"]),
        "step103_fluent_solver_gap_comparison_pass": False,
        "validation_claim_allowed": bool(policy["validation_claim_allowed"]),
    }
    summary["step103_fluent_solver_gap_comparison_pass"] = bool(
        summary["smoke_matrix_pass"]
        and summary["our_solver_run_stable"]
        and not summary["our_solver_has_nan"]
        and not summary["our_solver_has_inf"]
        and summary["official_case_dimensionality"] == "2D"
        and summary["our_solver_dimensionality"] == "3D"
        and summary["direct_quantitative_equivalence_allowed"] is False
        and summary["validation_claim_allowed"] is False
        and summary["official_structural_model"] == "linear_elasticity_intrinsic_fsi"
        and summary["our_structural_model_equivalent"] is False
        and summary["official_dynamic_mesh"] is True
        and summary["our_geometry_mutation_enabled"] is False
        and summary["our_equivalent_flap_tip_displacement_available"] is False
        and summary["capability_gap_count"] >= 1
        and summary["official_fluent_files_used_as_runtime_input"] is False
    )
    write_gap_report(root, rows, summary)
    return rows, summary


def gap_row(name: str) -> dict:
    descriptions = {
        "dimensionality_equivalence": "official case is 2D while current solver is 3D",
        "conformal_mesh_equivalence": "official case uses conformal FSI mesh while current geometry is procedural proxy",
        "linear_elasticity_equivalence": "official case uses intrinsic linear elasticity while current solver does not match it",
        "dynamic_mesh_equivalence": "official case deforms mesh while current geometry mutation is diagnostic-only/no-op",
        "exact_flap_tip_displacement": "official monitor is displacement while current equivalent flap-tip monitor is unavailable",
        "dimensional_velocity_mapping": "official inlet is 10 m/s while current LBM velocity is nondimensional/mapped",
    }
    return {
        "capability_gap": name,
        "description": descriptions[name],
        "gap_present": True,
        "validation_claim_allowed": False,
    }


def write_gap_report(root: Path, rows: list[dict], summary: dict) -> None:
    out_dir = root / "outputs" / "step103_fluent_comparison"
    write_json(out_dir / "fluent_solver_gap_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "fluent_solver_gap_report.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "fluent_solver_gap_report.md",
        "Step103 Fluent Solver Gap Report",
        rows,
        ["capability_gap", "gap_present", "description", "validation_claim_allowed"],
    )
