import math
import os

from step25_common import ROOT, STEP25_DESCRIPTORS, load_json, write_csv_rows, write_json, write_log
from src.geometry_intake import run_candidate_quality_check


FIELDS = [
    "candidate_id",
    "geometry_type",
    "quality_kind",
    "quality_pass",
    "quality_severity",
    "quality_warnings_count",
    "quality_reasons_count",
    "quality_report_path",
    "occupied_count",
    "connected_component_count",
    "largest_component_fraction",
    "touches_domain_boundary",
]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step25_voxel_candidate_quality"
    rows = []
    for path in STEP25_DESCRIPTORS:
        descriptor = load_json(path)
        if descriptor["geometry_type"] == "voxel":
            row = run_candidate_quality_check(path, out_dir / descriptor["candidate_id"])
            _assert_voxel_row(row)
            rows.append(row)
    if not rows:
        raise RuntimeError("no Step 25 voxel candidate quality rows")

    write_csv_rows(out_dir / "voxel_candidate_quality.csv", rows, FIELDS)
    write_json(out_dir / "voxel_candidate_quality.json", {"row_count": len(rows), "rows": rows})
    marker = "[OK] Step 25 voxel candidate quality finished"
    write_log("logs/step25_voxel_candidate_quality.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _assert_voxel_row(row):
    if row["occupied_count"] <= 0:
        raise RuntimeError(f"voxel quality row has no occupied cells: {row}")
    if row["connected_component_count"] < 1:
        raise RuntimeError(f"voxel quality row has no connected components: {row}")
    if not math.isfinite(float(row["largest_component_fraction"])):
        raise RuntimeError(f"largest_component_fraction is not finite: {row}")
    if row["quality_pass"] is not True or row["quality_severity"] != "ok":
        raise RuntimeError(f"voxel strict quality gate failed: {row}")


if __name__ == "__main__":
    main()
