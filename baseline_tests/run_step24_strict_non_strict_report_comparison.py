from dataclasses import replace
import os

from step24_common import ROOT, read_csv_rows, read_json, row_key, write_json, write_log
from src.geometry_config import GeometryConfig
from src.geometry_quality import GeometryQualityGate, analyze_geometry_config
from src.run_utils import save_csv_rows


STEP23_CSVS = [
    "outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv",
]

STEP24_CSVS = [
    "outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv",
    "outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv",
]

COMPARISON_FIELDS = [
    "case",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
    "comparison_source",
    "strict_report_path",
    "nonstrict_report_path",
    "same_quality_kind",
    "same_geometry_type",
    "same_pass",
    "same_severity",
    "strict_reasons_count",
    "nonstrict_reasons_count",
    "strict_warnings_count",
    "nonstrict_warnings_count",
    "mesh_counts_match",
    "voxel_counts_match",
    "reports_match",
    "notes",
]


def _load_rows(paths):
    rows = []
    for relative_path in paths:
        rows.extend(read_csv_rows(relative_path))
    return rows


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _safe_key_text(key):
    return f"{key[0]}_{key[3]}_{key[1]}_{key[2]}".replace("/", "_").replace("\\", "_")


def _make_nonstrict_report(step24_row, out_dir):
    key = row_key(step24_row)
    geometry_config = GeometryConfig.from_json(os.path.join(ROOT, step24_row["geometry_source"]))
    nonstrict_config = replace(geometry_config, quality_check_enabled=True, quality_check_strict=False)
    report = analyze_geometry_config(nonstrict_config)
    gate = GeometryQualityGate(strict=False).evaluate(report)
    payload = {"report": report, "gate": gate}
    path = os.path.join(out_dir, "nonstrict_reports", f"{_safe_key_text(key)}_geometry_quality_report.json")
    write_json(path, payload)
    return path, payload


def _compare_reports(step24_rows, step23_rows, out_dir):
    step23_by_key = {row_key(row): row for row in step23_rows}
    rows = []
    for step24_row in step24_rows:
        key = row_key(step24_row)
        strict_path = os.path.join(ROOT, step24_row["quality_report_path"])
        strict_payload = read_json(strict_path)
        comparison_source = "step23_report"
        if key in step23_by_key:
            nonstrict_path = os.path.join(ROOT, step23_by_key[key]["quality_report_path"])
            nonstrict_payload = read_json(nonstrict_path)
        else:
            comparison_source = "qa_only_nonstrict_report"
            nonstrict_path, nonstrict_payload = _make_nonstrict_report(step24_row, out_dir)

        row = _comparison_row(
            key,
            comparison_source,
            strict_path,
            strict_payload,
            nonstrict_path,
            nonstrict_payload,
        )
        _assert_comparison_row(row)
        rows.append(row)
    rows.sort(key=lambda item: (int(item["n_grid"]), item["case"], item["reaction_transfer_mode"]))
    return rows


def _comparison_row(key, comparison_source, strict_path, strict_payload, nonstrict_path, nonstrict_payload):
    strict_report = strict_payload["report"]
    strict_gate = strict_payload["gate"]
    nonstrict_report = nonstrict_payload["report"]
    nonstrict_gate = nonstrict_payload["gate"]

    mesh_counts_match = True
    voxel_counts_match = True
    if strict_report.get("geometry_type") == "mesh":
        mesh_counts_match = all(
            int(strict_report.get(name, 0)) == int(nonstrict_report.get(name, 0))
            for name in ("vertices_count", "faces_count", "boundary_edge_count", "degenerate_face_count", "nonmanifold_edge_count")
        )
    if strict_report.get("geometry_type") == "voxel":
        voxel_counts_match = (
            int(strict_report.get("occupied_count", 0)) == int(nonstrict_report.get("occupied_count", 0))
            and int(strict_report.get("connected_component_count", 0))
            == int(nonstrict_report.get("connected_component_count", 0))
            and float(strict_report.get("largest_component_fraction", 0.0))
            == float(nonstrict_report.get("largest_component_fraction", 0.0))
        )

    row = {
        "case": key[0],
        "mode": key[1],
        "reaction_transfer_mode": key[2],
        "n_grid": key[3],
        "comparison_source": comparison_source,
        "strict_report_path": _relative_path(strict_path),
        "nonstrict_report_path": _relative_path(nonstrict_path),
        "same_quality_kind": strict_report.get("quality_kind", "") == nonstrict_report.get("quality_kind", ""),
        "same_geometry_type": strict_report.get("geometry_type", "") == nonstrict_report.get("geometry_type", ""),
        "same_pass": bool(strict_gate.get("pass", False)) == bool(nonstrict_gate.get("pass", False)),
        "same_severity": strict_gate.get("severity", "") == nonstrict_gate.get("severity", ""),
        "strict_reasons_count": len(strict_gate.get("reasons", [])),
        "nonstrict_reasons_count": len(nonstrict_gate.get("reasons", [])),
        "strict_warnings_count": len(strict_gate.get("warnings", [])),
        "nonstrict_warnings_count": len(nonstrict_gate.get("warnings", [])),
        "mesh_counts_match": bool(mesh_counts_match),
        "voxel_counts_match": bool(voxel_counts_match),
        "reports_match": True,
        "notes": "strict mode changes gate policy only for good synthetic imported geometry",
    }
    row["reports_match"] = bool(
        row["same_quality_kind"]
        and row["same_geometry_type"]
        and row["same_pass"]
        and row["same_severity"]
        and int(row["strict_reasons_count"]) == 0
        and int(row["nonstrict_reasons_count"]) == 0
        and int(row["strict_warnings_count"]) == 0
        and int(row["nonstrict_warnings_count"]) == 0
        and row["mesh_counts_match"]
        and row["voxel_counts_match"]
        and strict_gate.get("strict") is True
        and nonstrict_gate.get("strict") is False
        and strict_gate.get("severity") == "ok"
        and nonstrict_gate.get("severity") == "ok"
    )
    return row


def _assert_comparison_row(row):
    if row["reports_match"] is not True:
        raise RuntimeError(f"strict/non-strict quality reports diverged: {row}")


def _summary(rows):
    return {
        "row_count": len(rows),
        "reports_match_count": sum(1 for row in rows if row["reports_match"]),
        "step23_report_count": sum(1 for row in rows if row["comparison_source"] == "step23_report"),
        "qa_only_nonstrict_report_count": sum(
            1 for row in rows if row["comparison_source"] == "qa_only_nonstrict_report"
        ),
    }


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step24_strict_non_strict_report_comparison")
    os.makedirs(out_dir, exist_ok=True)
    rows = _compare_reports(_load_rows(STEP24_CSVS), _load_rows(STEP23_CSVS), out_dir)
    summary = _summary(rows)
    if summary["row_count"] != 9 or summary["reports_match_count"] != 9:
        raise RuntimeError(f"strict/non-strict report comparison failed: {summary}")
    if summary["step23_report_count"] < 7:
        raise RuntimeError(f"expected at least 7 Step 23 report comparisons: {summary}")

    save_csv_rows(
        rows,
        os.path.join(out_dir, "strict_non_strict_report_comparison.csv"),
        fieldnames=COMPARISON_FIELDS,
    )
    write_json(os.path.join(out_dir, "strict_non_strict_report_comparison.json"), summary)

    marker = "[OK] Step 24 strict vs non-strict report comparison finished"
    write_log(
        "logs/step24_strict_non_strict_report_comparison.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"reports_match_count={summary['reports_match_count']}",
            f"step23_report_count={summary['step23_report_count']}",
            f"qa_only_nonstrict_report_count={summary['qa_only_nonstrict_report_count']}",
        ],
    )
    print("Step 24 strict vs non-strict report comparison")
    print(f"row_count={summary['row_count']}")
    print(f"reports_match_count={summary['reports_match_count']}")
    print(f"step23_report_count={summary['step23_report_count']}")
    print(f"qa_only_nonstrict_report_count={summary['qa_only_nonstrict_report_count']}")
    print(marker)


if __name__ == "__main__":
    main()
