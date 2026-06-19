import os

from step25_common import ROOT, STEP25_DESCRIPTORS, write_csv_rows, write_json, write_log
from src.geometry_intake import run_candidate_projection_smoke


FIELDS = [
    "candidate_id",
    "geometry_type",
    "projected_mass",
    "projected_volume_raw",
    "projected_volume_clamped",
    "max_phi_raw",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "has_nan",
    "has_inf",
    "projection_pass",
    "scope_note",
]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step25_projection_smoke"
    rows = [run_candidate_projection_smoke(path, out_dir) for path in STEP25_DESCRIPTORS]
    for row in rows:
        _assert_projection_row(row)

    write_csv_rows(out_dir / "projection_smoke_results.csv", rows, FIELDS)
    write_json(out_dir / "projection_smoke_results.json", {"row_count": len(rows), "rows": rows})
    marker = "[OK] Step 25 projection smoke finished"
    write_log(
        "logs/step25_projection_smoke.log",
        [
            marker,
            f"row_count={len(rows)}",
            "scope=projection_only_no_fsi_driver_long_run",
        ],
    )
    print(f"row_count={len(rows)}")
    print(marker)


def _assert_projection_row(row):
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")
    if float(row["solid_phi_min"]) < 0.0:
        raise RuntimeError(f"solid_phi_min must be non-negative: {row}")
    if float(row["solid_phi_max"]) > 1.0:
        raise RuntimeError(f"solid_phi_max must be <= 1: {row}")
    if row["has_nan"] or row["has_inf"]:
        raise RuntimeError(f"projection smoke produced NaN or Inf: {row}")
    if "projection-only" not in row["scope_note"]:
        raise RuntimeError(f"projection smoke must be scoped as projection-only: {row}")
    if row["projection_pass"] is not True:
        raise RuntimeError(f"projection smoke failed: {row}")


if __name__ == "__main__":
    main()
