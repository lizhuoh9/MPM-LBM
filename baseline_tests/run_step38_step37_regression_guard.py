import os

from step38_common import ROOT, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 38 Step 37 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step38_step37_regression_guard"
    write_csv_rows(out_dir / "step37_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step37_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 Step 37 regression guard finished"
    write_log("logs/step38_step37_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = []
    rows.append(check("step37_report_exists", (ROOT / "STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_REPORT.md").is_file(), "STEP37 report", "Step 37 report remains present"))
    driver = read_json("outputs/step37_application_window_driver/application_window_results.json")["summary"]
    envelope = read_json("outputs/step37_application_envelope_summary/application_envelope.json")["summary"]
    step36_guard = read_json("outputs/step37_step36_regression_guard/step36_regression_guard.json")["summary"]
    artifact = read_json("outputs/step37_artifact_manifest/artifact_summary.json")
    rows.append(check("step37_driver_row_count", int(driver["row_count"]) == 4, driver["row_count"], "Step 37 driver row count stays 4"))
    rows.append(check("step37_driver_stable_count", int(driver["stable_count"]) == 4, driver["stable_count"], "Step 37 driver rows stay stable"))
    rows.append(check("step37_experimental_report_count", int(driver["max_application_report_count"]) >= 20, driver["max_application_report_count"], "Step 37 experimental rows still wrote 20 application reports"))
    rows.append(check("step37_application_envelope", bool(envelope["application_envelope_pass"]), envelope["application_envelope_pass"], "Step 37 application envelope stays passing"))
    rows.append(check("step37_step36_guard", bool(step36_guard["regression_pass"]), step36_guard["regression_pass"], "Step 37 Step 36 guard stays passing"))
    rows.append(check("step37_large_file_count", int(artifact["large_file_count"]) == 0, artifact["large_file_count"], "Step 37 artifact large-file count stays 0"))
    rows.append(check("step37_vtr_count", int(artifact["step37_vtr_count"]) == 0, artifact["step37_vtr_count"], "Step 37 wrote no VTR outputs"))
    rows.append(check("step37_particle_npy_count", int(artifact["step37_particle_npy_count"]) == 0, artifact["step37_particle_npy_count"], "Step 37 wrote no particle NPY outputs"))
    return rows


def check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
