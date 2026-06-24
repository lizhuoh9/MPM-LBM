from __future__ import annotations


def step104_gap_fields() -> dict:
    return {
        "direct_quantitative_equivalence_allowed": False,
        "gap_dynamic_mesh_equivalence": True,
        "gap_exact_fluent_monitor_equivalence": True,
        "gap_linear_elasticity_equivalence": True,
        "official_case_dimensionality": "2D",
        "official_dynamic_mesh": True,
        "official_monitor_quantity": "total_displacement",
        "official_structural_model": "linear_elasticity_intrinsic_fsi",
        "our_geometry_mutation_enabled": False,
        "our_solver_dimensionality": "3D",
        "our_structural_model_equivalent": False,
        "proxy_flap_tip_displacement_available": True,
        "validation_claim_allowed": False,
    }


def step104_capability_gap_count(fields: dict) -> int:
    return sum(
        1
        for key in (
            "gap_dynamic_mesh_equivalence",
            "gap_exact_fluent_monitor_equivalence",
            "gap_linear_elasticity_equivalence",
        )
        if bool(fields.get(key, False))
    )
