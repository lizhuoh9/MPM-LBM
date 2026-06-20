import os

from step39_common import ROOT, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 39 Step 38 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step39_step38_regression_guard"
    write_csv_rows(out_dir / "step38_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step38_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 Step 38 regression guard finished"
    write_log("logs/step39_step38_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = []
    rows.append(check("step38_report_exists", (ROOT / "STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_REPORT.md").is_file(), "STEP38 report", "Step 38 report remains present"))
    driver = read_json("outputs/step38_cycle_driver/cycle_driver_results.json")["summary"]
    proxy = read_json("outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.json")["summary"]
    wall = read_json("outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.json")["summary"]
    guard = read_json("outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.json")["summary"]
    artifact = read_json("outputs/step38_artifact_manifest/artifact_summary.json")
    rows.append(check("step38_driver_row_count", int(driver["row_count"]) == 4, driver["row_count"], "Step 38 driver row count stays 4"))
    rows.append(check("step38_driver_stable_count", int(driver["stable_count"]) == 4, driver["stable_count"], "Step 38 driver rows stay stable"))
    rows.append(check("step38_cycle_proxy", bool(proxy["phase_alignment_pass"]) and bool(proxy["cavity_volume_cycle_pass"]) and bool(proxy["funnel_aperture_cycle_pass"]), True, "Step 38 cycle proxy diagnostics stay passing"))
    rows.append(check("step38_wall_velocity_cycle_quality", bool(wall["quality_pass"]), wall["quality_pass"], "Step 38 wall velocity cycle quality stays passing"))
    rows.append(check("step38_tethered_guard", bool(guard["guard_pass"]), guard["guard_pass"], "Step 38 tethered guard stays passing"))
    rows.append(check("step38_large_file_count", int(artifact["large_file_count"]) == 0, artifact["large_file_count"], "Step 38 artifact large-file count stays 0"))
    rows.append(check("step38_vtr_count", int(artifact["step38_vtr_count"]) == 0, artifact["step38_vtr_count"], "Step 38 wrote no VTR outputs"))
    rows.append(check("step38_particle_npy_count", int(artifact["step38_particle_npy_count"]) == 0, artifact["step38_particle_npy_count"], "Step 38 wrote no particle NPY outputs"))
    return rows


def check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
