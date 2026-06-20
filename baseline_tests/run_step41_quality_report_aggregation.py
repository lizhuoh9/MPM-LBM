import os

from step41_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = [
    "case",
    "mode_class",
    "reaction_transfer_mode",
    "geometry_type",
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
    rows = collect_reports()
    summary = summarize(rows)
    assert_summary(summary)

    out_dir = ROOT / "outputs" / "step41_quality_report_aggregation"
    write_csv_rows(out_dir / "quality_report_summary.csv", rows, FIELDS)
    write_json(out_dir / "quality_report_summary.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 41 quality report aggregation finished"
    write_log("logs/step41_quality_report_aggregation.log", [marker, f"quality_report_count={summary['quality_report_count']}"])
    print(f"quality_report_count={summary['quality_report_count']}")
    print(marker)


def collect_reports():
    root_path = ROOT / "outputs" / "step41_64_selected_parameter_driver"
    if not root_path.is_dir():
        raise RuntimeError(f"missing Step 41 driver output root: {root_path}")
    rows = []
    for dirpath, _, filenames in os.walk(root_path):
        if "geometry_quality_report.json" not in filenames:
            continue
        rows.append(row_from_report(os.path.join(dirpath, "geometry_quality_report.json")))
    rows.sort(key=lambda row: row["source_report_path"])
    return rows


def row_from_report(report_path):
    payload = read_json_path(report_path)
    report = payload["report"]
    gate = payload["gate"]
    case = os.path.basename(os.path.dirname(report_path))
    row = {
        "case": case,
        "mode_class": "experimental" if case.startswith("step41_64_experimental") else "static",
        "reaction_transfer_mode": "link_area_experimental" if "link_area" in case else "engineering",
        "geometry_type": report.get("geometry_type", ""),
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
        "source_report_path": relative_path(report_path),
    }
    if row["geometry_type"] != "squid_proxy" or row["quality_kind"] != "procedural_voxelized":
        raise RuntimeError(f"Step 41 quality report must be procedural squid proxy quality: {row}")
    return row


def summarize(rows):
    return {
        "quality_report_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "strict_count": sum(1 for row in rows if row["strict"]),
        "warning_count": sum(1 for row in rows if int(row["warnings_count"]) > 0 or row["severity"] == "warning"),
        "error_count": sum(1 for row in rows if row["severity"] == "error"),
        "static_report_count": sum(1 for row in rows if row["mode_class"] == "static"),
        "experimental_report_count": sum(1 for row in rows if row["mode_class"] == "experimental"),
    }


def assert_summary(summary):
    if int(summary["quality_report_count"]) != 4:
        raise RuntimeError(f"expected 4 Step 41 quality reports: {summary}")
    if int(summary["pass_count"]) != 4 or int(summary["strict_count"]) != 4:
        raise RuntimeError(f"all Step 41 quality reports must pass strict gates: {summary}")
    if int(summary["warning_count"]) != 0 or int(summary["error_count"]) != 0:
        raise RuntimeError(f"Step 41 quality reports contain warnings/errors: {summary}")
    if int(summary["static_report_count"]) != 2 or int(summary["experimental_report_count"]) != 2:
        raise RuntimeError(f"Step 41 quality report mode split is wrong: {summary}")


def read_json_path(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


if __name__ == "__main__":
    main()
