import os

from step35_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    rows = build_regression_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
    }
    summary["regression_pass"] = summary["row_count"] == summary["pass_count"]
    for row in rows:
        summary[row["check"]] = row["observed"]
    if not bool(summary["regression_pass"]):
        raise RuntimeError(f"Step 35 Step 34 regression guard failed: {summary}")

    out_dir = ROOT / "outputs" / "step35_step34_regression_guard"
    write_csv_rows(out_dir / "step34_regression_guard.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "step34_regression_guard.json", summary)
    marker = "[OK] Step 35 Step 34 regression guard finished"
    write_log(
        "logs/step35_step34_regression_guard.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"pass_count={summary['pass_count']}",
            f"regression_pass={summary['regression_pass']}",
        ],
    )
    print(f"regression_pass={summary['regression_pass']}")
    print(marker)


def build_regression_rows() -> list[dict]:
    interface = read_json("outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report.json")["summary"]
    noop = read_json("outputs/step34_noop_state_guard/noop_state_guard.json")["summary"]
    quality = read_json("outputs/step34_quality_report_aggregation/quality_report_summary.json")["summary"]
    artifact = read_json("outputs/step34_artifact_manifest/artifact_summary.json")
    report_exists = (ROOT / "STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md").is_file()
    return [
        check_row("step34_report_exists", report_exists, True, "Step 34 report must remain present"),
        check_row("step34_no_op_pass", bool(interface["no_op_pass"]), True, "Step 34 interface no-op must remain accepted"),
        check_row("step34_noop_state_guard_pass_count", int(noop["pass_count"]), 2, "Step 34 no-op state guard must keep two passing rows"),
        check_row("step34_quality_report_count", int(quality["quality_report_count"]), 6, "Step 34 quality report count must remain six"),
        check_row("step34_large_file_count", int(artifact["large_file_count"]), 0, "Step 34 artifact large-file count must remain zero"),
        check_row("step34_vtr_count", int(artifact["step34_vtr_count"]), 0, "Step 34 must not contain .vtr outputs"),
        check_row("step34_particle_npy_count", int(artifact["step34_particle_npy_count"]), 0, "Step 34 must not contain particle .npy outputs"),
    ]


def check_row(check: str, observed, expected, notes: str) -> dict:
    return {"check": check, "observed": observed, "expected": expected, "pass": observed == expected, "notes": notes}


if __name__ == "__main__":
    main()
