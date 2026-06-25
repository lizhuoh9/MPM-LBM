from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step108_common import (
    numeric_values_finite,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)


MAPPING_FIELDS = [
    "low_mach_mapping_enabled",
    "duct_length_m",
    "n_grid",
    "dx_phys_m",
    "target_inlet_velocity_mps",
    "target_u_lbm",
    "lbm_dt_phys_s",
    "official_fsi_dt_s",
    "lbm_substeps_per_fsi_step",
    "mapped_inlet_velocity_mps",
    "mapped_velocity_error_mps",
    "mapping_pass",
]


def build_step108_dimensional_mapping(
    root: Path,
    policy_path: str = "configs/step108_low_mach_subcycling_policy.json",
) -> dict:
    root = Path(root)
    policy = read_json(root / policy_path)
    mapping = compute_mapping(policy)
    out_dir = root / "outputs" / "step108_dimensional_mapping"
    reset_output_dir(out_dir, root / "outputs")
    write_json(out_dir / "low_mach_subcycling_mapping_report.json", mapping)
    write_csv_rows(out_dir / "low_mach_subcycling_mapping_report.csv", [mapping], MAPPING_FIELDS)
    write_csv_rows(out_dir / "low_mach_subcycling_mapping_summary.csv", summary_rows(mapping), ["metric", "value"])
    write_markdown_table(
        out_dir / "low_mach_subcycling_mapping_report.md",
        "Step108 Low-Mach Subcycling Mapping",
        [mapping],
        MAPPING_FIELDS,
        note="This mapping keeps the LBM inlet at low Mach while matching the public tutorial 10 m/s inlet speed dimensionally.",
    )
    if not mapping["mapping_pass"]:
        raise RuntimeError(f"Step108 dimensional mapping failed: {mapping}")
    return mapping


def compute_mapping(policy: dict) -> dict:
    duct_length_m = float(policy["physical_duct_length_m"])
    n_grid = int(policy["n_grid"])
    dx_phys_m = duct_length_m / float(n_grid)
    target_inlet_velocity_mps = float(policy["target_inlet_velocity_mps"])
    target_u_lbm = float(policy["target_u_lbm"])
    lbm_dt_phys_s = float(policy["lbm_dt_phys_s"])
    official_fsi_dt_s = float(policy["official_fsi_dt_s"])
    lbm_substeps = int(policy["lbm_substeps_per_fsi_step"])
    mapped_velocity = target_u_lbm * dx_phys_m / lbm_dt_phys_s
    error = mapped_velocity - target_inlet_velocity_mps
    tolerance = float(policy["mapped_inlet_velocity_tolerance_mps"])
    mapping = {
        "duct_length_m": duct_length_m,
        "dx_phys_m": dx_phys_m,
        "lbm_dt_phys_s": lbm_dt_phys_s,
        "lbm_substeps_per_fsi_step": lbm_substeps,
        "low_mach_mapping_enabled": bool(policy["low_mach_mapping_enabled"]),
        "mapped_inlet_velocity_mps": mapped_velocity,
        "mapped_velocity_error_mps": error,
        "n_grid": n_grid,
        "official_fsi_dt_s": official_fsi_dt_s,
        "target_inlet_velocity_mps": target_inlet_velocity_mps,
        "target_u_lbm": target_u_lbm,
    }
    mapping["mapping_pass"] = bool(
        mapping["low_mach_mapping_enabled"]
        and n_grid == 48
        and target_u_lbm <= 0.03
        and lbm_substeps == 120
        and abs(error) <= tolerance
        and abs(official_fsi_dt_s - lbm_substeps * lbm_dt_phys_s) <= 1.0e-15
        and numeric_values_finite(mapping)
    )
    return mapping
