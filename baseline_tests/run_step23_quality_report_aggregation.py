import os

from step23_common import ROOT, write_json
from src.run_utils import save_csv_rows


DRIVER_ROOTS = [
    "outputs/step23_quality_gated_voxel_sphere_48_modes",
    "outputs/step23_quality_gated_mesh_cube_48_modes",
    "outputs/step23_quality_gated_mesh_ellipsoid_48_modes",
    "outputs/step23_quality_gated_imported_geometry_64_feasibility",
]


QUALITY_REPORT_FIELDS = [
    "case",
    "geometry_type",
    "quality_kind",
    "pass",
    "severity",
    "warnings_count",
    "reasons_count",
    "vertices_count",
    "faces_count",
    "boundary_edge_count",
    "degenerate_face_count",
    "occupied_count",
    "connected_component_count",
    "largest_component_fraction",
    "source_report_path",
]


def _read_json(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _collect_reports():
    rows = []
    for root in DRIVER_ROOTS:
        root_path = os.path.join(ROOT, root)
        if not os.path.isdir(root_path):
            raise RuntimeError(f"missing Step 23 driver output root: {root}")

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
                "pass": bool(gate.get("pass", False)),
                "severity": gate.get("severity", ""),
                "warnings_count": len(gate.get("warnings", [])),
                "reasons_count": len(gate.get("reasons", [])),
                "vertices_count": int(report.get("vertices_count", 0)),
                "faces_count": int(report.get("faces_count", 0)),
                "boundary_edge_count": int(report.get("boundary_edge_count", 0)),
                "degenerate_face_count": int(report.get("degenerate_face_count", 0)),
                "occupied_count": int(report.get("occupied_count", 0)),
                "connected_component_count": int(report.get("connected_component_count", 0)),
                "largest_component_fraction": float(report.get("largest_component_fraction", 0.0)),
                "source_report_path": _relative_path(report_path),
            }
            _assert_quality_report_row(row)
            rows.append(row)
    rows.sort(key=lambda row: row["source_report_path"])
    return rows


def _assert_quality_report_row(row):
    if not _as_bool(row["pass"]):
        raise RuntimeError(f"quality report did not pass: {row}")
    if row["severity"] == "error":
        raise RuntimeError(f"quality report has error severity: {row}")
    if int(row["reasons_count"]) != 0:
        raise RuntimeError(f"quality report has reasons: {row}")
    if row["geometry_type"] == "mesh":
        if int(row["vertices_count"]) <= 0 or int(row["faces_count"]) <= 0:
            raise RuntimeError(f"mesh quality report missing mesh size: {row}")
        if int(row["boundary_edge_count"]) != 0 or int(row["degenerate_face_count"]) != 0:
            raise RuntimeError(f"mesh quality report has boundary or degenerate issues: {row}")
    if row["geometry_type"] == "voxel":
        if int(row["occupied_count"]) <= 0 or int(row["connected_component_count"]) < 1:
            raise RuntimeError(f"voxel quality report missing occupancy/connectivity: {row}")


def _summary(rows):
    return {
        "quality_report_count": len(rows),
        "pass_count": sum(1 for row in rows if _as_bool(row["pass"])),
        "error_count": sum(1 for row in rows if row["severity"] == "error"),
        "warning_count": sum(1 for row in rows if row["severity"] == "warning"),
        "mesh_row_count": sum(1 for row in rows if row["geometry_type"] == "mesh"),
        "voxel_row_count": sum(1 for row in rows if row["geometry_type"] == "voxel"),
    }


def main():
    os.chdir(ROOT)
    rows = _collect_reports()
    summary = _summary(rows)
    if summary["quality_report_count"] < 15:
        raise RuntimeError(f"expected at least 15 quality reports, got {summary['quality_report_count']}")
    if summary["error_count"] != 0:
        raise RuntimeError(f"quality reports contain errors: {summary}")
    if summary["pass_count"] != len(rows):
        raise RuntimeError(f"not all quality reports passed: {summary}")

    out_dir = os.path.join(ROOT, "outputs", "step23_quality_report_aggregation")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "quality_report_summary.csv")
    json_path = os.path.join(out_dir, "quality_report_summary.json")
    save_csv_rows(rows, csv_path, fieldnames=QUALITY_REPORT_FIELDS)
    write_json(json_path, summary)

    print("Step 23 quality report aggregation")
    print(f"quality_report_count={summary['quality_report_count']}")
    print(f"pass_count={summary['pass_count']}")
    print(f"error_count={summary['error_count']}")
    print("[OK] Step 23 quality report aggregation finished")


if __name__ == "__main__":
    main()
