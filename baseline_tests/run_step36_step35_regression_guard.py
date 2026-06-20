import os

from step35_common import STEP35_LOG_MARKERS
from step36_common import ROOT, write_csv_rows, write_json, write_log


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
        raise RuntimeError(f"Step 36 Step 35 regression guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step36_step35_regression_guard"
    write_csv_rows(out_dir / "step35_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step35_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 36 Step 35 regression guard finished"
    write_log(
        "logs/step36_step35_regression_guard.log",
        [marker, f"row_count={summary['row_count']}", f"regression_pass={summary['regression_pass']}"],
    )
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def regression_rows():
    rows = []
    config_payload = read_json("outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.json")
    field_payload = read_json("outputs/step35_wall_velocity_field/wall_velocity_field.json")
    no_update_payload = read_json("outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json")
    rows.append(check("step35_config_validation_pass", bool(config_payload["summary"]["validation_pass"]), config_payload["summary"]["validation_pass"], "Step 35 config remains valid"))
    rows.append(check("step35_wall_velocity_row_count", int(field_payload["summary"]["row_count"]) == 63, field_payload["summary"]["row_count"], "Step 35 still has 63 diagnostic rows"))
    rows.append(check("step35_no_lbm_update_pass", bool(no_update_payload["summary"]["guard_pass"]), no_update_payload["summary"]["guard_pass"], "Step 35 remains diagnostic-only"))
    rows.append(check("step35_apply_to_lbm_count_zero", int(field_payload["summary"]["apply_to_lbm_count"]) == 0, field_payload["summary"]["apply_to_lbm_count"], "Step 35 does not apply to LBM"))
    rows.append(check("step35_lbm_population_update_count_zero", int(field_payload["summary"]["lbm_population_update_enabled_count"]) == 0, field_payload["summary"]["lbm_population_update_enabled_count"], "Step 35 does not update populations"))
    rows.append(check("step35_moving_bounceback_update_count_zero", int(field_payload["summary"]["moving_bounceback_update_enabled_count"]) == 0, field_payload["summary"]["moving_bounceback_update_enabled_count"], "Step 35 does not update moving bounce-back"))
    for path, marker in STEP35_LOG_MARKERS.items():
        log_path = ROOT / path
        rows.append(check(f"log_marker_{log_path.stem}", log_path.is_file() and marker in log_path.read_text(encoding="utf-8"), path, "Step 35 log marker is present"))
    return rows


def check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
