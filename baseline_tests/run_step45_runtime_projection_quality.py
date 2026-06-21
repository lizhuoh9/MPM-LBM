import os

from step45_common import ROOT, STEP45_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection import compute_runtime_projection_rows
    from src.runtime_geometry_projection_config import RuntimeGeometryProjectionIntegrationConfig
    from src.runtime_geometry_projection_quality import analyze_runtime_projection_quality

    config = RuntimeGeometryProjectionIntegrationConfig.from_json(STEP45_CONFIG_PATH)
    rows = compute_runtime_projection_rows(STEP45_CONFIG_PATH)
    summary = analyze_runtime_projection_quality(rows, config)
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 45 runtime projection quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step45_runtime_projection_quality"
    write_csv_rows(out_dir / "runtime_projection_quality.csv", summary_rows(summary))
    write_json(out_dir / "runtime_projection_quality.json", {"summary": summary, "rows": summary_rows(summary)})
    marker = "[OK] Step 45 runtime projection quality finished"
    write_log("logs/step45_runtime_projection_quality.log", [marker, f"row_count={summary['row_count']}", f"quality_pass={summary['quality_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
