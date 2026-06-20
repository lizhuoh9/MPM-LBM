import os

from step33_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step32_report_exists", "STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md"),
        check_step32_schedule(),
        check_step32_quality(),
        check_step32_repeatability(),
        check_step32_region_mapping(),
        check_step32_artifact_summary("large_file_count", 0),
        check_step32_artifact_summary("step32_vtr_count", 0),
        check_step32_artifact_summary("step32_particle_npy_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 32 regression guard failed: {failed}")

    schedule = load_json("outputs/step32_kinematics_schedule/kinematics_schedule.json")["summary"]
    quality = load_json("outputs/step32_schedule_quality/schedule_quality.json")["summary"]
    repeatability = load_json("outputs/step32_schedule_repeatability/schedule_repeatability.json")["summary"]
    mapping = load_json("outputs/step32_region_mapping_validation/region_mapping_validation.json")["summary"]
    artifact = load_json("outputs/step32_artifact_manifest/artifact_summary.json")
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step32_schedule_row_count": schedule["row_count"],
        "step32_quality_pass": quality["quality_pass"],
        "step32_repeatability_pass": repeatability["repeatability_pass"],
        "step32_region_mapping_pass": mapping["mapping_pass"],
        "step32_large_file_count": artifact["large_file_count"],
        "step32_vtr_count": artifact["step32_vtr_count"],
        "step32_particle_npy_count": artifact["step32_particle_npy_count"],
    }
    out_dir = ROOT / "outputs" / "step33_step32_regression_guard"
    write_csv_rows(out_dir / "step32_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step32_regression_guard.json", summary)
    marker = "[OK] Step 33 Step 32 regression guard finished"
    write_log("logs/step33_step32_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 32 artifact"}


def check_step32_schedule():
    summary = load_json("outputs/step32_kinematics_schedule/kinematics_schedule.json")["summary"]
    value = int(summary.get("row_count", 0))
    return {"check": "step32_schedule_row_count", "pass": value == 81, "value": value, "notes": "expected 81 schedule rows"}


def check_step32_quality():
    summary = load_json("outputs/step32_schedule_quality/schedule_quality.json")["summary"]
    return {"check": "step32_quality_pass", "pass": bool(summary.get("quality_pass", False)), "value": summary.get("quality_pass", False), "notes": "Step 32 quality must pass"}


def check_step32_repeatability():
    summary = load_json("outputs/step32_schedule_repeatability/schedule_repeatability.json")["summary"]
    return {"check": "step32_repeatability_pass", "pass": bool(summary.get("repeatability_pass", False)), "value": summary.get("repeatability_pass", False), "notes": "Step 32 repeatability must pass"}


def check_step32_region_mapping():
    summary = load_json("outputs/step32_region_mapping_validation/region_mapping_validation.json")["summary"]
    return {"check": "step32_region_mapping_pass", "pass": bool(summary.get("mapping_pass", False)), "value": summary.get("mapping_pass", False), "notes": "Step 32 region mapping must pass"}


def check_step32_artifact_summary(key, expected):
    summary = load_json("outputs/step32_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step32_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
