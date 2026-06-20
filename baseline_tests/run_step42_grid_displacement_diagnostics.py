import os

from step42_common import ROOT, load_displacement_inputs, write_csv_rows, write_json, write_log
from src.geometry_displacement_field import compute_geometry_displacement_rows
from src.geometry_displacement_grid_diagnostics import GRID_FIELDS, assert_grid_displacement_diagnostics, summarize_displacement_on_grids, summarize_grid_displacement_rows


def main():
    os.chdir(ROOT)
    inputs = load_displacement_inputs()
    displacement_rows = compute_geometry_displacement_rows(
        inputs["config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["points"],
        inputs["masks"],
    )
    rows = summarize_displacement_on_grids(
        inputs["points"],
        inputs["masks"],
        inputs["schedule_rows"],
        displacement_rows,
        inputs["geometry_config"],
        inputs["config"].grid_sizes,
    )
    summary = summarize_grid_displacement_rows(rows)
    assert_grid_displacement_diagnostics(summary)

    out_dir = ROOT / "outputs" / "step42_grid_displacement_diagnostics"
    write_csv_rows(out_dir / "grid_displacement_diagnostics.csv", rows, GRID_FIELDS)
    write_json(out_dir / "grid_displacement_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 42 grid displacement diagnostics finished"
    write_log("logs/step42_grid_displacement_diagnostics.log", [marker, f"row_count={summary['row_count']}", f"min_active_cell_count={summary['min_active_cell_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
