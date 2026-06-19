import math
import os

from step25_common import ROOT, STEP25_DESCRIPTORS, load_json, relative_path, write_csv_rows, write_json, write_log
from src.geometry_normalization import normalize_mesh_candidate, normalize_voxel_candidate, write_normalization_report


FIELDS = [
    "candidate_id",
    "geometry_type",
    "normalization_report_path",
    "normalized_inside_domain",
    "padding",
    "preserve_aspect_ratio",
    "scale_factor",
    "translation",
    "source_file_modified",
    "repair_performed",
    "remeshing_performed",
]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step25_normalization_reports"
    rows = []
    for path in STEP25_DESCRIPTORS:
        descriptor = load_json(path)
        report = (
            normalize_mesh_candidate(descriptor)
            if descriptor["geometry_type"] == "mesh"
            else normalize_voxel_candidate(descriptor)
        )
        report_path = out_dir / descriptor["candidate_id"] / "normalization_report.json"
        write_normalization_report(report, report_path)
        row = {
            "candidate_id": report["candidate_id"],
            "geometry_type": report["geometry_type"],
            "normalization_report_path": relative_path(report_path),
            "normalized_inside_domain": report["normalized_inside_domain"],
            "padding": report["padding"],
            "preserve_aspect_ratio": report["preserve_aspect_ratio"],
            "scale_factor": report["scale_factor"],
            "translation": report["translation"],
            "source_file_modified": report["source_file_modified"],
            "repair_performed": report["repair_performed"],
            "remeshing_performed": report["remeshing_performed"],
        }
        _assert_normalization_report(report)
        rows.append(row)

    write_csv_rows(out_dir / "normalization_summary.csv", rows, FIELDS)
    write_json(out_dir / "normalization_summary.json", {"row_count": len(rows), "rows": rows})
    marker = "[OK] Step 25 normalization reports finished"
    write_log("logs/step25_normalization_reports.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _assert_normalization_report(report):
    if report["normalized_inside_domain"] is not True:
        raise RuntimeError(f"normalization bounds left the domain: {report}")
    if not math.isfinite(float(report["scale_factor"])):
        raise RuntimeError(f"normalization scale is not finite: {report}")
    if report["source_file_modified"] is not False:
        raise RuntimeError(f"normalization modified source file: {report}")
    if report["repair_performed"] is not False:
        raise RuntimeError(f"normalization performed repair: {report}")
    if report["remeshing_performed"] is not False:
        raise RuntimeError(f"normalization performed remeshing: {report}")
    if not all(math.isfinite(float(value)) for value in report["translation"]):
        raise RuntimeError(f"normalization translation is not finite: {report}")


if __name__ == "__main__":
    main()
