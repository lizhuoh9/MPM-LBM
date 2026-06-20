import os

from step33_common import ROOT, load_motion_inputs, write_csv_rows, write_json, write_log
from src.squid_motion_mapping import compute_region_motion_rows
from src.squid_motion_projection_diagnostics import GRID_FIELDS, assert_motion_grid_diagnostics, summarize_motion_grid_rows, summarize_motion_on_grids


def main():
    os.chdir(ROOT)
    inputs = load_motion_inputs()
    motion_rows = compute_region_motion_rows(
        inputs["mapping_config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["region_config"],
        inputs["points"],
        inputs["masks"],
    )
    rows = summarize_motion_on_grids(inputs["points"], inputs["masks"], motion_rows, inputs["mapping_config"].grid_sizes)
    summary = summarize_motion_grid_rows(rows)
    assert_motion_grid_diagnostics(summary)

    out_dir = ROOT / "outputs" / "step33_motion_grid_diagnostics"
    write_csv_rows(out_dir / "motion_grid_diagnostics.csv", rows, GRID_FIELDS)
    write_json(out_dir / "motion_grid_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 33 motion grid diagnostics finished"
    write_log(
        "logs/step33_motion_grid_diagnostics.log",
        [marker, f"row_count={summary['row_count']}", f"min_active_cell_count={summary['min_active_cell_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
