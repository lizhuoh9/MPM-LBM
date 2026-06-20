import os

from step34_common import ROOT, write_csv_rows, write_json, write_log


QUALITY_REPORT_FIELDS = [
    "case",
    "candidate_id",
    "geometry_type",
    "mode",
    "reaction_transfer_mode",
    "boundary_motion_mode",
    "quality_kind",
    "strict",
    "pass",
    "severity",
    "warnings_count",
    "reasons_count",
    "occupied_count",
    "connected_component_count",
    "largest_component_fraction",
    "report_size_bytes",
    "source_report_path",
]


def main():
    os.chdir(ROOT)
    rows = _collect_reports()
    summary = _summary(rows)
    _assert_summary(summary)

    out_dir = ROOT / "outputs" / "step34_quality_report_aggregation"
    write_csv_rows(out_dir / "quality_report_summary.csv", rows, QUALITY_REPORT_FIELDS)
    write_json(out_dir / "quality_report_summary.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 34 quality report aggregation finished"
    write_log(
        "logs/step34_quality_report_aggregation.log",
        [
            marker,
            f"quality_report_count={summary['quality_report_count']}",
            f"pass_count={summary['pass_count']}",
            f"warning_count={summary['warning_count']}",
            f"error_count={summary['error_count']}",
        ],
    )
    print(f"quality_report_count={summary['quality_report_count']}")
    print(marker)


def _collect_reports():
    roots = [
        ROOT / "outputs" / "step34_static_driver_regression",
        ROOT / "outputs" / "step34_prescribed_interface_noop_smoke",
    ]
    rows = []
    for root_path in roots:
        if not root_path.is_dir():
            raise RuntimeError(f"missing Step 34 driver output root: {root_path}")
        for dirpath, _, filenames in os.walk(root_path):
            if "geometry_quality_report.json" not in filenames:
                continue
            rows.append(_row_from_report(os.path.join(dirpath, "geometry_quality_report.json")))
    rows.sort(key=lambda row: row["source_report_path"])
    return rows


def _row_from_report(report_path):
    payload = _read_json(report_path)
    report = payload["report"]
    gate = payload["gate"]
    case = os.path.basename(os.path.dirname(report_path))
    mode, transfer, boundary_mode = _modes_from_case(case)
    row = {
        "case": case,
        "candidate_id": "squid_proxy_boundary_motion_interface",
        "geometry_type": report.get("geometry_type", ""),
        "mode": mode,
        "reaction_transfer_mode": transfer,
        "boundary_motion_mode": boundary_mode,
        "quality_kind": report.get("quality_kind", ""),
        "strict": bool(gate.get("strict", False)),
        "pass": bool(gate.get("pass", False)),
        "severity": gate.get("severity", ""),
        "warnings_count": len(gate.get("warnings", [])),
        "reasons_count": len(gate.get("reasons", [])),
        "occupied_count": int(report.get("occupied_count", 0)),
        "connected_component_count": int(report.get("connected_component_count", 0)),
        "largest_component_fraction": float(report.get("largest_component_fraction", 0.0)),
        "report_size_bytes": int(os.path.getsize(report_path)),
        "source_report_path": _relative_path(report_path),
    }
    _assert_row(row)
    return row


def _assert_row(row):
    if row["geometry_type"] != "squid_proxy" or row["quality_kind"] != "procedural_voxelized":
        raise RuntimeError(f"Step 34 quality report must be procedural squid proxy quality: {row}")
    if row["strict"] is not True or row["pass"] is not True or row["severity"] != "ok":
        raise RuntimeError(f"Step 34 quality report must pass strict gate: {row}")
    if int(row["warnings_count"]) != 0 or int(row["reasons_count"]) != 0:
        raise RuntimeError(f"Step 34 quality report must have zero warnings and reasons: {row}")
    if int(row["occupied_count"]) <= 0 or int(row["connected_component_count"]) <= 0:
        raise RuntimeError(f"Step 34 quality report has no procedural occupancy: {row}")
    if int(row["report_size_bytes"]) >= 100_000:
        raise RuntimeError(f"Step 34 quality report is too large: {row}")


def _summary(rows):
    return {
        "quality_report_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "strict_count": sum(1 for row in rows if bool(row["strict"])),
        "static_boundary_motion_report_count": sum(1 for row in rows if row["boundary_motion_mode"] == "static"),
        "prescribed_boundary_motion_report_count": sum(1 for row in rows if row["boundary_motion_mode"] == "prescribed_kinematic"),
        "error_count": sum(1 for row in rows if row["severity"] == "error"),
        "warning_count": sum(1 for row in rows if row["severity"] == "warning" or int(row["warnings_count"]) > 0),
        "procedural_row_count": sum(1 for row in rows if row["quality_kind"] == "procedural_voxelized"),
        "quality_report_total_size_bytes": sum(int(row["report_size_bytes"]) for row in rows),
        "quality_report_max_size_bytes": max(int(row["report_size_bytes"]) for row in rows) if rows else 0,
    }


def _assert_summary(summary):
    if int(summary["quality_report_count"]) != 6:
        raise RuntimeError(f"expected 6 Step 34 quality reports: {summary}")
    if int(summary["pass_count"]) != 6 or int(summary["strict_count"]) != 6:
        raise RuntimeError(f"all Step 34 quality reports must pass strict gates: {summary}")
    if int(summary["static_boundary_motion_report_count"]) != 4 or int(summary["prescribed_boundary_motion_report_count"]) != 2:
        raise RuntimeError(f"Step 34 quality reports have wrong boundary mode split: {summary}")
    if int(summary["error_count"]) != 0 or int(summary["warning_count"]) != 0:
        raise RuntimeError(f"Step 34 quality reports have warnings or errors: {summary}")
    if int(summary["procedural_row_count"]) != 6:
        raise RuntimeError(f"Step 34 quality reports must all be procedural rows: {summary}")
    if int(summary["quality_report_total_size_bytes"]) <= 0 or int(summary["quality_report_max_size_bytes"]) >= 100_000:
        raise RuntimeError(f"Step 34 quality report size summary is wrong: {summary}")


def _modes_from_case(case):
    boundary_mode = "prescribed_kinematic" if "prescribed_interface" in case else "static"
    if case.endswith("_link_area"):
        return "moving_boundary", "link_area_experimental", boundary_mode
    if case.endswith("_moving_boundary"):
        return "moving_boundary", "engineering", boundary_mode
    if case.endswith("_penalty"):
        return "penalty", "engineering", boundary_mode
    if case.endswith("_none"):
        return "none", "engineering", boundary_mode
    return "", "", boundary_mode


def _read_json(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


if __name__ == "__main__":
    main()
