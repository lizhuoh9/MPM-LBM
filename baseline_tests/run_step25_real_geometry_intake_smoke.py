import os

from step25_common import ROOT, STEP25_DESCRIPTORS, write_csv_rows, write_json, write_log
from src.geometry_intake import run_candidate_intake


FIELDS = [
    "candidate_id",
    "geometry_type",
    "manifest_pass",
    "quality_pass",
    "quality_severity",
    "normalization_pass",
    "source_file",
    "normalization_report_path",
    "quality_report_path",
    "scope_note",
]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step25_real_geometry_intake_smoke"
    rows = [run_candidate_intake(path, out_dir) for path in STEP25_DESCRIPTORS]
    if not any(row["geometry_type"] == "mesh" and row["quality_pass"] for row in rows):
        raise RuntimeError("Step 25 intake smoke requires a passing mesh candidate")
    if not any(row["geometry_type"] == "voxel" and row["quality_pass"] for row in rows):
        raise RuntimeError("Step 25 intake smoke requires a passing voxel candidate")
    if any("real squid validation" not in row["scope_note"] for row in rows):
        raise RuntimeError(f"missing no-claim scope note: {rows}")

    write_csv_rows(out_dir / "intake_smoke_summary.csv", rows, FIELDS)
    write_json(out_dir / "intake_smoke_summary.json", {"row_count": len(rows), "rows": rows})
    marker = "[OK] Step 25 real geometry intake smoke finished"
    write_log(
        "logs/step25_real_geometry_intake_smoke.log",
        [
            marker,
            f"row_count={len(rows)}",
            "scope=descriptor_fingerprint_load_qa_normalization_manifest_only",
        ],
    )
    print(f"row_count={len(rows)}")
    print(marker)


if __name__ == "__main__":
    main()
