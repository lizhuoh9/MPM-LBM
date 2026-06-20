import os

from step34_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step33_report_exists", "STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md"),
        check_step33_motion_mapping(),
        check_step33_motion_quality(),
        check_step33_motion_repeatability(),
        check_step33_schedule_motion_consistency(),
        check_step33_artifact_summary("large_file_count", 0),
        check_step33_artifact_summary("step33_vtr_count", 0),
        check_step33_artifact_summary("step33_particle_npy_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 33 regression guard failed: {failed}")

    motion = load_json("outputs/step33_motion_mapping/motion_mapping.json")["summary"]
    quality = load_json("outputs/step33_motion_quality/motion_quality.json")["summary"]
    repeatability = load_json("outputs/step33_motion_repeatability/motion_repeatability.json")["summary"]
    consistency = load_json("outputs/step33_schedule_motion_consistency/schedule_motion_consistency.json")["summary"]
    artifact = load_json("outputs/step33_artifact_manifest/artifact_summary.json")
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step33_motion_row_count": motion["row_count"],
        "step33_motion_quality_pass": quality["quality_pass"],
        "step33_repeatability_pass": repeatability["repeatability_pass"],
        "step33_consistency_pass": consistency["consistency_pass"],
        "step33_large_file_count": artifact["large_file_count"],
        "step33_vtr_count": artifact["step33_vtr_count"],
        "step33_particle_npy_count": artifact["step33_particle_npy_count"],
    }
    out_dir = ROOT / "outputs" / "step34_step33_regression_guard"
    write_csv_rows(out_dir / "step33_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step33_regression_guard.json", summary)
    marker = "[OK] Step 34 Step 33 regression guard finished"
    write_log("logs/step34_step33_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 33 artifact"}


def check_step33_motion_mapping():
    summary = load_json("outputs/step33_motion_mapping/motion_mapping.json")["summary"]
    value = int(summary.get("row_count", 0))
    return {"check": "step33_motion_row_count", "pass": value == 243, "value": value, "notes": "expected 243 motion rows"}


def check_step33_motion_quality():
    summary = load_json("outputs/step33_motion_quality/motion_quality.json")["summary"]
    return {"check": "step33_motion_quality_pass", "pass": bool(summary.get("quality_pass", False)), "value": summary.get("quality_pass", False), "notes": "Step 33 quality must pass"}


def check_step33_motion_repeatability():
    summary = load_json("outputs/step33_motion_repeatability/motion_repeatability.json")["summary"]
    return {"check": "step33_repeatability_pass", "pass": bool(summary.get("repeatability_pass", False)), "value": summary.get("repeatability_pass", False), "notes": "Step 33 repeatability must pass"}


def check_step33_schedule_motion_consistency():
    summary = load_json("outputs/step33_schedule_motion_consistency/schedule_motion_consistency.json")["summary"]
    return {"check": "step33_consistency_pass", "pass": bool(summary.get("consistency_pass", False)), "value": summary.get("consistency_pass", False), "notes": "Step 33 schedule-motion consistency must pass"}


def check_step33_artifact_summary(key, expected):
    summary = load_json("outputs/step33_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step33_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
