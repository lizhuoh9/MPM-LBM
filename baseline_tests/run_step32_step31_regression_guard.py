import os

from step32_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step31_report_exists", "STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_REPORT.md"),
        check_step31_projection(),
        check_step31_static_driver(),
        check_step31_quality(),
        check_step31_artifact_summary("large_file_count", 0),
        check_step31_artifact_summary("step31_vtr_count", 0),
        check_step31_artifact_summary("step31_particle_npy_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 31 regression guard failed: {failed}")

    projection = load_json("outputs/step31_region_projection_scale/region_projection_scale.json")["summary"]
    driver = load_json("outputs/step31_static_driver_smoke/static_driver_results.json")["summary"]
    quality = load_json("outputs/step31_quality_report_aggregation/quality_report_summary.json")["summary"]
    artifact = load_json("outputs/step31_artifact_manifest/artifact_summary.json")
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step31_projection_row_count": projection["row_count"],
        "step31_static_driver_row_count": driver["driver_row_count"],
        "step31_static_driver_stable_count": driver["stable_count"],
        "step31_quality_report_count": quality["quality_report_count"],
        "step31_large_file_count": artifact["large_file_count"],
        "step31_vtr_count": artifact["step31_vtr_count"],
        "step31_particle_npy_count": artifact["step31_particle_npy_count"],
    }
    out_dir = ROOT / "outputs" / "step32_step31_regression_guard"
    write_csv_rows(out_dir / "step31_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step31_regression_guard.json", summary)
    marker = "[OK] Step 32 Step 31 regression guard finished"
    write_log("logs/step32_step31_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 31 artifact"}


def check_step31_projection():
    summary = load_json("outputs/step31_region_projection_scale/region_projection_scale.json")["summary"]
    passed = int(summary.get("row_count", 0)) == 21 and bool(summary.get("projection_pass", False))
    return {"check": "step31_region_projection_scale", "pass": passed, "value": summary.get("row_count", 0), "notes": "expected 21 passing projection rows"}


def check_step31_static_driver():
    summary = load_json("outputs/step31_static_driver_smoke/static_driver_results.json")["summary"]
    passed = int(summary.get("driver_row_count", 0)) == 4 and int(summary.get("stable_count", 0)) == 4
    return {"check": "step31_static_driver_smoke", "pass": passed, "value": summary.get("driver_row_count", 0), "notes": "expected four stable static rows"}


def check_step31_quality():
    summary = load_json("outputs/step31_quality_report_aggregation/quality_report_summary.json")["summary"]
    passed = int(summary.get("quality_report_count", 0)) == 4 and int(summary.get("pass_count", 0)) == 4
    return {"check": "step31_quality_report_aggregation", "pass": passed, "value": summary.get("quality_report_count", 0), "notes": "expected four passing strict reports"}


def check_step31_artifact_summary(key, expected):
    summary = load_json("outputs/step31_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step31_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
