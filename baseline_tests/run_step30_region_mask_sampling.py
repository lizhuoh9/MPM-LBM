import os

from step30_common import ROOT, SAMPLE_COUNT, make_step30_region_sample, write_json, write_log
from src.squid_proxy_regions import (
    region_assignment_hash,
    sample_squid_proxy_region_points,
    sample_squid_proxy_regions,
    sampled_position_hash,
    summarize_region_masks,
    write_region_manifest,
)
from src.squid_region_config import REQUIRED_REGION_IDS


def main():
    os.chdir(ROOT)
    geometry_config, region_config, points, masks, rows = make_step30_region_sample()
    repeat_points = sample_squid_proxy_region_points(geometry_config, count=SAMPLE_COUNT, seed=30)
    repeat_masks = sample_squid_proxy_regions(geometry_config, region_config, repeat_points)
    repeat_rows = summarize_region_masks(repeat_points, repeat_masks, geometry_config, region_config)
    counts = {row["region_id"]: int(row["point_count"]) for row in rows}
    repeat_counts = {row["region_id"]: int(row["point_count"]) for row in repeat_rows}
    position_hash = sampled_position_hash(points)
    repeat_position_hash = sampled_position_hash(repeat_points)
    assignment_hash = region_assignment_hash(masks)
    repeat_assignment_hash = region_assignment_hash(repeat_masks)
    summary = {
        "row_count": len(rows),
        "required_region_count": len(REQUIRED_REGION_IDS),
        "sample_count": len(points),
        "mantle_outer_count": counts["mantle_outer"],
        "mantle_cavity_proxy_count": counts["mantle_cavity_proxy"],
        "funnel_outlet_proxy_count": counts["funnel_outlet_proxy"],
        "head_proxy_count": counts["head_proxy"],
        "arms_proxy_count": counts["arms_proxy"],
        "left_fin_proxy_count": counts["left_fin_proxy"],
        "right_fin_proxy_count": counts["right_fin_proxy"],
        "all_masks_boolean": all(row["mask_is_boolean"] for row in rows),
        "deterministic_counts_pass": counts == repeat_counts,
        "sampled_position_hash": position_hash,
        "sampled_position_hash_repeat": repeat_position_hash,
        "sampled_position_hash_repeatable": position_hash == repeat_position_hash,
        "region_assignment_hash": assignment_hash,
        "region_assignment_hash_repeat": repeat_assignment_hash,
        "region_assignment_hash_repeatable": assignment_hash == repeat_assignment_hash,
    }
    summary["sampling_pass"] = (
        summary["row_count"] >= len(REQUIRED_REGION_IDS)
        and all(summary[f"{region_id}_count"] > 0 for region_id in REQUIRED_REGION_IDS)
        and summary["all_masks_boolean"]
        and summary["deterministic_counts_pass"]
        and summary["sampled_position_hash_repeatable"]
        and summary["region_assignment_hash_repeatable"]
    )
    if not summary["sampling_pass"]:
        raise RuntimeError(f"Step 30 region mask sampling failed: {summary}")

    out_dir = ROOT / "outputs" / "step30_region_mask_sampling"
    write_region_manifest(rows, out_dir / "region_mask_summary.csv", out_dir / "region_mask_summary.json", summary)
    write_json(out_dir / "region_mask_summary.json", {"rows": rows, "summary": summary})
    marker = "[OK] Step 30 region mask sampling finished"
    write_log(
        "logs/step30_region_mask_sampling.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"sample_count={summary['sample_count']}",
            f"region_assignment_hash={summary['region_assignment_hash']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
