import os

from step24_common import ROOT, STEP24_OUTPUT_ROOTS, write_json, write_log
from src.run_utils import save_csv_rows


QUALITY_REPORT_FIELDS = [
    "case",
    "geometry_type",
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


def _read_json(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _collect_reports():
    rows = []
    for root in STEP24_OUTPUT_ROOTS:
        root_path = os.path.join(ROOT, root)
        if not os.path.isdir(root_path):
            raise RuntimeError(f"missing Step 24 driver output root: {root}")

        for dirpath, _, filenames in os.walk(root_path):
            if "geometry_quality_report.json" not in filenames:
                continue
            report_path = os.path.join(dirpath, "geometry_quality_report.json")
            payload = _read_json(report_path)
            report = payload["report"]
            gate = payload["gate"]
            row = {
                "case": os.path.basename(dirpath),
                "geometry_type": report.get("geometry_type", ""),
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
            _assert_quality_report_row(row)
            rows.append(row)
    rows.sort(key=lambda row: row["source_report_path"])
    return rows


def _assert_quality_report_row(row):
    if row["strict"] is not True:
        raise RuntimeError(f"Step 24 report is not strict: {row}")
    if row["pass"] is not True:
        raise RuntimeError(f"quality report did not pass: {row}")
    if row["severity"] != "ok":
        raise RuntimeError(f"quality report severity must be ok: {row}")
    if int(row["warnings_count"]) != 0 or int(row["reasons_count"]) != 0:
        raise RuntimeError(f"quality report has warnings or reasons: {row}")
    if int(row["report_size_bytes"]) >= 100_000:
        raise RuntimeError(f"quality report is too large: {row}")
    if row["geometry_type"] == "mesh":
        if int(row["vertices_count"]) <= 0 or int(row["faces_count"]) <= 0:
            raise RuntimeError(f"mesh quality report missing mesh size: {row}")
        if (
            int(row["boundary_edge_count"]) != 0
            or int(row["degenerate_face_count"]) != 0
            or int(row["nonmanifold_edge_count"]) != 0
        ):
            raise RuntimeError(f"mesh strict report has topology issues: {row}")
    if row["geometry_type"] == "voxel":
        if int(row["occupied_count"]) <= 0:
            raise RuntimeError(f"voxel quality report has no occupancy: {row}")
        if int(row["connected_component_count"]) != 1:
            raise RuntimeError(f"voxel quality report must have one connected component: {row}")
        if float(row["largest_component_fraction"]) != 1.0:
            raise RuntimeError(f"voxel quality report must be fully connected: {row}")


def _summary(rows):
    return {
        "quality_report_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "error_count": sum(1 for row in rows if row["severity"] == "error"),
        "warning_count": sum(1 for row in rows if row["severity"] == "warning" or int(row["warnings_count"]) > 0),
        "mesh_row_count": sum(1 for row in rows if row["geometry_type"] == "mesh"),
        "voxel_row_count": sum(1 for row in rows if row["geometry_type"] == "voxel"),
        "quality_report_total_size_bytes": sum(int(row["report_size_bytes"]) for row in rows),
        "quality_report_max_size_bytes": max(int(row["report_size_bytes"]) for row in rows) if rows else 0,
    }


def main():
    os.chdir(ROOT)
    rows = _collect_reports()
    summary = _summary(rows)
    if summary["quality_report_count"] != 9:
        raise RuntimeError(f"expected exactly 9 quality reports, got {summary['quality_report_count']}")
    if summary["pass_count"] != 9 or summary["error_count"] != 0 or summary["warning_count"] != 0:
        raise RuntimeError(f"Step 24 quality reports did not all pass cleanly: {summary}")

    out_dir = os.path.join(ROOT, "outputs", "step24_quality_report_aggregation")
    os.makedirs(out_dir, exist_ok=True)
    save_csv_rows(rows, os.path.join(out_dir, "quality_report_summary.csv"), fieldnames=QUALITY_REPORT_FIELDS)
    write_json(os.path.join(out_dir, "quality_report_summary.json"), summary)

    marker = "[OK] Step 24 quality report aggregation finished"
    write_log(
        "logs/step24_quality_report_aggregation.log",
        [
            marker,
            f"quality_report_count={summary['quality_report_count']}",
            f"pass_count={summary['pass_count']}",
            f"error_count={summary['error_count']}",
            f"warning_count={summary['warning_count']}",
        ],
    )
    print("Step 24 quality report aggregation")
    print(f"quality_report_count={summary['quality_report_count']}")
    print(f"pass_count={summary['pass_count']}")
    print(f"error_count={summary['error_count']}")
    print(f"warning_count={summary['warning_count']}")
    print(marker)


if __name__ == "__main__":
    main()
