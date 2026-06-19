import os

from step24_common import ROOT, STEP24_CONFIGS, STEP24_OUTPUT_ROOTS, read_json, write_json, write_log
from src.artifact_utils import scan_artifacts, summarize_artifacts, write_artifact_manifest
from src.run_utils import save_csv_rows


def _check_driver_configs_disable_heavy_outputs():
    for relative_path in STEP24_CONFIGS:
        data = read_json(relative_path)
        if data.get("quality_check_enabled") is not True:
            raise RuntimeError(f"{relative_path} must enable quality_check_enabled")
        if data.get("quality_check_strict") is not True:
            raise RuntimeError(f"{relative_path} must enable quality_check_strict")
        if data.get("write_vtk") is not False or data.get("write_particles") is not False:
            raise RuntimeError(f"{relative_path} must disable heavy outputs")


def _step24_output_rows(rows):
    return [row for row in rows if row["path"].startswith("outputs/step24") or row["path"].startswith("logs/step24")]


def _is_driver_quality_report(path):
    return any(path.startswith(root + "/") for root in STEP24_OUTPUT_ROOTS) and path.endswith(
        "geometry_quality_report.json"
    )


def _check_step24_outputs(rows):
    step24_rows = _step24_output_rows(rows)
    if not step24_rows:
        raise RuntimeError("artifact manifest found no Step 24 outputs")

    quality_report_rows = [row for row in step24_rows if _is_driver_quality_report(row["path"])]
    if len(quality_report_rows) != 9:
        raise RuntimeError(f"expected 9 Step 24 quality reports, got {len(quality_report_rows)}")
    for row in quality_report_rows:
        if int(row["size_bytes"]) >= 100_000:
            raise RuntimeError(f"Step 24 quality report too large: {row}")

    offenders = []
    for row in step24_rows:
        path = row["path"]
        if path.endswith(".vtr"):
            offenders.append(path)
        if path.endswith(".npy") and "particle" in path.lower():
            offenders.append(path)
    if offenders:
        raise RuntimeError(f"Step 24 wrote forbidden heavy outputs: {offenders}")

    total_size_bytes = sum(int(row["size_bytes"]) for row in step24_rows)
    if total_size_bytes >= 25 * 1024 * 1024:
        raise RuntimeError(f"Step 24 output total size exceeds 25 MB: {total_size_bytes}")
    return {
        "step24_file_count": len(step24_rows),
        "step24_total_size_bytes": int(total_size_bytes),
        "step24_total_size_mb": total_size_bytes / 1024.0 / 1024.0,
        "step24_quality_report_count": len(quality_report_rows),
    }


def _summary_rows(summary):
    rows = []
    for key, value in summary.items():
        if key == "by_extension":
            continue
        rows.append({"metric": key, "value": value})
    for extension, value in summary.get("by_extension", {}).items():
        rows.append({"metric": f"by_extension:{extension}", "value": value})
    return rows


def main():
    os.chdir(ROOT)
    _check_driver_configs_disable_heavy_outputs()
    for root in STEP24_OUTPUT_ROOTS:
        if not os.path.isdir(os.path.join(ROOT, root)):
            raise RuntimeError(f"missing Step 24 output root: {root}")

    out_dir = os.path.join(ROOT, "outputs", "step24_artifact_manifest")
    os.makedirs(out_dir, exist_ok=True)

    rows = scan_artifacts(
        root_paths=[
            "logs",
            "outputs",
            "STEP*_REPORT.md",
            "STEP*_GOAL.md",
            "docs",
            "paper",
            "configs",
            "data/geometry_fixtures",
        ]
    )
    summary = summarize_artifacts(rows)
    step24_summary = _check_step24_outputs(rows)
    summary.update(step24_summary)
    if summary["file_count"] <= 0 or summary["total_size_bytes"] <= 0:
        raise RuntimeError("artifact manifest found no files")
    if summary["large_file_count"] != 0:
        raise RuntimeError("Step 24 artifact manifest found large files")
    if float(summary["total_size_mb"]) >= 150.0:
        raise RuntimeError(f"repository artifact summary exceeds 150 MB: {summary['total_size_mb']:.6f}")

    write_artifact_manifest(rows, os.path.join(out_dir, "artifact_manifest.csv"))
    save_csv_rows(_summary_rows(summary), os.path.join(out_dir, "artifact_summary.csv"), fieldnames=["metric", "value"])
    write_json(os.path.join(out_dir, "artifact_summary.json"), summary)

    marker = "[OK] Step 24 artifact manifest finished"
    write_log(
        "logs/step24_artifact_manifest.log",
        [
            marker,
            f"file_count={summary['file_count']}",
            f"total_size_mb={summary['total_size_mb']:.6f}",
            f"large_file_count={summary['large_file_count']}",
            f"step24_total_size_mb={summary['step24_total_size_mb']:.6f}",
            f"step24_quality_report_count={summary['step24_quality_report_count']}",
        ],
    )
    print("Step 24 artifact manifest")
    print(f"file_count={summary['file_count']}")
    print(f"total_size_mb={summary['total_size_mb']:.6f}")
    print(f"large_file_count={summary['large_file_count']}")
    print(f"step24_total_size_mb={summary['step24_total_size_mb']:.6f}")
    print(marker)


if __name__ == "__main__":
    main()
