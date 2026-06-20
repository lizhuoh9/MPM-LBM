import os

from step29_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step28_report_exists", "STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md"),
        check_step28_driver_summary(),
        check_step28_comparison(),
        check_step28_quality(),
        check_step28_artifact_summary("large_file_count", 0),
        check_step28_artifact_summary("raw_candidate_large_file_count", 0),
        check_step28_artifact_summary("scan_data_file_count", 0),
        check_step28_artifact_summary("private_absolute_path_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 28 regression guard failed: {failed}")

    out_dir = ROOT / "outputs" / "step29_step28_regression_guard"
    step28_summary = load_json("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json")["summary"]
    comparison_summary = load_json("outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json")["summary"]
    quality_summary = load_json("outputs/step28_quality_report_aggregation/quality_report_summary.json")["summary"]
    artifact_summary = load_json("outputs/step28_artifact_manifest/artifact_summary.json")
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step28_driver_row_count": step28_summary["driver_row_count"],
        "step28_stable_count": step28_summary["stable_count"],
        "step28_quality_report_count": step28_summary["quality_report_count"],
        "step28_quality_pass_count": quality_summary["pass_count"],
        "step28_comparison_pass_count": comparison_summary["pass_count"],
        "step28_large_file_count": artifact_summary["large_file_count"],
    }
    write_csv_rows(out_dir / "step28_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step28_regression_guard.json", summary)
    marker = "[OK] Step 29 Step 28 regression guard finished"
    write_log("logs/step29_step28_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 28 artifact"}


def check_step28_driver_summary():
    summary = load_json("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json")["summary"]
    passed = (
        int(summary.get("driver_row_count", 0)) == 4
        and int(summary.get("stable_count", 0)) == 4
        and int(summary.get("quality_report_count", 0)) == 4
    )
    return {"check": "step28_transfer_pair_driver", "pass": passed, "value": summary.get("driver_row_count", 0), "notes": "expected 4 stable rows"}


def check_step28_comparison():
    summary = load_json("outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json")["summary"]
    passed = int(summary.get("row_count", 0)) == 2 and int(summary.get("pass_count", 0)) == 2
    return {"check": "step28_engineering_vs_link_area", "pass": passed, "value": summary.get("pass_count", 0), "notes": "expected 2 passing comparisons"}


def check_step28_quality():
    summary = load_json("outputs/step28_quality_report_aggregation/quality_report_summary.json")["summary"]
    passed = int(summary.get("quality_report_count", 0)) == 4 and int(summary.get("pass_count", 0)) == 4
    return {"check": "step28_quality_report_aggregation", "pass": passed, "value": summary.get("quality_report_count", 0), "notes": "expected 4 passing reports"}


def check_step28_artifact_summary(key, expected):
    summary = load_json("outputs/step28_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step28_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
