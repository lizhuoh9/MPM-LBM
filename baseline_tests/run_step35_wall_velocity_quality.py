import os

from step35_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.wall_velocity_config import WallVelocityFieldConfig
from src.wall_velocity_field import generate_wall_velocity_field_rows
from src.wall_velocity_quality import analyze_wall_velocity_quality


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = WallVelocityFieldConfig.from_json("configs/step35_squid_proxy_wall_velocity_field.json")
    rows = generate_wall_velocity_field_rows("configs/step35_squid_proxy_wall_velocity_field.json")
    summary = analyze_wall_velocity_quality(rows, config)
    if not bool(summary["quality_pass"]):
        raise RuntimeError(f"Step 35 wall velocity quality failed: {summary}")

    out_dir = ROOT / "outputs" / "step35_wall_velocity_quality"
    write_csv_rows(out_dir / "wall_velocity_quality.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "wall_velocity_quality.json", {"summary": summary})
    marker = "[OK] Step 35 wall velocity quality finished"
    write_log(
        "logs/step35_wall_velocity_quality.log",
        [
            marker,
            f"quality_pass={summary['quality_pass']}",
            f"row_count={summary['row_count']}",
            f"max_velocity_norm={summary['max_velocity_norm']:.12g}",
        ],
    )
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
