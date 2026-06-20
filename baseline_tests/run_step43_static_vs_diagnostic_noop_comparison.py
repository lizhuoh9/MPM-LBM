import os

from step43_common import ROOT, read_json, write_csv_rows, write_json, write_log


FIELDS = [
    "comparison",
    "reaction_transfer_mode",
    "static_case",
    "diagnostic_case",
    "both_stable",
    "rho_min_delta",
    "rho_max_delta",
    "lbm_max_v_delta",
    "mpm_min_J_delta",
    "projected_mass_delta",
    "active_cell_count_delta",
    "bb_link_count_delta",
    "area_scale_delta",
    "diagnostic_no_op_pass",
    "comparison_pass",
    "notes",
]


def main():
    os.chdir(ROOT)
    static_rows = read_json("outputs/step43_static_driver_regression/static_driver_results.json")["rows"]
    diagnostic_rows = read_json("outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json")["rows"]
    rows = compare_rows(static_rows, diagnostic_rows)
    summary = {
        "row_count": len(rows),
        "comparison_pass_count": sum(1 for row in rows if row["comparison_pass"]),
        "comparison_pass": all(row["comparison_pass"] for row in rows),
    }
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 43 static-vs-diagnostic no-op comparison failed: {rows}")
    out_dir = ROOT / "outputs" / "step43_static_vs_diagnostic_noop_comparison"
    write_csv_rows(out_dir / "static_vs_diagnostic_noop.csv", rows, FIELDS)
    write_json(out_dir / "static_vs_diagnostic_noop.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 43 static-vs-diagnostic no-op comparison finished"
    write_log("logs/step43_static_vs_diagnostic_noop_comparison.log", [marker, f"row_count={summary['row_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def compare_rows(static_rows, diagnostic_rows):
    static_by_transfer = {row["reaction_transfer_mode"]: row for row in static_rows}
    rows = []
    for diagnostic in sorted(diagnostic_rows, key=lambda row: row["reaction_transfer_mode"]):
        static = static_by_transfer[diagnostic["reaction_transfer_mode"]]
        row = {
            "comparison": f"static_vs_diagnostic_noop_{diagnostic['reaction_transfer_mode']}",
            "reaction_transfer_mode": diagnostic["reaction_transfer_mode"],
            "static_case": static["case"],
            "diagnostic_case": diagnostic["case"],
            "both_stable": bool(static["stable"] and diagnostic["stable"]),
            "rho_min_delta": float(diagnostic["rho_min_global"]) - float(static["rho_min_global"]),
            "rho_max_delta": float(diagnostic["rho_max_global"]) - float(static["rho_max_global"]),
            "lbm_max_v_delta": float(diagnostic["lbm_max_v_global"]) - float(static["lbm_max_v_global"]),
            "mpm_min_J_delta": float(diagnostic["mpm_min_J_global"]) - float(static["mpm_min_J_global"]),
            "projected_mass_delta": float(diagnostic["projected_mass_max"]) - float(static["projected_mass_max"]),
            "active_cell_count_delta": int(diagnostic["active_cell_count"]) - int(static["active_cell_count"]),
            "bb_link_count_delta": int(diagnostic["bb_link_count_max"]) - int(static["bb_link_count_max"]),
            "area_scale_delta": float(diagnostic["area_scale_final"]) - float(static["area_scale_final"]),
            "diagnostic_no_op_pass": bool(diagnostic["geometry_motion_no_op_pass"]),
            "notes": "Step 43 diagnostic geometry motion is report-only; physics diagnostics must match static row",
        }
        row["comparison_pass"] = bool(
            row["both_stable"]
            and row["diagnostic_no_op_pass"]
            and abs(row["rho_min_delta"]) <= 1.0e-6
            and abs(row["rho_max_delta"]) <= 1.0e-6
            and abs(row["lbm_max_v_delta"]) <= 1.0e-6
            and abs(row["mpm_min_J_delta"]) <= 1.0e-6
            and abs(row["projected_mass_delta"]) <= 1.0e-6
            and int(row["active_cell_count_delta"]) == 0
            and int(row["bb_link_count_delta"]) == 0
            and abs(row["area_scale_delta"]) <= 1.0e-12
        )
        rows.append(row)
    return rows


if __name__ == "__main__":
    main()
