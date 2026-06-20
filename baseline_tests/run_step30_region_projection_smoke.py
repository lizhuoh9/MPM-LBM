import os

from step30_common import ROOT, load_step30_geometry_config, load_step30_region_config, write_log
from src.squid_region_projection import run_squid_region_projection_smoke, summarize_projection_rows


def main():
    os.chdir(ROOT)
    geometry_config = load_step30_geometry_config()
    region_config = load_step30_region_config()
    out_dir = ROOT / "outputs" / "step30_region_projection_smoke"
    rows = run_squid_region_projection_smoke(geometry_config, region_config, grid_sizes=(32, 48), out_dir=out_dir)
    summary = summarize_projection_rows(rows)
    if not summary["projection_pass"]:
        raise RuntimeError(f"Step 30 projection smoke failed: {summary}")
    marker = "[OK] Step 30 region projection smoke finished"
    write_log(
        "logs/step30_region_projection_smoke.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"projected_mass_total={summary['projected_mass_total']}",
            f"active_cell_count_total={summary['active_cell_count_total']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
