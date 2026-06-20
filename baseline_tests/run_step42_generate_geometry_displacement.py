import os

from step42_common import ROOT, load_displacement_inputs, write_log
from src.geometry_displacement_field import assert_geometry_displacement_summary, compute_geometry_displacement_rows, summarize_geometry_displacement_rows, write_geometry_displacement_rows


def main():
    os.chdir(ROOT)
    inputs = load_displacement_inputs()
    rows = compute_geometry_displacement_rows(
        inputs["config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["points"],
        inputs["masks"],
    )
    summary = summarize_geometry_displacement_rows(rows, inputs["config"])
    assert_geometry_displacement_summary(summary)

    out_dir = ROOT / "outputs" / "step42_geometry_displacement"
    write_geometry_displacement_rows(
        rows,
        out_dir / "geometry_displacement.csv",
        out_dir / "geometry_displacement.json",
        out_dir / "geometry_displacement_summary.npz",
        summary=summary,
    )
    marker = "[OK] Step 42 generate geometry displacement finished"
    write_log(
        "logs/step42_generate_geometry_displacement.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"phase_sample_count={summary['phase_sample_count']}",
            f"tracked_region_count={summary['tracked_region_count']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
