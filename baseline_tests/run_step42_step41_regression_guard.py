import os

from step42_common import ROOT, check_row, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 42 Step 41 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step42_step41_regression_guard"
    write_csv_rows(out_dir / "step41_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step41_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 42 Step 41 regression guard finished"
    write_log("logs/step42_step41_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = [
        check_file("step41_report_exists", "STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_REPORT.md"),
        check_file("step41_driver_results_exists", "outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json"),
        check_file("step41_feasibility_summary_exists", "outputs/step41_64_feasibility_summary/feasibility_summary.json"),
        check_file("step41_wall_velocity_quality_exists", "outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json"),
        check_file("step41_cycle_proxy_exists", "outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json"),
        check_file("step41_tethered_guard_exists", "outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json"),
        check_file("step41_quality_summary_exists", "outputs/step41_quality_report_aggregation/quality_report_summary.json"),
        check_file("step41_artifact_summary_exists", "outputs/step41_artifact_manifest/artifact_summary.json"),
    ]
    driver = read_json_if_exists("outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json", "summary")
    feasibility = read_json_if_exists("outputs/step41_64_feasibility_summary/feasibility_summary.json", "summary")
    wall_quality = read_json_if_exists("outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json", "summary")
    cycle = read_json_if_exists("outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json", "summary")
    tethered = read_json_if_exists("outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json", "summary")
    quality = read_json_if_exists("outputs/step41_quality_report_aggregation/quality_report_summary.json", "summary")
    artifact = read_json_file("outputs/step41_artifact_manifest/artifact_summary.json")
    rows.extend(
        [
            check_row("step41_driver_row_count", int(driver.get("row_count", 0)) == 4, driver.get("row_count", None), "Step 41 driver row count stays 4"),
            check_row("step41_driver_stable_count", int(driver.get("stable_count", 0)) == 4, driver.get("stable_count", None), "Step 41 driver rows stay stable"),
            check_row("step41_feasibility_pass", bool(feasibility.get("feasibility_pass", False)), feasibility.get("feasibility_pass", None), "Step 41 feasibility summary stays passing"),
            check_row("step41_wall_velocity_quality_pass", bool(wall_quality.get("quality_pass", False)), wall_quality.get("quality_pass", None), "Step 41 wall velocity quality stays passing"),
            check_row("step41_cycle_proxy_pass", bool(cycle.get("cycle_proxy_64_pass", False)), cycle.get("cycle_proxy_64_pass", None), "Step 41 cycle proxy diagnostics stay passing"),
            check_row("step41_tethered_guard_pass", bool(tethered.get("guard_pass", False)), tethered.get("guard_pass", None), "Step 41 tethered guard stays passing"),
            check_row("step41_quality_reports_pass", int(quality.get("pass_count", 0)) == int(quality.get("quality_report_count", -1)) == 4, quality.get("pass_count", None), "Step 41 strict quality reports stay passing"),
            check_row("step41_large_file_count", int(artifact.get("large_file_count", -1)) == 0, artifact.get("large_file_count", None), "Step 41 artifact large-file count stays 0"),
            check_row("step41_vtr_count", int(artifact.get("step41_vtr_count", -1)) == 0, artifact.get("step41_vtr_count", None), "Step 41 wrote no VTR outputs"),
            check_row("step41_particle_npy_count", int(artifact.get("step41_particle_npy_count", -1)) == 0, artifact.get("step41_particle_npy_count", None), "Step 41 wrote no particle NPY outputs"),
        ]
    )
    return rows


def check_file(name, relative_path):
    return check_row(name, (ROOT / relative_path).is_file(), relative_path, "required Step 41 artifact")


def read_json_if_exists(relative_path, key):
    payload = read_json_file(relative_path)
    return payload.get(key, {}) if isinstance(payload, dict) else {}


def read_json_file(relative_path):
    import json

    path = ROOT / relative_path
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
