import os

from step43_common import ROOT, check_row, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = regression_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "regression_pass": all(row["pass"] for row in rows),
    }
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 43 Step 42 regression guard failed: {rows}")
    out_dir = ROOT / "outputs" / "step43_step42_regression_guard"
    write_csv_rows(out_dir / "step42_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step42_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 43 Step 42 regression guard finished"
    write_log("logs/step43_step42_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = [
        check_file("step42_report_exists", "STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_REPORT.md"),
        check_file("step42_geometry_displacement_exists", "outputs/step42_geometry_displacement/geometry_displacement.json"),
        check_file("step42_quality_exists", "outputs/step42_displacement_quality/displacement_quality.json"),
        check_file("step42_no_driver_guard_exists", "outputs/step42_no_driver_update_guard/no_driver_update_guard.json"),
        check_file("step42_artifact_summary_exists", "outputs/step42_artifact_manifest/artifact_summary.json"),
    ]
    displacement = read_json_file("outputs/step42_geometry_displacement/geometry_displacement.json").get("summary", {})
    quality = read_json_file("outputs/step42_displacement_quality/displacement_quality.json").get("summary", {})
    guard = read_json_file("outputs/step42_no_driver_update_guard/no_driver_update_guard.json").get("summary", {})
    artifact = read_json_file("outputs/step42_artifact_manifest/artifact_summary.json")
    rows.extend(
        [
            check_row("step42_displacement_row_count", int(displacement.get("row_count", 0)) == 243, displacement.get("row_count", None), "Step 42 displacement row count stays 243"),
            check_row("step42_displacement_phase_count", int(displacement.get("phase_sample_count", 0)) == 81, displacement.get("phase_sample_count", None), "Step 42 displacement phase count stays 81"),
            check_row("step42_quality_pass", bool(quality.get("quality_pass", False)), quality.get("quality_pass", None), "Step 42 quality stays passing"),
            check_row("step42_no_driver_guard_pass", bool(guard.get("guard_pass", False)), guard.get("guard_pass", None), "Step 42 no-driver-update guard stays passing"),
            check_row("step42_large_file_count", int(artifact.get("large_file_count", -1)) == 0, artifact.get("large_file_count", None), "Step 42 artifact large-file count stays 0"),
            check_row("step42_vtr_count", int(artifact.get("step42_vtr_count", -1)) == 0, artifact.get("step42_vtr_count", None), "Step 42 wrote no VTR outputs"),
            check_row("step42_particle_npy_count", int(artifact.get("step42_particle_npy_count", -1)) == 0, artifact.get("step42_particle_npy_count", None), "Step 42 wrote no particle NPY outputs"),
        ]
    )
    return rows


def check_file(name, relative_path):
    return check_row(name, (ROOT / relative_path).is_file(), relative_path, "required Step 42 artifact")


def read_json_file(relative_path):
    import json

    path = ROOT / relative_path
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
