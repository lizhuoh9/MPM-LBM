import os
from pathlib import Path

from step46_common import ROOT, check_row, read_json, write_csv_rows, write_json, write_log


REGRESSION_FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows, summary = build_regression_guard()
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 46 Step 45 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step46_step45_regression_guard"
    write_csv_rows(out_dir / "step45_regression_guard.csv", rows, REGRESSION_FIELDS)
    write_json(out_dir / "step45_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 46 Step 45 regression guard finished"
    write_log("logs/step46_step45_regression_guard.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def build_regression_guard():
    rows = []
    report_path = "STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md"
    rows.append(check_row("step45_report_exists", (ROOT / report_path).is_file(), report_path, "Step 45 accepted report remains present"))
    runtime_payload = _read_if_exists("outputs/step45_runtime_projection_integration/runtime_projection_integration.json")
    runtime_summary = runtime_payload.get("summary", {})
    rows.append(check_row("step45_runtime_projection_row_count", int(runtime_summary.get("row_count", 0)) == 10, runtime_summary.get("row_count", 0), "Step 45 10-row runtime projection matrix remains available"))
    rows.append(check_row("step45_runtime_projection_pass_count", int(runtime_summary.get("projection_pass_count", 0)) == 10, runtime_summary.get("projection_pass_count", 0), "Step 45 runtime projection rows remain passing"))
    state_payload = _read_if_exists("outputs/step45_runtime_projection_state_guard/runtime_projection_state_guard.json")
    rows.append(check_row("step45_runtime_projection_state_guard_pass", state_payload.get("summary", {}).get("guard_pass") is True, state_payload.get("summary", {}).get("guard_pass"), "Step 45 state guard remains green"))
    manifest = _read_if_exists("outputs/step45_artifact_manifest/artifact_summary.json")
    rows.append(check_row("step45_artifact_large_file_count", int(manifest.get("large_file_count", 1)) == 0, manifest.get("large_file_count"), "Step 45 artifacts remain below large-file threshold"))
    rows.append(check_row("step45_vtr_count", int(manifest.get("step45_vtr_count", 1)) == 0, manifest.get("step45_vtr_count"), "Step 45 still has no VTR artifacts"))
    rows.append(check_row("step45_particle_npy_count", int(manifest.get("step45_particle_npy_count", 1)) == 0, manifest.get("step45_particle_npy_count"), "Step 45 still has no particle npy artifacts"))
    rows.append(check_row("step45_geo_all_fluid_dat_count_added", int(manifest.get("geo_all_fluid_dat_count_added", 1)) == 0, manifest.get("geo_all_fluid_dat_count_added"), "Step 45 still has no geo_all_fluid dat additions"))
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
