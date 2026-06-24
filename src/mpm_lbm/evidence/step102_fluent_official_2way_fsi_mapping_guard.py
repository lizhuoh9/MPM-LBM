from __future__ import annotations

import json
from pathlib import Path


EXPECTED_MAPPING_VALUES = {
    "mapping_status": "intake_only",
    "direct_equivalence_claim_allowed": False,
    "validation_claim_allowed": False,
    "official_case_dimensionality": "2D",
    "current_solver_dimensionality": "3D",
    "official_mesh_type": "2D conformal fluid-solid mesh",
    "current_solver_geometry_type": "procedural_squid_proxy_or_future_procedural_proxy",
    "official_structure_model": "linear_elasticity_intrinsic_fsi",
    "current_structure_proxy": "mpm_particles_or_future_duct_flap_proxy",
    "comparison_level_allowed_initially": "qualitative_and_diagnostic_only",
    "quantitative_match_claim_allowed": False,
    "recommended_future_solver_proxy": "procedural_duct_flap_proxy_not_official_mesh_import",
}


def build_step102_fluent_official_2way_fsi_mapping_guard(
    root: Path,
    policy_path: str = "configs/step102_fluent_official_2way_fsi_mapping_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [mapping_row(policy, key, expected) for key, expected in EXPECTED_MAPPING_VALUES.items()]
    summary = {key: policy[key] for key in EXPECTED_MAPPING_VALUES}
    summary.update(
        {
            "allowed_initial_observable_count": len(policy["allowed_initial_observables"]),
            "forbidden_initial_observable_count": len(policy["forbidden_initial_observables"]),
            "pass_count": sum(1 for row in rows if row["pass"]),
            "row_count": len(rows),
            "step102_fluent_official_2way_fsi_mapping_guard_pass": False,
        }
    )
    summary["step102_fluent_official_2way_fsi_mapping_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["mapping_status"] == "intake_only"
        and summary["direct_equivalence_claim_allowed"] is False
        and summary["validation_claim_allowed"] is False
        and summary["quantitative_match_claim_allowed"] is False
        and summary["comparison_level_allowed_initially"] == "qualitative_and_diagnostic_only"
        and summary["recommended_future_solver_proxy"] == "procedural_duct_flap_proxy_not_official_mesh_import"
    )
    return rows, summary


def mapping_row(policy: dict, key: str, expected) -> dict:
    actual = policy.get(key)
    return {
        "actual": actual,
        "check": key,
        "expected": expected,
        "pass": actual == expected,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
