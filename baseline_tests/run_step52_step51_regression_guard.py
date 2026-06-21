import os

from step52_common import ROOT, check_row, read_json, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = build_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
    }
    summary["regression_pass"] = summary["row_count"] == summary["pass_count"]
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 51 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_step51_regression_guard"
    write_csv_rows(out_dir / "step51_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step51_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 52 Step 51 regression guard finished"
    write_log("logs/step52_step51_regression_guard.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def build_rows():
    report = ROOT / "STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_REPORT.md"
    report_rel = report.relative_to(ROOT).as_posix()
    matrix = read_json("outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json")["summary"]
    link_area = read_json("outputs/step51_link_area_envelope/link_area_envelope.json")["summary"]
    guard = read_json("outputs/step51_state_mutation_guard/state_mutation_guard.json")["summary"]
    manifest = read_json("outputs/step51_artifact_manifest/artifact_summary.json")
    return [
        check_row("step51_report_exists", report.is_file(), report_rel, "accepted Step 51 report must remain present"),
        check_row("step51_matrix_row_count", int(matrix["row_count"]) == 8, matrix["row_count"], "Step 51 matrix must still have eight rows"),
        check_row("step51_matrix_stable_count", int(matrix["stable_count"]) == 8, matrix["stable_count"], "Step 51 matrix must still be stable"),
        check_row("step51_link_area_envelope_pass", link_area["link_area_envelope_pass"] is True, link_area["link_area_envelope_pass"], "Step 51 link-area envelope must remain green"),
        check_row("step51_state_guard_pass", guard["guard_pass"] is True, guard["guard_pass"], "Step 51 state guard must remain green"),
        check_row("step51_artifact_budget_pass", manifest["artifact_budget_pass"] is True, manifest["artifact_budget_pass"], "Step 51 artifact budget must remain green"),
        check_row("step51_large_file_count", int(manifest["large_file_count"]) == 0, manifest["large_file_count"], "Step 51 must still have no large files"),
        check_row("step51_vtr_count", int(manifest["step51_vtr_count"]) == 0, manifest["step51_vtr_count"], "Step 51 must still have no VTR output"),
        check_row("step51_particle_npy_count", int(manifest["step51_particle_npy_count"]) == 0, manifest["step51_particle_npy_count"], "Step 51 must still have no particle NPY output"),
        check_row("step51_geo_all_fluid_dat_count_added", int(manifest["geo_all_fluid_dat_count_added"]) == 0, manifest["geo_all_fluid_dat_count_added"], "Step 51 must still have no geo_all_fluid dat output"),
    ]


if __name__ == "__main__":
    main()
