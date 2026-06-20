import os

from step31_common import (
    ROOT,
    STEP31_GEOMETRY_CONFIG_PATH,
    STEP31_REGION_CONFIG_PATH,
    summary_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.squid_region_config import REQUIRED_REGION_IDS
from src.squid_region_driver_diagnostics import load_region_driver_context
from src.squid_region_projection import run_squid_region_projection_smoke, summarize_projection_rows


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    geometry_config, region_config = load_region_driver_context(STEP31_GEOMETRY_CONFIG_PATH, STEP31_REGION_CONFIG_PATH)
    rows = run_squid_region_projection_smoke(geometry_config, region_config, grid_sizes=(32, 48, 64), out_dir=None)
    summary = summarize_projection_rows(rows)
    assert_projection_scale_summary(summary, rows)

    out_dir = ROOT / "outputs" / "step31_region_projection_scale"
    fieldnames = list(rows[0].keys()) if rows else []
    write_csv_rows(out_dir / "region_projection_scale.csv", rows, fieldnames)
    write_csv_rows(out_dir / "region_projection_scale_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "region_projection_scale.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 31 region projection scale finished"
    write_log(
        "logs/step31_region_projection_scale.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"grid_size_count={summary['grid_size_count']}",
            f"projected_mass_total={summary['projected_mass_total']}",
            f"active_cell_count_total={summary['active_cell_count_total']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


def assert_projection_scale_summary(summary, rows):
    if int(summary["row_count"]) != 21 or int(summary["grid_size_count"]) != 3:
        raise RuntimeError(f"Step 31 projection scale row/grid count is wrong: {summary}")
    if int(summary["required_region_count"]) != 7 or int(summary["pass_count"]) != 21:
        raise RuntimeError(f"Step 31 projection scale pass count is wrong: {summary}")
    if not bool(summary["projection_pass"]):
        raise RuntimeError(f"Step 31 projection scale failed: {summary}")
    if float(summary["projected_mass_total"]) <= 0.0 or int(summary["active_cell_count_total"]) <= 0:
        raise RuntimeError(f"Step 31 projection scale totals are invalid: {summary}")
    if int(summary["has_nan_count"]) != 0 or int(summary["has_inf_count"]) != 0:
        raise RuntimeError(f"Step 31 projection scale has NaN/Inf: {summary}")
    for grid_size in (32, 48, 64):
        region_ids = {row["region_id"] for row in rows if int(row["grid_size"]) == grid_size}
        if region_ids != set(REQUIRED_REGION_IDS):
            raise RuntimeError(f"Step 31 grid {grid_size} region set is wrong: {region_ids}")


if __name__ == "__main__":
    main()
