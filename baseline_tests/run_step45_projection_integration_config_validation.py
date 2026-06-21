import os

from step45_common import ROOT, STEP45_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection_config import (
        RuntimeGeometryProjectionIntegrationConfig,
        summarize_runtime_geometry_projection_config_validation,
        validate_runtime_geometry_projection_config,
    )

    config = RuntimeGeometryProjectionIntegrationConfig.from_json(STEP45_CONFIG_PATH)
    rows = validate_runtime_geometry_projection_config(config, root=ROOT)
    summary = summarize_runtime_geometry_projection_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 45 projection integration config validation failed: {rows}")
    out_dir = ROOT / "outputs" / "step45_projection_integration_config_validation"
    write_csv_rows(out_dir / "projection_integration_config_validation.csv", rows)
    write_json(out_dir / "projection_integration_config_validation.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "projection_integration_config_summary.csv", summary_rows(summary))
    marker = "[OK] Step 45 projection integration config validation finished"
    write_log("logs/step45_projection_integration_config_validation.log", [marker, f"row_count={summary['row_count']}", f"validation_pass={summary['validation_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
