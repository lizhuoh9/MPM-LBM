import os

from step41_common import ROOT, STEP41_DRIVER_CONFIGS, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.tethered_cycle_diagnostics import guard_rows, summarize_no_free_body_state


def main():
    os.chdir(ROOT)
    configs = [read_json(path) for path in STEP41_DRIVER_CONFIGS]
    summary = summarize_no_free_body_state(configs, ROOT / "outputs" / "step41_64_selected_parameter_driver")
    summary["guard"] = "Step 41 selected-parameter 64 feasibility tethered no-free-body guard"
    summary["guard_pass"] = bool(
        int(summary["config_count"]) == 4
        and int(summary["free_body_state_file_count"]) == 0
        and int(summary["body_trajectory_output_count"]) == 0
        and summary["rigid_body_integrator_enabled"] is False
        and summary["body_position_state_enabled"] is False
        and summary["swimming_displacement_claim_enabled"] is False
        and summary["target_u_lbm_zero_for_cycle_configs"] is True
    )
    rows = guard_rows(summary)
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 41 tethered no-free-body guard failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_tethered_no_free_body_guard"
    write_csv_rows(out_dir / "tethered_no_free_body_guard.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "tethered_no_free_body_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 41 tethered no-free-body guard finished"
    write_log("logs/step41_tethered_no_free_body_guard.log", [marker, f"guard_pass={summary['guard_pass']}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
