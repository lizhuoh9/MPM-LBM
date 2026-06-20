import os

from step41_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = regression_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "regression_pass": all(row["pass"] for row in rows),
    }
    if not summary["regression_pass"]:
        raise RuntimeError(f"Step 41 Step 40 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step41_step40_regression_guard"
    write_csv_rows(out_dir / "step40_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step40_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 41 Step 40 regression guard finished"
    write_log("logs/step41_step40_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = []
    rows.append(check("step40_report_exists", (ROOT / "STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_REPORT.md").is_file(), "STEP40 report", "Step 40 report remains present"))
    driver = read_json("outputs/step40_parameter_sweep_driver/parameter_sweep_results.json")["summary"]
    sensitivity = read_json("outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.json")["summary"]
    cap = read_json("outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.json")["summary"]
    guard = read_json("outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.json")["summary"]
    artifact = read_json("outputs/step40_artifact_manifest/artifact_summary.json")
    rows.append(check("step40_driver_row_count", int(driver["row_count"]) == 8, driver["row_count"], "Step 40 driver row count stays 8"))
    rows.append(check("step40_driver_stable_count", int(driver["stable_count"]) == 8, driver["stable_count"], "Step 40 driver rows stay stable"))
    rows.append(check("step40_scale_count", int(driver["scale_count"]) == 3, driver["scale_count"], "Step 40 keeps three parameter scales"))
    rows.append(check("step40_parameter_sensitivity", bool(sensitivity["parameter_sensitivity_pass"]), sensitivity["parameter_sensitivity_pass"], "Step 40 sensitivity summary stays passing"))
    rows.append(check("step40_cap_pass", bool(cap["cap_pass"]), cap["cap_pass"], "Step 40 cap diagnostics stay passing"))
    rows.append(check("step40_tethered_guard", bool(guard["guard_pass"]), guard["guard_pass"], "Step 40 tethered guard stays passing"))
    rows.append(check("step40_large_file_count", int(artifact["large_file_count"]) == 0, artifact["large_file_count"], "Step 40 artifact large-file count stays 0"))
    rows.append(check("step40_vtr_count", int(artifact["step40_vtr_count"]) == 0, artifact["step40_vtr_count"], "Step 40 wrote no VTR outputs"))
    rows.append(check("step40_particle_npy_count", int(artifact["step40_particle_npy_count"]) == 0, artifact["step40_particle_npy_count"], "Step 40 wrote no particle NPY outputs"))
    return rows


def check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
