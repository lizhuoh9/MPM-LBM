import os

from step27_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step26_report_exists", "STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md"),
        check_step26_projection(),
        check_step26_short_driver_summary(),
        check_step26_quality(),
        check_step26_artifact_summary("large_file_count", 0),
        check_step26_artifact_summary("raw_candidate_large_file_count", 0),
        check_step26_artifact_summary("scan_data_file_count", 0),
        check_step26_artifact_summary("private_absolute_path_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 26 regression guard failed: {failed}")

    out_dir = ROOT / "outputs" / "step27_step26_regression_guard"
    step26_summary = load_json("outputs/step26_short_driver_summary/short_driver_summary.json")["summary"]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step26_projection_row_count": load_json("outputs/step26_projection_scale_diagnostics/projection_scale_results.json")["row_count"],
        "step26_driver_row_count": step26_summary["driver_row_count"],
        "step26_stable_count": step26_summary["stable_count"],
        "step26_quality_report_count": step26_summary["quality_report_count"],
        "step26_large_file_count": load_json("outputs/step26_artifact_manifest/artifact_summary.json")["large_file_count"],
    }
    write_csv_rows(out_dir / "step26_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step26_regression_guard.json", summary)
    marker = "[OK] Step 27 Step 26 regression guard finished"
    write_log("logs/step27_step26_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 26 artifact"}


def check_step26_projection():
    payload = load_json("outputs/step26_projection_scale_diagnostics/projection_scale_results.json")
    summary = payload.get("summary", {})
    passed = int(payload.get("row_count", 0)) == 6 and int(summary.get("pass_count", 0)) == 6
    return {"check": "step26_projection_scale_diagnostics", "pass": passed, "value": payload.get("row_count", 0), "notes": "expected 6 passing rows"}


def check_step26_short_driver_summary():
    summary = load_json("outputs/step26_short_driver_summary/short_driver_summary.json")["summary"]
    passed = int(summary.get("driver_row_count", 0)) == 8 and int(summary.get("stable_count", 0)) == 8
    return {"check": "step26_short_driver_summary", "pass": passed, "value": summary.get("driver_row_count", 0), "notes": "expected 8 stable rows"}


def check_step26_quality():
    summary = load_json("outputs/step26_quality_report_aggregation/quality_report_summary.json")["summary"]
    passed = int(summary.get("quality_report_count", 0)) == 8 and int(summary.get("pass_count", 0)) == 8
    return {"check": "step26_quality_report_aggregation", "pass": passed, "value": summary.get("quality_report_count", 0), "notes": "expected 8 passing reports"}


def check_step26_artifact_summary(key, expected):
    summary = load_json("outputs/step26_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step26_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
