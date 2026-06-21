import os

from step44_common import STEP44_CONFIG_PATH, ROOT, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_update_config import (
        DiagnosticGeometryUpdateConfig,
        summarize_diagnostic_geometry_update_config_validation,
        validate_diagnostic_geometry_update_config,
    )

    config = DiagnosticGeometryUpdateConfig.from_json(STEP44_CONFIG_PATH)
    rows = validate_diagnostic_geometry_update_config(config, root=ROOT)
    summary = summarize_diagnostic_geometry_update_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 44 diagnostic update config validation failed: {rows}")
    out_dir = ROOT / "outputs" / "step44_diagnostic_update_config_validation"
    write_csv_rows(out_dir / "diagnostic_update_config_validation.csv", rows)
    write_csv_rows(out_dir / "diagnostic_update_config_validation_summary.csv", summary_rows(summary))
    write_json(out_dir / "diagnostic_update_config_validation.json", {"summary": summary, "rows": rows, "config": config.to_dict()})
    marker = "[OK] Step 44 diagnostic update config validation finished"
    write_log("logs/step44_diagnostic_update_config_validation.log", [marker, f"row_count={summary['row_count']}", f"validation_pass={summary['validation_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
