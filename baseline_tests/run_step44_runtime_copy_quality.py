import os

from step44_common import STEP44_CONFIG_PATH, ROOT, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_update import compute_runtime_displaced_copy_rows, runtime_copy_quality_summary
    from src.diagnostic_geometry_update_config import DiagnosticGeometryUpdateConfig

    config = DiagnosticGeometryUpdateConfig.from_json(STEP44_CONFIG_PATH)
    rows = compute_runtime_displaced_copy_rows(STEP44_CONFIG_PATH)
    summary = runtime_copy_quality_summary(rows, config)
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 44 runtime copy quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_runtime_copy_quality"
    write_csv_rows(out_dir / "runtime_copy_quality.csv", summary_rows(summary))
    write_json(out_dir / "runtime_copy_quality.json", {"summary": summary})
    marker = "[OK] Step 44 runtime copy quality finished"
    write_log("logs/step44_runtime_copy_quality.log", [marker, f"row_count={summary['row_count']}", f"quality_pass={summary['quality_pass']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
