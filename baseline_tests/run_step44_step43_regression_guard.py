import os

from step44_common import ROOT, check_row, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    rows = build_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
    }
    summary["regression_pass"] = bool(summary["row_count"] >= 6 and summary["pass_count"] == summary["row_count"])
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 44 Step 43 regression guard failed: {rows}")
    out_dir = ROOT / "outputs" / "step44_step43_regression_guard"
    write_csv_rows(out_dir / "step43_regression_guard.csv", rows)
    write_json(out_dir / "step43_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 44 Step 43 regression guard finished"
    write_log("logs/step44_step43_regression_guard.log", [marker, f"row_count={summary['row_count']}", f"regression_pass={summary['regression_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def build_rows():
    config_validation = read_json("outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.json")["summary"]
    mutation_guard = read_json("outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.json")["summary"]
    artifact_summary = read_json("outputs/step43_artifact_manifest/artifact_summary.json")
    return [
        check_row("step43_report_exists", (ROOT / "STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_REPORT.md").is_file(), "STEP43 report", "Step 43 report must exist"),
        check_row("step43_config_validation_pass", config_validation["validation_pass"] is True, config_validation["validation_pass"], "Step 43 diagnostic config validation must pass"),
        check_row("step43_mutation_guard_pass", mutation_guard["guard_pass"] is True, mutation_guard["guard_pass"], "Step 43 no-mutation guard must pass"),
        check_row("step43_large_file_count_zero", int(artifact_summary["large_file_count"]) == 0, artifact_summary["large_file_count"], "Step 43 artifact manifest must have no large files"),
        check_row("step43_vtr_count_zero", int(artifact_summary["step43_vtr_count"]) == 0, artifact_summary["step43_vtr_count"], "Step 43 must not add VTR outputs"),
        check_row("step43_particle_npy_count_zero", int(artifact_summary["step43_particle_npy_count"]) == 0, artifact_summary["step43_particle_npy_count"], "Step 43 must not add particle NPY outputs"),
        check_row("step43_geometry_motion_noop_pass", mutation_guard["geometry_motion_report_no_op_pass"] is True, mutation_guard["geometry_motion_report_no_op_pass"], "Step 43 geometry-motion report must remain no-op"),
    ]


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
