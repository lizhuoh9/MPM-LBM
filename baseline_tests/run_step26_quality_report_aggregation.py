import os

from step26_common import ROOT, write_csv_rows, write_json, write_log


QUALITY_REPORT_FIELDS = [
    "case",
    "candidate_id",
    "geometry_type",
    "mode",
    "reaction_transfer_mode",
    "quality_kind",
    "strict",
    "pass",
    "severity",
    "warnings_count",
    "reasons_count",
    "vertices_count",
    "faces_count",
    "boundary_edge_count",
    "degenerate_face_count",
    "nonmanifold_edge_count",
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

    out_dir = ROOT / "outputs" / "step26_quality_report_aggregation"
    write_csv_rows(out_dir / "quality_report_summary.csv", rows, QUALITY_REPORT_FIELDS)
    write_json(out_dir / "quality_report_summary.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 26 quality report aggregation finished"
    write_log(
        "logs/step26_quality_report_aggregation.log",
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
    rows = []
    for root in ("outputs/step26_short_driver_mesh_48_modes", "outputs/step26_short_driver_voxel_48_modes"):
        root_path = ROOT / root
        if not root_path.is_dir():
            raise RuntimeError(f"missing Step 26 driver output root: {root}")
        for dirpath, _, filenames in os.walk(root_path):
            if "geometry_quality_report.json" not in filenames:
                continue
            report_path = os.path.join(dirpath, "geometry_quality_report.json")
            rows.append(_row_from_report(report_path))
    rows.sort(key=lambda row: row["source_report_path"])
    return rows


def _row_from_report(report_path):
    payload = _read_json(report_path)
    report = payload["report"]
    gate = payload["gate"]
    case = os.path.basename(os.path.dirname(report_path))
    mode, transfer = _mode_from_case(case)
    row = {
        "case": case,
        "candidate_id": _candidate_from_case(case),
        "geometry_type": report.get("geometry_type", ""),
        "mode": mode,
        "reaction_transfer_mode": transfer,
        "quality_kind": report.get("quality_kind", ""),
        "strict": bool(gate.get("strict", False)),
        "pass": bool(gate.get("pass", False)),
        "severity": gate.get("severity", ""),
        "warnings_count": len(gate.get("warnings", [])),
        "reasons_count": len(gate.get("reasons", [])),
        "vertices_count": int(report.get("vertices_count", 0)),
        "faces_count": int(report.get("faces_count", 0)),
        "boundary_edge_count": int(report.get("boundary_edge_count", 0)),
        "degenerate_face_count": int(report.get("degenerate_face_count", 0)),
        "nonmanifold_edge_count": int(report.get("nonmanifold_edge_count", 0)),
        "occupied_count": int(report.get("occupied_count", 0)),
        "connected_component_count": int(report.get("connected_component_count", 0)),
        "largest_component_fraction": float(report.get("largest_component_fraction", 0.0)),
        "report_size_bytes": int(os.path.getsize(report_path)),
        "source_report_path": _relative_path(report_path),
    }
    _assert_row(row)
    return row


def _assert_row(row):
    if row["strict"] is not True or row["pass"] is not True or row["severity"] != "ok":
        raise RuntimeError(f"Step 26 quality report must pass strict gate: {row}")
    if int(row["warnings_count"]) != 0 or int(row["reasons_count"]) != 0:
        raise RuntimeError(f"Step 26 quality report must have zero warnings and reasons: {row}")
    if int(row["report_size_bytes"]) >= 100_000:
        raise RuntimeError(f"Step 26 quality report is too large: {row}")
    if row["geometry_type"] == "mesh":
        if int(row["vertices_count"]) <= 0 or int(row["faces_count"]) <= 0:
            raise RuntimeError(f"Step 26 mesh quality report missing mesh size: {row}")
        if int(row["boundary_edge_count"]) != 0 or int(row["degenerate_face_count"]) != 0:
            raise RuntimeError(f"Step 26 mesh quality report has topology issues: {row}")
        if int(row["nonmanifold_edge_count"]) != 0:
            raise RuntimeError(f"Step 26 mesh quality report has nonmanifold edges: {row}")
    if row["geometry_type"] == "voxel":
        if int(row["occupied_count"]) <= 0:
            raise RuntimeError(f"Step 26 voxel quality report has no occupancy: {row}")
        if int(row["connected_component_count"]) != 1:
            raise RuntimeError(f"Step 26 voxel quality report must be connected: {row}")
        if float(row["largest_component_fraction"]) != 1.0:
            raise RuntimeError(f"Step 26 voxel quality report must have full largest component: {row}")


def _summary(rows):
    return {
        "quality_report_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "strict_count": sum(1 for row in rows if bool(row["strict"])),
        "error_count": sum(1 for row in rows if row["severity"] == "error"),
        "warning_count": sum(1 for row in rows if row["severity"] == "warning" or int(row["warnings_count"]) > 0),
        "mesh_row_count": sum(1 for row in rows if row["geometry_type"] == "mesh"),
        "voxel_row_count": sum(1 for row in rows if row["geometry_type"] == "voxel"),
        "quality_report_total_size_bytes": sum(int(row["report_size_bytes"]) for row in rows),
        "quality_report_max_size_bytes": max(int(row["report_size_bytes"]) for row in rows) if rows else 0,
    }


def _assert_summary(summary):
    if int(summary["quality_report_count"]) != 8:
        raise RuntimeError(f"expected 8 Step 26 quality reports: {summary}")
    if int(summary["pass_count"]) != 8 or int(summary["strict_count"]) != 8:
        raise RuntimeError(f"all Step 26 quality reports must pass strict gates: {summary}")
    if int(summary["error_count"]) != 0 or int(summary["warning_count"]) != 0:
        raise RuntimeError(f"Step 26 quality reports have warnings or errors: {summary}")
    if int(summary["mesh_row_count"]) != 4 or int(summary["voxel_row_count"]) != 4:
        raise RuntimeError(f"Step 26 quality report type split is wrong: {summary}")


def _candidate_from_case(case):
    if case.startswith("real_candidate_smoke_mesh"):
        return "real_candidate_smoke_mesh"
    if case.startswith("real_candidate_smoke_voxel"):
        return "real_candidate_smoke_voxel"
    return case


def _mode_from_case(case):
    if case.endswith("_48_link_area"):
        return "moving_boundary", "link_area_experimental"
    if case.endswith("_48_moving_boundary"):
        return "moving_boundary", "engineering"
    if case.endswith("_48_penalty"):
        return "penalty", "engineering"
    if case.endswith("_48_none"):
        return "none", "engineering"
    return "", ""


def _read_json(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


if __name__ == "__main__":
    main()
