import os

from step32_common import ROOT, load_schedule_config, make_schedule_rows, write_log
from src.squid_kinematics_schedule import summarize_schedule, write_schedule_outputs


def main():
    os.chdir(ROOT)
    config = load_schedule_config()
    rows = make_schedule_rows()
    summary = summarize_schedule(rows)
    assert_schedule_summary(summary, config)

    out_dir = ROOT / "outputs" / "step32_kinematics_schedule"
    write_schedule_outputs(rows, out_dir / "kinematics_schedule.csv", out_dir / "kinematics_schedule.json", summary=summary)
    marker = "[OK] Step 32 generate kinematics schedule finished"
    write_log(
        "logs/step32_generate_kinematics_schedule.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"phase_min={summary['phase_min']}",
            f"phase_max={summary['phase_max']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


def assert_schedule_summary(summary, config):
    if int(summary["row_count"]) != int(config.sample_count):
        raise RuntimeError(f"Step 32 schedule row count mismatch: {summary}")
    if float(summary["phase_min"]) != 0.0 or float(summary["phase_max"]) != 1.0:
        raise RuntimeError(f"Step 32 phase range is wrong: {summary}")
    if not bool(summary["finite_pass"]) or not bool(summary["endpoint_repeatability_pass"]):
        raise RuntimeError(f"Step 32 schedule finite/repeatability checks failed: {summary}")
    if int(summary["driver_integration_enabled_count"]) != 0 or int(summary["actuation_enabled_count"]) != 0:
        raise RuntimeError(f"Step 32 schedule must keep driver integration and actuation disabled: {summary}")
    if float(summary["mantle_radius_scale_min_observed"]) < config.mantle_radius_scale_min:
        raise RuntimeError(f"Step 32 mantle radius min out of range: {summary}")
    if float(summary["cavity_volume_scale_min_observed"]) < config.cavity_volume_scale_min:
        raise RuntimeError(f"Step 32 cavity volume min out of range: {summary}")
    if float(summary["funnel_aperture_scale_max_observed"]) > config.funnel_aperture_scale_max:
        raise RuntimeError(f"Step 32 funnel aperture max out of range: {summary}")


if __name__ == "__main__":
    main()
