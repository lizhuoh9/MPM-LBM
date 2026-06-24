from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step105_common import summary_rows, write_csv_rows, write_json, write_markdown_table


GAP_FIELDS = [
    "gap_name",
    "gap_present",
    "official_reference",
    "current_proxy_state",
    "why_blocks_fluent_equivalence",
]


def step105_gap_rows() -> list[dict]:
    return [
        {
            "gap_name": "dimensionality_2D_vs_3D",
            "gap_present": True,
            "official_reference": "public tutorial is a 2D duct/flap case",
            "current_proxy_state": "current proxy solver is 3D on a 48^3 grid",
            "why_blocks_fluent_equivalence": "3D proxy dynamics and section averaging are not the official 2D formulation",
        },
        {
            "gap_name": "conformal_mesh_equivalence",
            "gap_present": True,
            "official_reference": "Fluent tutorial uses its mesh and intrinsic FSI setup",
            "current_proxy_state": "procedural duct/flap particles and static LBM duct geometry are used",
            "why_blocks_fluent_equivalence": "the committed proxy does not import or reproduce the official mesh",
        },
        {
            "gap_name": "linear_elasticity_equivalence",
            "gap_present": True,
            "official_reference": "official structural model is linear elasticity",
            "current_proxy_state": "current MPM stress path remains the existing corotated/hyperelastic implementation",
            "why_blocks_fluent_equivalence": "material parameters are mapped, but the constitutive update is not the Fluent structural model",
        },
        {
            "gap_name": "dynamic_mesh_equivalence",
            "gap_present": True,
            "official_reference": "official transient uses Fluent dynamic mesh with two-way FSI",
            "current_proxy_state": "current LBM geometry is static duct walls plus MPM moving-boundary coupling",
            "why_blocks_fluent_equivalence": "dynamic mesh deformation is not reproduced",
        },
        {
            "gap_name": "exact_fluent_monitor_equivalence",
            "gap_present": True,
            "official_reference": "official monitor is structural-point total displacement near the flap tip",
            "current_proxy_state": "current output is the mean displacement of the free-tip proxy particle mask",
            "why_blocks_fluent_equivalence": "the committed monitor is not the same point, interpolation, or averaging definition",
        },
        {
            "gap_name": "dimensional_velocity_mapping",
            "gap_present": True,
            "official_reference": "official inlet velocity is 10 m/s",
            "current_proxy_state": "target_u_lbm=[0.02,0,0] maps to about 0.0833333333 m/s for this proxy scale",
            "why_blocks_fluent_equivalence": "the current proxy inlet speed is not dimensionally equal to the official inlet speed",
        },
        {
            "gap_name": "turbulence_or_fluid_model_equivalence",
            "gap_present": True,
            "official_reference": "official run uses Fluent fluid-model settings",
            "current_proxy_state": "current solver uses the existing single-phase LBM setup and parameters",
            "why_blocks_fluent_equivalence": "fluid-model and solver numerics are not matched",
        },
        {
            "gap_name": "steady_preflow_initial_condition",
            "gap_present": True,
            "official_reference": "official transient starts from a steady fluid-flow pre-solve",
            "current_proxy_state": "current Step105 transient starts from the initialized quiescent LBM field",
            "why_blocks_fluent_equivalence": "the transient initial flow field is not the official steady preflow state",
        },
    ]


def build_step105_gap_taxonomy(root: Path) -> tuple[list[dict], dict]:
    rows = step105_gap_rows()
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "gap_count": len(rows),
        "gap_taxonomy_report_pass": False,
        "required_gap_count": 8,
        "validation_claim_allowed": False,
    }
    summary["gap_taxonomy_report_pass"] = bool(
        summary["gap_count"] >= summary["required_gap_count"]
        and not summary["direct_quantitative_equivalence_allowed"]
        and not summary["validation_claim_allowed"]
        and all(row["gap_present"] for row in rows)
    )
    return rows, summary


def write_step105_gap_taxonomy_artifacts(root: Path, rows: list[dict], summary: dict) -> None:
    out_dir = Path(root) / "outputs" / "step105_gap_taxonomy"
    write_json(out_dir / "gap_taxonomy_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "gap_taxonomy_report.csv", rows, GAP_FIELDS)
    write_csv_rows(out_dir / "gap_taxonomy_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(out_dir / "gap_taxonomy_report.md", "Step105 Gap Taxonomy Report", rows, GAP_FIELDS)
