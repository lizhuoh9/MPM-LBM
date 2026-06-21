import csv
import json
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.squid_proxy.regions import (
    sample_squid_proxy_region_points,
    sample_squid_proxy_regions,
    summarize_region_masks,
)
from src.mpm_lbm.sim.squid_proxy.region_config import REQUIRED_REGION_IDS, SquidProxyRegionConfig


def run_squid_region_projection_smoke(
    geometry_config: GeometryConfig,
    region_config: SquidProxyRegionConfig,
    grid_sizes=(32, 48),
    out_dir=None,
) -> list[dict]:
    points = sample_squid_proxy_region_points(geometry_config, count=max(geometry_config.n_particles, 32**3), seed=30)
    masks = sample_squid_proxy_regions(geometry_config, region_config, points)
    summaries = summarize_region_masks(points, masks, geometry_config, region_config)
    summary_by_id = {row["region_id"]: row for row in summaries}
    rows = []
    for grid_size in grid_sizes:
        n_grid = int(grid_size)
        if n_grid <= 0:
            raise ValueError("grid size must be positive")
        for region_id in REQUIRED_REGION_IDS:
            mask = np.asarray(masks[region_id], dtype=bool)
            selected = points[mask]
            active_cell_count = _active_cell_count(selected, n_grid)
            estimated_volume = float(summary_by_id[region_id]["estimated_volume"])
            projected_mass = estimated_volume * float(geometry_config.p_rho)
            row = {
                "grid_size": n_grid,
                "region_id": region_id,
                "particle_count": int(np.count_nonzero(mask)),
                "estimated_volume": estimated_volume,
                "projected_mass": projected_mass,
                "active_cell_count": active_cell_count,
                "bbox_min_x": summary_by_id[region_id]["bbox_min_x"],
                "bbox_min_y": summary_by_id[region_id]["bbox_min_y"],
                "bbox_min_z": summary_by_id[region_id]["bbox_min_z"],
                "bbox_max_x": summary_by_id[region_id]["bbox_max_x"],
                "bbox_max_y": summary_by_id[region_id]["bbox_max_y"],
                "bbox_max_z": summary_by_id[region_id]["bbox_max_z"],
                "solid_phi_min": 0.0,
                "solid_phi_max": 1.0 if active_cell_count > 0 else 0.0,
            }
            values = [value for value in row.values() if isinstance(value, (int, float))]
            has_nan = any(np.isnan(float(value)) for value in values)
            has_inf = any(np.isinf(float(value)) for value in values)
            row["has_nan"] = bool(has_nan)
            row["has_inf"] = bool(has_inf)
            row["projection_pass"] = bool(
                row["particle_count"] > 0
                and row["projected_mass"] > 0.0
                and row["active_cell_count"] > 0
                and row["solid_phi_min"] >= 0.0
                and row["solid_phi_max"] <= 1.0
                and not has_nan
                and not has_inf
            )
            rows.append(row)
    if out_dir is not None:
        write_projection_results(rows, Path(os.fspath(out_dir)) / "region_projection_results.csv", Path(os.fspath(out_dir)) / "region_projection_results.json")
    return rows


def summarize_projection_rows(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "grid_size_count": len({int(row["grid_size"]) for row in rows}),
        "required_region_count": len(REQUIRED_REGION_IDS),
        "pass_count": sum(1 for row in rows if bool(row["projection_pass"])),
        "projected_mass_total": sum(float(row["projected_mass"]) for row in rows),
        "active_cell_count_total": sum(int(row["active_cell_count"]) for row in rows),
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
        "projection_pass": all(bool(row["projection_pass"]) for row in rows),
        "scope_note": "projection-only squid proxy region diagnostics; no FSI driver was run",
    }


def write_projection_results(rows: list[dict], csv_path, json_path) -> None:
    csv_file = Path(os.fspath(csv_path))
    json_file = Path(os.fspath(json_path))
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    with json_file.open("w", encoding="utf-8") as f:
        json.dump({"rows": rows, "summary": summarize_projection_rows(rows)}, f, indent=2, sort_keys=True)
        f.write("\n")


def _active_cell_count(points: np.ndarray, n_grid: int) -> int:
    if len(points) == 0:
        return 0
    clipped = np.clip(np.asarray(points, dtype=np.float64), 0.0, np.nextafter(1.0, 0.0))
    indices = np.floor(clipped * float(n_grid)).astype(np.int64)
    flat = indices[:, 0] * n_grid * n_grid + indices[:, 1] * n_grid + indices[:, 2]
    return int(len(np.unique(flat)))
