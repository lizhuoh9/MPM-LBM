import os
from pathlib import Path

from step48_common import ROOT, check_row, read_json, write_csv_rows, write_json, write_log


REGRESSION_FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows, summary = build_regression_guard()
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 48 Step 47 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step48_step47_regression_guard"
    write_csv_rows(out_dir / "step47_regression_guard.csv", rows, REGRESSION_FIELDS)
    write_json(out_dir / "step47_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 48 Step 47 regression guard finished"
    write_log("logs/step48_step47_regression_guard.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def build_regression_guard():
    rows = []
    report_path = "STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md"
    rows.append(check_row("step47_report_exists", (ROOT / report_path).is_file(), report_path, "Step 47 accepted report remains present"))
    matrix = _read_if_exists("outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.json")
    matrix_summary = matrix.get("summary", {})
    matrix_rows = matrix.get("rows", [])
    rows.append(check_row("step47_matrix_row_count", int(matrix_summary.get("row_count", 0)) == 4, matrix_summary.get("row_count", 0), "Step 47 four-row matrix remains available"))
    rows.append(check_row("step47_matrix_stable_count", int(matrix_summary.get("stable_count", 0)) == 4, matrix_summary.get("stable_count", 0), "Step 47 matrix remains stable"))
    rows.append(check_row("step47_matrix_step_count", int(matrix_summary.get("step_count_per_row", 0)) == 5, matrix_summary.get("step_count_per_row", 0), "Step 47 remains a five-step accepted envelope"))
    rows.append(check_row("step47_combined_row_exists", any(row.get("row_name") == "runtime_geometry_plus_wall_velocity_32_5step" for row in matrix_rows), "runtime_geometry_plus_wall_velocity_32_5step", "Step 47 combined row remains available"))
    phase_payload = _read_if_exists("outputs/step47_phase_progression_diagnostics/phase_progression_diagnostics.json")
    rows.append(check_row("step47_phase_progression_pass", phase_payload.get("summary", {}).get("phase_progression_pass") is True, phase_payload.get("summary", {}).get("phase_progression_pass"), "Step 47 phase progression remains green"))
    state_payload = _read_if_exists("outputs/step47_state_mutation_guard/state_mutation_guard.json")
    rows.append(check_row("step47_state_guard_pass", state_payload.get("summary", {}).get("guard_pass") is True, state_payload.get("summary", {}).get("guard_pass"), "Step 47 state guard remains green"))
    manifest = _read_if_exists("outputs/step47_artifact_manifest/artifact_summary.json")
    rows.append(check_row("step47_artifact_large_file_count", int(manifest.get("large_file_count", 1)) == 0, manifest.get("large_file_count"), "Step 47 artifacts remain below large-file threshold"))
    rows.append(check_row("step47_vtr_count", int(manifest.get("step47_vtr_count", 1)) == 0, manifest.get("step47_vtr_count"), "Step 47 still has no VTR artifacts"))
    rows.append(check_row("step47_particle_npy_count", int(manifest.get("step47_particle_npy_count", 1)) == 0, manifest.get("step47_particle_npy_count"), "Step 47 still has no particle npy artifacts"))
    rows.append(check_row("step47_geo_all_fluid_dat_count_added", int(manifest.get("geo_all_fluid_dat_count_added", 1)) == 0, manifest.get("geo_all_fluid_dat_count_added"), "Step 47 still has no geo_all_fluid dat additions"))
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
    }
    summary["regression_pass"] = summary["row_count"] == summary["pass_count"]
    return rows, summary


def _read_if_exists(path: str):
    full = ROOT / Path(path)
    if not full.is_file():
        return {}
    return read_json(path)


if __name__ == "__main__":
    main()
