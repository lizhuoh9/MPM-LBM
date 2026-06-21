import os

from step45_common import ROOT, check_row, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    rows = build_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
    }
    summary["regression_pass"] = bool(summary["row_count"] >= 7 and summary["pass_count"] == summary["row_count"])
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 45 Step 44 regression guard failed: {rows}")
    out_dir = ROOT / "outputs" / "step45_step44_regression_guard"
    write_csv_rows(out_dir / "step44_regression_guard.csv", rows)
    write_json(out_dir / "step44_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 45 Step 44 regression guard finished"
    write_log("logs/step45_step44_regression_guard.log", [marker, f"row_count={summary['row_count']}", f"regression_pass={summary['regression_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def build_rows():
    runtime_copy = read_json("outputs/step44_runtime_displaced_copy/runtime_displaced_copy.json")["summary"]
    projection = read_json("outputs/step44_projection_only_smoke/projection_only_smoke.json")["summary"]
    mutation_guard = read_json("outputs/step44_state_mutation_guard/state_mutation_guard.json")["summary"]
    artifact_summary = read_json("outputs/step44_artifact_manifest/artifact_summary.json")
    return [
        check_row("step44_report_exists", (ROOT / "STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md").is_file(), "STEP44 report", "Step 44 report must exist"),
        check_row("step44_runtime_copy_row_count", int(runtime_copy["row_count"]) == 15, runtime_copy["row_count"], "Step 44 runtime copy row count must remain 15"),
        check_row("step44_projection_only_row_count", int(projection["row_count"]) == 10, projection["row_count"], "Step 44 projection-only row count must remain 10"),
        check_row("step44_state_mutation_guard_pass", mutation_guard["guard_pass"] is True, mutation_guard["guard_pass"], "Step 44 state mutation guard must pass"),
        check_row("step44_large_file_count_zero", int(artifact_summary["large_file_count"]) == 0, artifact_summary["large_file_count"], "Step 44 artifact manifest must have no large files"),
        check_row("step44_vtr_count_zero", int(artifact_summary["step44_vtr_count"]) == 0, artifact_summary["step44_vtr_count"], "Step 44 must not add VTR outputs"),
        check_row("step44_particle_npy_count_zero", int(artifact_summary["step44_particle_npy_count"]) == 0, artifact_summary["step44_particle_npy_count"], "Step 44 must not add particle NPY outputs"),
        check_row("step44_geo_all_fluid_count_zero", int(artifact_summary["geo_all_fluid_dat_count_added"]) == 0, artifact_summary["geo_all_fluid_dat_count_added"], "Step 44 must not add geo_all_fluid dat artifacts"),
    ]


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
