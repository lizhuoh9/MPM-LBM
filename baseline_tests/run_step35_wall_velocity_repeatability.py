import os

from step35_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.wall_velocity_field import generate_wall_velocity_field_rows, wall_velocity_hashes


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    first = generate_wall_velocity_field_rows("configs/step35_squid_proxy_wall_velocity_field.json")
    second = generate_wall_velocity_field_rows("configs/step35_squid_proxy_wall_velocity_field.json")
    first_hashes = wall_velocity_hashes(first)
    second_hashes = wall_velocity_hashes(second)
    summary = {
        "row_count_first": len(first),
        "row_count_second": len(second),
        "velocity_field_hash_first": first_hashes["velocity_field_hash"],
        "velocity_field_hash_second": second_hashes["velocity_field_hash"],
        "mantle_velocity_hash_first": first_hashes["mantle_velocity_hash"],
        "mantle_velocity_hash_second": second_hashes["mantle_velocity_hash"],
        "cavity_velocity_hash_first": first_hashes["cavity_velocity_hash"],
        "cavity_velocity_hash_second": second_hashes["cavity_velocity_hash"],
        "funnel_velocity_hash_first": first_hashes["funnel_velocity_hash"],
        "funnel_velocity_hash_second": second_hashes["funnel_velocity_hash"],
    }
    summary["repeatability_pass"] = (
        int(summary["row_count_first"]) == 63
        and int(summary["row_count_second"]) == 63
        and summary["velocity_field_hash_first"] == summary["velocity_field_hash_second"]
        and summary["mantle_velocity_hash_first"] == summary["mantle_velocity_hash_second"]
        and summary["cavity_velocity_hash_first"] == summary["cavity_velocity_hash_second"]
        and summary["funnel_velocity_hash_first"] == summary["funnel_velocity_hash_second"]
    )
    if not bool(summary["repeatability_pass"]):
        raise RuntimeError(f"Step 35 repeatability failed: {summary}")

    out_dir = ROOT / "outputs" / "step35_wall_velocity_repeatability"
    write_csv_rows(out_dir / "wall_velocity_repeatability.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "wall_velocity_repeatability.json", {"summary": summary})
    marker = "[OK] Step 35 wall velocity repeatability finished"
    write_log(
        "logs/step35_wall_velocity_repeatability.log",
        [
            marker,
            f"repeatability_pass={summary['repeatability_pass']}",
            f"velocity_field_hash={summary['velocity_field_hash_first']}",
        ],
    )
    print(f"repeatability_pass={summary['repeatability_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
