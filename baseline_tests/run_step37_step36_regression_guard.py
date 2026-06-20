import os

from step37_common import ROOT, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 37 Step 36 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step37_step36_regression_guard"
    write_csv_rows(out_dir / "step36_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step36_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 Step 36 regression guard finished"
    write_log("logs/step37_step36_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = []
    rows.append(check("step36_report_exists", (ROOT / "STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_REPORT.md").is_file(), "STEP36 report", "Step 36 report remains present"))
    experimental = read_json("outputs/step36_experimental_application_smoke/experimental_application_results.json")["summary"]
    quality = read_json("outputs/step36_wall_velocity_application_quality/application_quality.json")["summary"]
    step35_guard = read_json("outputs/step36_step35_regression_guard/step35_regression_guard.json")["summary"]
    artifact = read_json("outputs/step36_artifact_manifest/artifact_summary.json")
    rows.append(check("step36_experimental_rows", int(experimental["driver_row_count"]) == 3, experimental["driver_row_count"], "Step 36 experimental row count stays 3"))
    rows.append(check("step36_experimental_stable", int(experimental["stable_count"]) == 3, experimental["stable_count"], "Step 36 experimental rows stay stable"))
    rows.append(check("step36_application_quality", bool(quality["quality_pass"]), quality["quality_pass"], "Step 36 application quality stays passing"))
    rows.append(check("step36_step35_guard", bool(step35_guard["regression_pass"]), step35_guard["regression_pass"], "Step 36 Step 35 regression guard stays passing"))
    rows.append(check("step36_large_file_count", int(artifact["large_file_count"]) == 0, artifact["large_file_count"], "Step 36 artifact large-file count stays 0"))
    rows.append(check("step36_vtr_count", int(artifact["step36_vtr_count"]) == 0, artifact["step36_vtr_count"], "Step 36 wrote no VTR outputs"))
    rows.append(check("step36_particle_npy_count", int(artifact["step36_particle_npy_count"]) == 0, artifact["step36_particle_npy_count"], "Step 36 wrote no particle NPY outputs"))
    return rows


def check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
