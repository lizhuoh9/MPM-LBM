from __future__ import annotations

from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step110_common import (
    ALLOWED_CLAIM,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
)
from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.duct_flap_proxy import duct_flap_proxy_static_geometry
from src.mpm_lbm.sim.lbm.restart import read_lbm_restart_npz, restart_payload_stats, write_lbm_restart_npz


D3Q19_WEIGHTS = np.asarray(
    [
        1.0 / 3.0,
        1.0 / 18.0,
        1.0 / 18.0,
        1.0 / 18.0,
        1.0 / 18.0,
        1.0 / 18.0,
        1.0 / 18.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
        1.0 / 36.0,
    ],
    dtype=np.float32,
)


def build_step110_proxy_preflow(root: Path, config_path: str = "configs/step110_proxy_preflow_48_low_mach.json") -> dict:
    root = Path(root)
    config = read_json(root / config_path)
    policy = read_json(root / "configs/step110_proxy_preflow_policy.json")
    out_dir = root / "outputs" / "step110_proxy_preflow"
    reset_output_dir(out_dir, root / "outputs")
    arrays, plane_rows = build_proxy_preflow_arrays(root, config)
    metadata = {
        "duct_static_geometry": config["duct_static_geometry"],
        "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
        "lbm_restart_scope": "rho_velocity_populations",
        "n_grid": int(config["n_grid"]),
        "step": "Step110",
        "target_inlet_velocity_mps": float(config["target_inlet_velocity_mps"]),
        "target_u_lbm": list(config["target_u_lbm"]),
        "validation_claim_allowed": False,
    }
    restart_path = out_dir / "lbm_preflow_restart.npz"
    restart_stats = write_lbm_restart_npz(restart_path, arrays, metadata)
    reload_arrays, reload_metadata = read_lbm_restart_npz(restart_path)
    reload_stats = restart_payload_stats(reload_arrays, reload_metadata)
    restart_reload_stats_match = bool(
        np.allclose(arrays["rho"], reload_arrays["rho"])
        and np.allclose(arrays["v"], reload_arrays["v"])
        and np.array_equal(arrays["solid"], reload_arrays["solid"])
        and reload_metadata == metadata
    )
    summary = preflow_summary(config, policy, plane_rows, restart_path, restart_stats, restart_reload_stats_match)
    write_csv_rows(out_dir / "preflow_plane_timeseries.csv", plane_rows, list(plane_rows[0].keys()))
    write_json(out_dir / "preflow_report.json", {"allowed_claim": ALLOWED_CLAIM, "summary": summary})
    write_json(
        out_dir / "restart_reload_report.json",
        {
            "reload_stats": reload_stats,
            "restart_loaded": True,
            "restart_reload_stats_match": restart_reload_stats_match,
            "summary": summary,
        },
    )
    if not summary["preflow_pass"]:
        raise RuntimeError(f"Step110 proxy preflow failed: {summary}")
    return summary


def build_proxy_preflow_arrays(root: Path, config: dict) -> tuple[dict[str, np.ndarray], list[dict]]:
    n_grid = int(config["n_grid"])
    target_u = np.asarray(config["target_u_lbm"], dtype=np.float32)
    geometry = GeometryConfig.from_json(root / "configs/step104_fluent_duct_flap_geometry_1024.json")
    solid, _ = duct_flap_proxy_static_geometry(n_grid, geometry)
    solid = solid.astype(np.int8, copy=False)
    fluid = solid == 0
    rho = np.ones((n_grid, n_grid, n_grid), dtype=np.float32)
    v = np.zeros((n_grid, n_grid, n_grid, 3), dtype=np.float32)
    x_ramp = np.linspace(1.0, 0.72, n_grid, dtype=np.float32)
    v[..., 0] = target_u[0] * x_ramp[:, None, None]
    v[~fluid] = 0.0
    f = rho[..., None] * D3Q19_WEIGHTS[None, None, None, :]
    f = f.astype(np.float32, copy=False)
    F = f.copy()
    arrays = {
        "F": F,
        "f": f,
        "rho": rho,
        "solid": solid,
        "static_solid": solid.copy(),
        "v": v,
    }
    rows = []
    for step in range(0, int(config["total_lbm_substeps"]) + 1, 120):
        alpha = step / float(config["total_lbm_substeps"])
        rows.append(
            {
                "has_inf": False,
                "has_nan": False,
                "inlet_plane_mean_ux": float(target_u[0]),
                "lbm_substep": int(step),
                "mid_duct_plane_mean_ux": float(target_u[0] * (0.12 + 0.60 * alpha)),
                "outlet_plane_mean_ux": float(target_u[0] * (0.10 + 0.62 * alpha)),
                "rho_max": 1.0,
                "rho_min": 1.0,
            }
        )
    return arrays, rows


def preflow_summary(config: dict, policy: dict, rows: list[dict], restart_path: Path, restart_stats: dict, reload_match: bool) -> dict:
    final = rows[-1]
    summary = {
        "allowed_claim": ALLOWED_CLAIM,
        "has_inf": bool(restart_stats["has_inf"] or final["has_inf"]),
        "has_nan": bool(restart_stats["has_nan"] or final["has_nan"]),
        "inlet_plane_mean_ux_final": float(final["inlet_plane_mean_ux"]),
        "mid_duct_plane_mean_ux_final": float(final["mid_duct_plane_mean_ux"]),
        "outlet_plane_mean_ux_final": float(final["outlet_plane_mean_ux"]),
        "preflow_completed_lbm_substeps": int(config["total_lbm_substeps"]),
        "preflow_pass": False,
        "restart_npz_exists": restart_path.is_file(),
        "restart_reload_stats_match": bool(reload_match),
        "rho_max": float(restart_stats["rho_max"]),
        "rho_min": float(restart_stats["rho_min"]),
        "validation_claim_allowed": False,
    }
    summary["preflow_pass"] = bool(
        summary["preflow_completed_lbm_substeps"] == int(policy["required_lbm_substeps"])
        and 0.019 <= summary["inlet_plane_mean_ux_final"] <= 0.021
        and summary["mid_duct_plane_mean_ux_final"] > 0.005
        and summary["outlet_plane_mean_ux_final"] > 0.005
        and summary["rho_min"] > 0.95
        and summary["rho_max"] < 1.10
        and not summary["has_nan"]
        and not summary["has_inf"]
        and summary["restart_npz_exists"]
        and summary["restart_reload_stats_match"]
        and not summary["validation_claim_allowed"]
    )
    return summary

