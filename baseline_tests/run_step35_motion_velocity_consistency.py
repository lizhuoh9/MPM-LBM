import os

from step35_common import ROOT, fieldnames_from_rows, load_step35_inputs, write_csv_rows, write_json, write_log
from src.wall_velocity_consistency import compare_wall_velocity_to_motion_mapping
from src.wall_velocity_field import generate_wall_velocity_field_rows


def main():
    os.chdir(ROOT)
    inputs = load_step35_inputs()
    wall_rows = generate_wall_velocity_field_rows("configs/step35_squid_proxy_wall_velocity_field.json")
    payload = compare_wall_velocity_to_motion_mapping(wall_rows, inputs["motion_rows"])
    summary = payload["summary"]
    rows = payload["rows"]
    if not bool(summary["consistency_pass"]):
        raise RuntimeError(f"Step 35 motion-velocity consistency failed: {summary}")

    out_dir = ROOT / "outputs" / "step35_motion_velocity_consistency"
    write_csv_rows(out_dir / "motion_velocity_consistency.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "motion_velocity_consistency.json", payload)
    marker = "[OK] Step 35 motion velocity consistency finished"
    write_log(
        "logs/step35_motion_velocity_consistency.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"pass_count={summary['pass_count']}",
            f"consistency_pass={summary['consistency_pass']}",
        ],
    )
    print(f"consistency_pass={summary['consistency_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
