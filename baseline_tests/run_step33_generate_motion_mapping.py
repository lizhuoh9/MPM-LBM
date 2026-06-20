import os

from step33_common import ROOT, load_motion_inputs, write_log
from src.squid_motion_mapping import compute_region_motion_rows, summarize_motion_rows, write_motion_rows


def main():
    os.chdir(ROOT)
    inputs = load_motion_inputs()
    rows = compute_region_motion_rows(
        inputs["mapping_config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["region_config"],
        inputs["points"],
        inputs["masks"],
    )
    summary = summarize_motion_rows(rows)
    assert_motion_summary(summary)

    out_dir = ROOT / "outputs" / "step33_motion_mapping"
    write_motion_rows(rows, out_dir / "motion_mapping.csv", out_dir / "motion_mapping.json", summary=summary)
    marker = "[OK] Step 33 generate motion mapping finished"
    write_log(
        "logs/step33_generate_motion_mapping.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"schedule_sample_count={summary['schedule_sample_count']}",
            f"tracked_region_count={summary['tracked_region_count']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


def assert_motion_summary(summary):
    if int(summary["row_count"]) != 243:
        raise RuntimeError(f"Step 33 motion row count mismatch: {summary}")
    if int(summary["schedule_sample_count"]) != 81 or int(summary["tracked_region_count"]) != 3:
        raise RuntimeError(f"Step 33 motion dimensions are wrong: {summary}")
    if not bool(summary["finite_pass"]) or not bool(summary["bounds_pass"]):
        raise RuntimeError(f"Step 33 motion finite/bounds checks failed: {summary}")
    if int(summary["mantle_outer_nonzero_velocity_row_count"]) <= 0:
        raise RuntimeError(f"Step 33 mantle velocity proxy is empty: {summary}")
    if int(summary["cavity_volume_rate_nonzero_row_count"]) <= 0:
        raise RuntimeError(f"Step 33 cavity volume-rate proxy is empty: {summary}")
    if int(summary["funnel_aperture_rate_nonzero_row_count"]) <= 0:
        raise RuntimeError(f"Step 33 funnel aperture-rate proxy is empty: {summary}")
    if (
        int(summary["driver_integration_enabled_count"]) != 0
        or int(summary["lbm_wall_velocity_enabled_count"]) != 0
        or int(summary["jet_model_enabled_count"]) != 0
        or int(summary["actuation_enabled_count"]) != 0
    ):
        raise RuntimeError(f"Step 33 motion mapping must not enable execution flags: {summary}")


if __name__ == "__main__":
    main()
