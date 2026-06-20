import os

from step40_common import ROOT, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 40 Step 39 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step40_step39_regression_guard"
    write_csv_rows(out_dir / "step39_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step39_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 40 Step 39 regression guard finished"
    write_log("logs/step40_step39_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = []
    rows.append(check("step39_report_exists", (ROOT / "STEP39_CONTROLLED_JET_CYCLE_PROXY_MULTI_CYCLE_STABILITY_ENVELOPE_REPORT.md").is_file(), "STEP39 report", "Step 39 report remains present"))
    driver = read_json("outputs/step39_multicycle_driver/multicycle_driver_results.json")["summary"]
    proxy = read_json("outputs/step39_multicycle_proxy_diagnostics/multicycle_proxy_diagnostics.json")["summary"]
    drift = read_json("outputs/step39_cycle_to_cycle_drift_summary/cycle_to_cycle_drift.json")["summary"]
    wall = read_json("outputs/step39_wall_velocity_multicycle_quality/wall_velocity_multicycle_quality.json")["summary"]
    guard = read_json("outputs/step39_tethered_no_free_body_guard/tethered_no_free_body_guard.json")["summary"]
    artifact = read_json("outputs/step39_artifact_manifest/artifact_summary.json")
    rows.append(check("step39_driver_row_count", int(driver["row_count"]) == 4, driver["row_count"], "Step 39 driver row count stays 4"))
    rows.append(check("step39_driver_stable_count", int(driver["stable_count"]) == 4, driver["stable_count"], "Step 39 driver rows stay stable"))
    rows.append(check("step39_multicycle_proxy", bool(proxy["multicycle_proxy_pass"]), proxy["multicycle_proxy_pass"], "Step 39 multicycle proxy diagnostics stay passing"))
    rows.append(check("step39_drift_summary", bool(drift["drift_summary_pass"]), drift["drift_summary_pass"], "Step 39 cycle-to-cycle drift stays passing"))
    rows.append(check("step39_wall_velocity_quality", bool(wall["quality_pass"]), wall["quality_pass"], "Step 39 wall velocity quality stays passing"))
    rows.append(check("step39_tethered_guard", bool(guard["guard_pass"]), guard["guard_pass"], "Step 39 tethered guard stays passing"))
    rows.append(check("step39_large_file_count", int(artifact["large_file_count"]) == 0, artifact["large_file_count"], "Step 39 artifact large-file count stays 0"))
    rows.append(check("step39_vtr_count", int(artifact["step39_vtr_count"]) == 0, artifact["step39_vtr_count"], "Step 39 wrote no VTR outputs"))
    rows.append(check("step39_particle_npy_count", int(artifact["step39_particle_npy_count"]) == 0, artifact["step39_particle_npy_count"], "Step 39 wrote no particle NPY outputs"))
    return rows


def check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
