from __future__ import annotations

import json
from pathlib import Path


EXPECTED_METADATA_VALUES = {
    "step": "Step102",
    "benchmark_id": "fluent_official_2way_intrinsic_fsi_duct_flap",
    "source_release": "2024 R2",
    "official_case_archive_name": "fsi_2way.zip",
    "problem_family": "two_way_intrinsic_fsi",
    "fluent_model_type": "intrinsic_fsi",
    "official_case_dimensionality": "2D",
    "duct_length_m": 0.10,
    "duct_height_m": 0.04,
    "flap_height_m": 0.01,
    "flap_thickness_m": 0.003,
    "inlet_velocity_m_per_s": 10.0,
    "outlet_type": "pressure_outlet",
    "source_access_policy": "user_local_access_required",
    "source_content_policy": "do_not_commit_ansys_proprietary_files_or_large_verbatim_excerpts",
    "step102_driver_run_required": False,
    "step102_simulation_run_allowed": False,
    "step102_fluent_run_allowed": False,
    "step102_benchmark_comparison_allowed": False,
    "step102_validation_claim_allowed": False,
}


def build_step102_fluent_official_2way_fsi_benchmark_intake(
    root: Path,
    metadata_path: str = "configs/step102_fluent_official_2way_fsi_benchmark_source_metadata.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    metadata = read_json(root / metadata_path)
    rows = [metadata_row(metadata, key, expected) for key, expected in EXPECTED_METADATA_VALUES.items()]
    rows.extend(
        [
            metadata_row(metadata["solid_material"], "density", 1600.0, "solid_material.density"),
            metadata_row(metadata["solid_material"], "youngs_modulus", 1000000.0, "solid_material.youngs_modulus"),
            metadata_row(metadata["solid_material"], "poisson_ratio", 0.47, "solid_material.poisson_ratio"),
            metadata_row(
                metadata["fluent_transient_settings"],
                "number_of_time_steps",
                50,
                "fluent_transient_settings.number_of_time_steps",
            ),
            metadata_row(
                metadata["fluent_transient_settings"],
                "time_step_size_s",
                0.0005,
                "fluent_transient_settings.time_step_size_s",
            ),
            metadata_row(
                metadata["fluent_transient_settings"],
                "max_iterations_per_time_step",
                40,
                "fluent_transient_settings.max_iterations_per_time_step",
            ),
            metadata_row(metadata["official_monitor"], "x", 0.0505, "official_monitor.x"),
            metadata_row(metadata["official_monitor"], "y", 0.0095, "official_monitor.y"),
        ]
    )
    official_files = list(metadata["official_files_expected_locally"])
    summary = {
        "benchmark_id": metadata["benchmark_id"],
        "duct_height_m": metadata["duct_height_m"],
        "duct_length_m": metadata["duct_length_m"],
        "flap_height_m": metadata["flap_height_m"],
        "flap_thickness_m": metadata["flap_thickness_m"],
        "fluent_model_type": metadata["fluent_model_type"],
        "inlet_velocity_m_per_s": metadata["inlet_velocity_m_per_s"],
        "max_iterations_per_time_step": metadata["fluent_transient_settings"]["max_iterations_per_time_step"],
        "number_of_time_steps": metadata["fluent_transient_settings"]["number_of_time_steps"],
        "official_archive_name": metadata["official_case_archive_name"],
        "official_case_dimensionality": metadata["official_case_dimensionality"],
        "official_files_expected": ", ".join(official_files),
        "official_journal_name": official_files[1],
        "official_mesh_name": official_files[0],
        "official_monitor_x": metadata["official_monitor"]["x"],
        "official_monitor_y": metadata["official_monitor"]["y"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "problem_family": metadata["problem_family"],
        "row_count": len(rows),
        "solid_density": metadata["solid_material"]["density"],
        "solid_poisson_ratio": metadata["solid_material"]["poisson_ratio"],
        "solid_youngs_modulus": metadata["solid_material"]["youngs_modulus"],
        "source_url": metadata["source_url"],
        "source_url_recorded": bool(metadata["source_url"].startswith("https://ansyshelp.ansys.com/")),
        "step102_benchmark_comparison_allowed": metadata["step102_benchmark_comparison_allowed"],
        "step102_driver_run_required": metadata["step102_driver_run_required"],
        "step102_fluent_run_allowed": metadata["step102_fluent_run_allowed"],
        "step102_fluent_official_2way_fsi_benchmark_intake_pass": False,
        "step102_simulation_run_allowed": metadata["step102_simulation_run_allowed"],
        "step102_validation_claim_allowed": metadata["step102_validation_claim_allowed"],
        "time_step_size_s": metadata["fluent_transient_settings"]["time_step_size_s"],
    }
    summary["step102_fluent_official_2way_fsi_benchmark_intake_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["source_url_recorded"] is True
        and summary["official_archive_name"] == "fsi_2way.zip"
        and summary["official_mesh_name"] == "flap.msh"
        and summary["official_journal_name"] == "steady_fluid_flow.jou"
        and summary["step102_driver_run_required"] is False
        and summary["step102_simulation_run_allowed"] is False
        and summary["step102_fluent_run_allowed"] is False
        and summary["step102_benchmark_comparison_allowed"] is False
        and summary["step102_validation_claim_allowed"] is False
    )
    return rows, summary


def metadata_row(source: dict, key: str, expected, label: str | None = None) -> dict:
    actual = source.get(key)
    return {
        "actual": actual,
        "check": label or key,
        "expected": expected,
        "pass": actual == expected,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
