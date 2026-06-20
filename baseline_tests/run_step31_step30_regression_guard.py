import os

from step31_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        check_file("step30_report_exists", "STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md"),
        check_region_schema(),
        check_region_mask_sampling(),
        check_region_projection(),
        check_step30_artifact_summary("large_file_count", 0),
        check_step30_artifact_summary("step30_vtr_count", 0),
        check_step30_artifact_summary("step30_particle_npy_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 30 regression guard failed: {failed}")

    schema = load_json("outputs/step30_region_schema_validation/region_schema_validation.json")["summary"]
    masks = load_json("outputs/step30_region_mask_sampling/region_mask_summary.json")["summary"]
    projection = load_json("outputs/step30_region_projection_smoke/region_projection_results.json")["summary"]
    artifact_summary = load_json("outputs/step30_artifact_manifest/artifact_summary.json")
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step30_required_region_count": schema["required_region_count"],
        "step30_sampling_hash_repeatable": masks["sampled_position_hash_repeatable"] and masks["region_assignment_hash_repeatable"],
        "step30_projection_pass": projection["projection_pass"],
        "step30_large_file_count": artifact_summary["large_file_count"],
        "step30_vtr_count": artifact_summary["step30_vtr_count"],
        "step30_particle_npy_count": artifact_summary["step30_particle_npy_count"],
    }
    out_dir = ROOT / "outputs" / "step31_step30_regression_guard"
    write_csv_rows(out_dir / "step30_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step30_regression_guard.json", summary)
    marker = "[OK] Step 31 Step 30 regression guard finished"
    write_log("logs/step31_step30_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 30 artifact"}


def check_region_schema():
    summary = load_json("outputs/step30_region_schema_validation/region_schema_validation.json")["summary"]
    passed = int(summary.get("required_region_count", 0)) == 7 and bool(summary.get("schema_pass", False))
    return {"check": "step30_region_schema", "pass": passed, "value": summary.get("required_region_count", 0), "notes": "expected seven regions"}


def check_region_mask_sampling():
    summary = load_json("outputs/step30_region_mask_sampling/region_mask_summary.json")["summary"]
    passed = bool(summary.get("sampled_position_hash_repeatable", False)) and bool(summary.get("region_assignment_hash_repeatable", False))
    return {"check": "step30_region_mask_sampling", "pass": passed, "value": summary.get("sample_count", 0), "notes": "expected repeatable hashes"}


def check_region_projection():
    summary = load_json("outputs/step30_region_projection_smoke/region_projection_results.json")["summary"]
    passed = bool(summary.get("projection_pass", False)) and int(summary.get("pass_count", 0)) == 14
    return {"check": "step30_region_projection_smoke", "pass": passed, "value": summary.get("pass_count", 0), "notes": "expected Step 30 32/48 projection pass"}


def check_step30_artifact_summary(key, expected):
    summary = load_json("outputs/step30_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step30_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def load_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
