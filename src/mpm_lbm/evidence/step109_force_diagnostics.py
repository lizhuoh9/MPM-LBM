from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step109_common import (
    numeric_values_finite,
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)


FORCE_FIELDS = [
    "row_name",
    "matrix_family",
    "mb_force_cap_norm",
    "mb_reaction_scale",
    "hydro_force_max_norm_max",
    "max_grid_reaction_norm_max",
    "max_grid_reaction_to_cap_ratio",
    "active_reaction_particle_count_final",
    "peak_solver_m",
    "peak_ratio",
    "stable",
]

STRUCTURAL_FIELDS = [
    "row_name",
    "youngs_modulus",
    "density",
    "mb_force_cap_norm",
    "mb_reaction_scale",
    "peak_solver_m",
    "peak_ratio",
    "relative_to_base_peak",
    "stable",
]


def build_step109_force_and_structural_diagnostics(root: Path) -> tuple[dict, dict]:
    root = Path(root)
    matrix = read_json(root / "outputs" / "step109_response_sensitivity_matrix" / "response_matrix_report.json")
    out_dir = root / "outputs" / "step109_diagnostics"
    reset_output_dir(out_dir, root / "outputs")
    rows = matrix["rows"]
    force_rows = [force_row(row) for row in rows]
    force_summary = force_summary_from_rows(force_rows, matrix["summary"])
    structural_rows = structural_rows_from_matrix(rows)
    structural_summary = structural_summary_from_rows(structural_rows)
    write_json(out_dir / "force_cap_diagnostics_report.json", {"summary": force_summary, "rows": force_rows})
    write_csv_rows(out_dir / "force_cap_diagnostics_report.csv", force_rows, FORCE_FIELDS)
    write_csv_rows(out_dir / "force_cap_diagnostics_summary.csv", summary_rows(force_summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "force_cap_diagnostics_report.md",
        "Step109 Force-Cap Diagnostics",
        force_rows,
        FORCE_FIELDS,
        note="Force rows are diagnostics for the proxy matrix, not Fluent force-transfer validation.",
    )
    write_json(out_dir / "structural_sensitivity_report.json", {"summary": structural_summary, "rows": structural_rows})
    write_csv_rows(out_dir / "structural_sensitivity_report.csv", structural_rows, STRUCTURAL_FIELDS)
    write_csv_rows(out_dir / "structural_sensitivity_summary.csv", summary_rows(structural_summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "structural_sensitivity_report.md",
        "Step109 Structural Sensitivity",
        structural_rows,
        STRUCTURAL_FIELDS,
        note="Material rows vary proxy MPM material parameters only; they do not reproduce the official structural model.",
    )
    if not force_summary["force_cap_diagnostics_pass"]:
        raise RuntimeError(f"Step109 force diagnostics failed: {force_summary}")
    if not structural_summary["structural_sensitivity_report_pass"]:
        raise RuntimeError(f"Step109 structural diagnostics failed: {structural_summary}")
    return {"summary": force_summary, "rows": force_rows}, {"summary": structural_summary, "rows": structural_rows}


def force_row(row: dict) -> dict:
    return {
        "active_reaction_particle_count_final": int(row["active_reaction_particle_count_final"]),
        "hydro_force_max_norm_max": float(row["hydro_force_max_norm_max"]),
        "matrix_family": row["matrix_family"],
        "max_grid_reaction_norm_max": float(row["max_grid_reaction_norm_max"]),
        "max_grid_reaction_to_cap_ratio": float(row["max_grid_reaction_to_cap_ratio"]),
        "mb_force_cap_norm": float(row["mb_force_cap_norm"]),
        "mb_reaction_scale": float(row["mb_reaction_scale"]),
        "peak_ratio": float(row["peak_ratio"]),
        "peak_solver_m": float(row["peak_solver_m"]),
        "row_name": row["row_name"],
        "stable": bool(row["stable"]),
    }


def force_summary_from_rows(rows: list[dict], matrix_summary: dict) -> dict:
    stable = [row for row in rows if row["stable"]]
    summary = {
        "all_force_metrics_finite": all(numeric_values_finite(row) for row in rows),
        "best_peak_solver_m": float(matrix_summary["best_peak_solver_m"]),
        "force_cap_diagnostics_pass": False,
        "row_count": len(rows),
        "stable_row_count": len(stable),
    }
    summary["force_cap_diagnostics_pass"] = bool(
        len(rows) >= 6
        and len(stable) >= 5
        and summary["best_peak_solver_m"] > 1.0e-5
        and summary["all_force_metrics_finite"]
    )
    return summary


def structural_rows_from_matrix(rows: list[dict]) -> list[dict]:
    base_peak = next((abs(float(row["peak_solver_m"])) for row in rows if row["row_name"] == "base"), 0.0)
    structural = []
    for row in rows:
        if row["matrix_family"] != "structural_stiffness":
            continue
        structural.append(
            {
                "density": float(row["density"]),
                "mb_force_cap_norm": float(row["mb_force_cap_norm"]),
                "mb_reaction_scale": float(row["mb_reaction_scale"]),
                "peak_ratio": float(row["peak_ratio"]),
                "peak_solver_m": float(row["peak_solver_m"]),
                "relative_to_base_peak": safe_ratio(abs(float(row["peak_solver_m"])), base_peak),
                "row_name": row["row_name"],
                "stable": bool(row["stable"]),
                "youngs_modulus": float(row["youngs_modulus"]),
            }
        )
    return structural


def structural_summary_from_rows(rows: list[dict]) -> dict:
    summary = {
        "all_structural_metrics_finite": all(numeric_values_finite(row) for row in rows),
        "stable_structural_row_count": sum(1 for row in rows if row["stable"]),
        "stiffness_reduction_order_of_magnitude_response": any(
            float(row["relative_to_base_peak"]) >= 10.0 for row in rows if row["stable"]
        ),
        "structural_row_count": len(rows),
        "structural_sensitivity_report_pass": False,
    }
    summary["structural_sensitivity_report_pass"] = bool(
        summary["structural_row_count"] >= 2
        and summary["stable_structural_row_count"] >= 1
        and summary["all_structural_metrics_finite"]
    )
    return summary
