import csv
import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step14_common import RESULT_FIELDS, write_json  # noqa: E402
from src.performance import estimate_total_memory_bytes  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


SUMMARY_FIELDS = [
    "n_grid",
    "geometry_type",
    "mode",
    "n_particles",
    "stable",
    "total_time_sec",
    "estimated_memory_mb",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "notes",
]


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_memory_estimates(path):
    if not os.path.isfile(path):
        return []
    rows = []
    for row in read_csv(path):
        rows.append(
            {
                "n_grid": int(float(row["n_grid"])),
                "geometry_type": "memory_estimate",
                "mode": "reference",
                "n_particles": int(float(row["n_particles"])),
                "stable": "False",
                "total_time_sec": 0.0,
                "estimated_memory_mb": float(row["total_estimated_mb"]),
                "rho_min": 1.0,
                "rho_max": 1.0,
                "lbm_max_v": 0.0,
                "mpm_min_J": 1.0,
                "notes": "Step 12 lower-bound dense memory estimate; not a runtime validation row",
            }
        )
    return rows


def result_to_summary(row):
    return {
        "n_grid": int(float(row["n_grid"])),
        "geometry_type": row["geometry_type"],
        "mode": row["mode"],
        "n_particles": int(float(row["n_particles"])),
        "stable": row["stable"],
        "total_time_sec": float(row["total_time_sec"]),
        "estimated_memory_mb": float(row["estimated_memory_mb"]),
        "rho_min": float(row["rho_min"]),
        "rho_max": float(row["rho_max"]),
        "lbm_max_v": float(row["lbm_max_v"]),
        "mpm_min_J": float(row["mpm_min_J"]),
        "notes": row.get("notes", ""),
    }


def validate_summary(rows):
    grids = {int(row["n_grid"]) for row in rows}
    if not {32, 48, 64}.issubset(grids):
        raise RuntimeError(f"scaling summary missing grid references: {sorted(grids)}")
    stable_rows = [row for row in rows if row["stable"] == "True"]
    if not stable_rows:
        raise RuntimeError("scaling summary has no stable runtime rows")
    for row in stable_rows:
        numeric = [
            row["n_grid"],
            row["n_particles"],
            row["total_time_sec"],
            row["estimated_memory_mb"],
            row["rho_min"],
            row["rho_max"],
            row["lbm_max_v"],
            row["mpm_min_J"],
        ]
        if not np.all(np.isfinite(numeric)):
            raise RuntimeError("scaling summary contains NaN or Inf")
        if float(row["estimated_memory_mb"]) <= 0.0:
            raise RuntimeError("scaling summary estimated_memory_mb must be positive")


def main():
    out_dir = os.path.join(ROOT, "outputs", "step14_scaling_summary")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 14 scaling summary")
    rows = read_memory_estimates(os.path.join(ROOT, "outputs", "step12_memory_estimate", "memory_estimate.csv"))

    source_paths = [
        os.path.join(ROOT, "outputs", "step14_scale_box_48", "box_48_results.csv"),
        os.path.join(ROOT, "outputs", "step14_scale_squid_proxy_48", "squid_proxy_48_results.csv"),
        os.path.join(ROOT, "outputs", "step14_feasibility_64", "feasibility_64_results.csv"),
    ]
    for path in source_paths:
        rows.extend(result_to_summary(row) for row in read_csv(path))

    # Ensure the 48^3 lower-bound estimate is represented even though Step 12 did not emit that grid.
    if 48 not in {int(row["n_grid"]) for row in rows}:
        estimate = estimate_total_memory_bytes(48, 13824)
        rows.append(
            {
                "n_grid": 48,
                "geometry_type": "memory_estimate",
                "mode": "reference",
                "n_particles": 13824,
                "stable": "False",
                "total_time_sec": 0.0,
                "estimated_memory_mb": float(estimate["total_estimated_mb"]),
                "rho_min": 1.0,
                "rho_max": 1.0,
                "lbm_max_v": 0.0,
                "mpm_min_J": 1.0,
                "notes": "Step 14 computed lower-bound dense memory estimate; not a runtime validation row",
            }
        )

    validate_summary(rows)
    csv_path = os.path.join(out_dir, "scaling_summary.csv")
    json_path = os.path.join(out_dir, "scaling_summary.json")
    save_csv_rows(rows, csv_path, fieldnames=SUMMARY_FIELDS)
    write_json(
        {
            "row_count": len(rows),
            "grid_references": sorted({int(row["n_grid"]) for row in rows}),
            "stable_runtime_rows": sum(1 for row in rows if row["stable"] == "True"),
            "scope_note": "Step 14 engineering scale baseline summary; not production benchmark.",
            "columns": SUMMARY_FIELDS,
            "result_source_columns": RESULT_FIELDS,
        },
        json_path,
    )

    print(f"row_count={len(rows)}")
    print(f"grid_references={sorted({int(row['n_grid']) for row in rows})}")
    print(f"csv={csv_path}")
    print(f"json={json_path}")
    print("[OK] Step 14 scaling summary finished")


if __name__ == "__main__":
    main()
