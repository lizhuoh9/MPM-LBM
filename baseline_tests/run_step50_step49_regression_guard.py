import os

from step50_common import ROOT, check_row, read_json, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 49 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_step49_regression_guard"
    write_csv_rows(out_dir / "step49_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step49_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 Step 49 regression guard finished"
    write_log("logs/step50_step49_regression_guard.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def build_rows():
    report = ROOT / "STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_REPORT.md"
    matrix = read_json("outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.json")["summary"]
    transition = read_json("outputs/step49_early_refill_transition_diagnostics/early_refill_transition_diagnostics.json")["summary"]
    guard = read_json("outputs/step49_state_mutation_guard/state_mutation_guard.json")["summary"]
    manifest = read_json("outputs/step49_artifact_manifest/artifact_summary.json")
    return [
        check_row("step49_report_exists", report.is_file(), str(report), "accepted Step 49 report must remain present"),
        check_row("step49_matrix_row_count", int(matrix["row_count"]) == 4, matrix["row_count"], "Step 49 matrix must still have four rows"),
        check_row("step49_matrix_stable_count", int(matrix["stable_count"]) == 4, matrix["stable_count"], "Step 49 matrix must still be stable"),
        check_row("step49_early_refill_pass", transition["transition_pass"] is True, transition["transition_pass"], "Step 49 early refill diagnostics must remain green"),
        check_row("step49_state_guard_pass", guard["guard_pass"] is True, guard["guard_pass"], "Step 49 state guard must remain green"),
        check_row("step49_large_file_count", int(manifest["large_file_count"]) == 0, manifest["large_file_count"], "Step 49 must still have no large files"),
        check_row("step49_vtr_count", int(manifest["step49_vtr_count"]) == 0, manifest["step49_vtr_count"], "Step 49 must still have no VTR output"),
        check_row("step49_particle_npy_count", int(manifest["step49_particle_npy_count"]) == 0, manifest["step49_particle_npy_count"], "Step 49 must still have no particle NPY output"),
        check_row("step49_geo_all_fluid_dat_count_added", int(manifest["geo_all_fluid_dat_count_added"]) == 0, manifest["geo_all_fluid_dat_count_added"], "Step 49 must still have no geo_all_fluid dat output"),
    ]


if __name__ == "__main__":
    main()
