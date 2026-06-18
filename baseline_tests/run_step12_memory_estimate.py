import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.performance import estimate_total_memory_bytes  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


FIELDS = [
    "n_grid",
    "n_cells",
    "n_particles",
    "lbm_estimated_mb",
    "mpm_particle_estimated_mb",
    "mpm_grid_estimated_mb",
    "coupling_estimated_mb",
    "total_estimated_mb",
]


def validate_rows(rows):
    totals = [float(row["total_estimated_mb"]) for row in rows]
    if not np.all(np.isfinite(totals)):
        raise RuntimeError("memory estimate contains NaN or Inf")
    if not all(a < b for a, b in zip(totals, totals[1:])):
        raise RuntimeError("memory estimate totals are not monotonically increasing")
    if totals[0] >= 1024.0:
        raise RuntimeError("32^3 lower-bound memory estimate unexpectedly exceeds 1 GB")


def main():
    cases = [
        (32, 4096),
        (64, 32768),
        (96, 110592),
        (128, 262144),
    ]
    out_dir = os.path.join(ROOT, "outputs", "step12_memory_estimate")
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    print("Step 12 memory estimate")
    for n_grid, n_particles in cases:
        row = estimate_total_memory_bytes(n_grid=n_grid, n_particles=n_particles)
        rows.append(row)
        print(
            f"n_grid={n_grid}, n_cells={row['n_cells']}, n_particles={n_particles}, "
            f"lbm_estimated_mb={row['lbm_estimated_mb']:.6f}, "
            f"mpm_particle_estimated_mb={row['mpm_particle_estimated_mb']:.6f}, "
            f"mpm_grid_estimated_mb={row['mpm_grid_estimated_mb']:.6f}, "
            f"coupling_estimated_mb={row['coupling_estimated_mb']:.6f}, "
            f"total_estimated_mb={row['total_estimated_mb']:.6f}"
        )

    validate_rows(rows)
    save_csv_rows(rows, os.path.join(out_dir, "memory_estimate.csv"), fieldnames=FIELDS)
    np.savez(
        os.path.join(out_dir, "memory_estimate.npz"),
        columns=np.asarray(FIELDS),
        rows=np.asarray([[row[field] for field in FIELDS] for row in rows], dtype=np.float64),
    )
    print("[OK] Step 12 memory estimate finished")


if __name__ == "__main__":
    main()
