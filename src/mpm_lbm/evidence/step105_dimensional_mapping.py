from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step105_common import STEP105_ROW_NAME, summary_rows, write_csv_rows, write_json, write_markdown_table


FIELDS = [
    "row_name",
    "n_grid",
    "dx_norm",
    "mpm_dt",
    "lbm_dt_phys",
    "duct_length_m",
    "target_u_lbm",
    "proxy_inlet_velocity_mps",
    "official_inlet_velocity_mps",
    "velocity_ratio",
    "dimensional_velocity_mapping_gap_present",
    "mapping_formula",
    "direct_quantitative_equivalence_allowed",
    "validation_claim_allowed",
]


def build_step105_dimensional_mapping(
    root: Path,
    run_config_path: str = "configs/step105_fluent_duct_flap_proxy_48_50step_transient_gap_smoke.json",
) -> tuple[list[dict], dict]:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.geometry.config import GeometryConfig

    root = Path(root)
    config = FSIDriverConfig.from_json(root / run_config_path)
    geometry_config = GeometryConfig.from_json(str(root / config.geometry_config_path))
    sim_config = config.make_unified_sim_config()
    dimensional = geometry_config.dimensional_reference or {}
    duct_length_m = float(dimensional["duct_length_m"])
    official_inlet_velocity_mps = float(dimensional["inlet_velocity_mps"])
    dx_norm = float(sim_config.dx_norm)
    lbm_dt_phys = float(sim_config.lbm_dt_phys)
    proxy_velocity = float(config.target_u_lbm[0]) * dx_norm / lbm_dt_phys * duct_length_m
    velocity_ratio = proxy_velocity / official_inlet_velocity_mps
    row = {
        "dimensional_velocity_mapping_gap_present": True,
        "direct_quantitative_equivalence_allowed": False,
        "duct_length_m": duct_length_m,
        "dx_norm": dx_norm,
        "lbm_dt_phys": lbm_dt_phys,
        "mapping_formula": "target_u_lbm_x * dx_norm / lbm_dt_phys * duct_length_m",
        "mpm_dt": float(config.mpm_dt),
        "n_grid": int(config.n_grid),
        "official_inlet_velocity_mps": official_inlet_velocity_mps,
        "proxy_inlet_velocity_mps": proxy_velocity,
        "row_name": STEP105_ROW_NAME,
        "target_u_lbm": list(config.target_u_lbm),
        "validation_claim_allowed": False,
        "velocity_ratio": velocity_ratio,
    }
    rows = [row]
    summary = {
        "dimensional_mapping_report_pass": bool(
            row["dimensional_velocity_mapping_gap_present"]
            and row["proxy_inlet_velocity_mps"] < row["official_inlet_velocity_mps"]
            and not row["direct_quantitative_equivalence_allowed"]
            and not row["validation_claim_allowed"]
        ),
        "row_count": 1,
    }
    return rows, summary


def write_step105_dimensional_mapping_artifacts(root: Path, rows: list[dict], summary: dict) -> None:
    out_dir = Path(root) / "outputs" / "step105_dimensional_mapping"
    write_json(out_dir / "velocity_mapping_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "velocity_mapping_report.csv", rows, FIELDS)
    write_csv_rows(out_dir / "velocity_mapping_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(out_dir / "velocity_mapping_report.md", "Step105 Velocity Mapping Report", rows, FIELDS)
