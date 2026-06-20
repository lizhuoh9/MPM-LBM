import os

from step30_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step29_report_exists", "STEP29_CONTROLLED_REAL_GEOMETRY_64_STABILITY_ENVELOPE_REPORT.md"),
        check_step29_driver_summary(),
        check_step29_quality(),
        check_step29_artifact_summary("large_file_count", 0),
        check_step29_artifact_summary("raw_candidate_large_file_count", 0),
        check_step29_artifact_summary("scan_data_file_count", 0),
        check_step29_artifact_summary("private_absolute_path_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 29 regression guard failed: {failed}")

    driver_summary = load_json("outputs/step29_64_stability_driver/stability_driver_results.json")["summary"]
    quality_summary = load_json("outputs/step29_quality_report_aggregation/quality_report_summary.json")["summary"]
    artifact_summary = load_json("outputs/step29_artifact_manifest/artifact_summary.json")
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step29_driver_row_count": driver_summary["driver_row_count"],
        "step29_stable_count": driver_summary["stable_count"],
        "step29_quality_report_count": driver_summary["quality_report_count"],
        "step29_quality_pass_count": quality_summary["pass_count"],
        "step29_large_file_count": artifact_summary["large_file_count"],
        "step29_raw_candidate_large_file_count": artifact_summary["raw_candidate_large_file_count"],
        "step29_scan_data_file_count": artifact_summary["scan_data_file_count"],
    }
    out_dir = ROOT / "outputs" / "step30_step29_regression_guard"
    write_csv_rows(out_dir / "step29_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step29_regression_guard.json", summary)
    marker = "[OK] Step 30 Step 29 regression guard finished"
    write_log("logs/step30_step29_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 29 artifact"}


def check_step29_driver_summary():
    summary = load_json("outputs/step29_64_stability_driver/stability_driver_results.json")["summary"]
    passed = (
        int(summary.get("driver_row_count", 0)) == 4
        and int(summary.get("stable_count", 0)) == 4
        and int(summary.get("quality_report_count", 0)) == 4
    )
    return {"check": "step29_stability_driver", "pass": passed, "value": summary.get("driver_row_count", 0), "notes": "expected 4 stable rows"}


def check_step29_quality():
    summary = load_json("outputs/step29_quality_report_aggregation/quality_report_summary.json")["summary"]
    passed = int(summary.get("quality_report_count", 0)) == 4 and int(summary.get("pass_count", 0)) == 4
    return {"check": "step29_quality_report_aggregation", "pass": passed, "value": summary.get("quality_report_count", 0), "notes": "expected 4 passing reports"}


def check_step29_artifact_summary(key, expected):
    summary = load_json("outputs/step29_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step29_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
