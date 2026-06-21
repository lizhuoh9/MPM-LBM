import os

from step50_common import ROOT, one_cycle_closure_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "phase0",
    "closure_phase",
    "phase0_projected_mass",
    "closure_projected_mass",
    "phase0_phase1_projected_mass_delta",
    "phase0_active_cell_count",
    "closure_active_cell_count",
    "phase0_phase1_active_cell_delta",
    "phase0_applied_velocity",
    "closure_applied_velocity",
    "phase0_phase1_applied_velocity_delta",
    "diagnostic_only",
    "persist_projected_state",
    "persist_displaced_geometry",
    "geometry_projection_closure_pass",
    "wall_velocity_closure_pass",
    "cycle_proxy_closure_pass",
    "closure_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import summarize_cycle_closure

    rows, summary = summarize_cycle_closure(one_cycle_closure_rows())
    if not summary["closure_pass"]:
        raise RuntimeError(f"Step 50 cycle closure diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_cycle_closure_diagnostics"
    write_csv_rows(out_dir / "cycle_closure_diagnostics.csv", rows, FIELDS)
    write_json(out_dir / "cycle_closure_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 cycle closure diagnostics finished"
    write_log("logs/step50_cycle_closure_diagnostics.log", [marker, f"closure_pass={summary['closure_pass']}", f"closure_pass_count={summary['closure_pass_count']}"])
    print(f"closure_pass_count={summary['closure_pass_count']}")
    print(marker)


if __name__ == "__main__":
    main()
