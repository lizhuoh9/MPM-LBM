import os

from step45_common import ROOT, STEP45_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection import compute_runtime_projection_rows, summarize_runtime_projection_rows, write_runtime_projection_rows
    from src.runtime_geometry_projection_config import RuntimeGeometryProjectionIntegrationConfig

    config = RuntimeGeometryProjectionIntegrationConfig.from_json(STEP45_CONFIG_PATH)
    rows = compute_runtime_projection_rows(STEP45_CONFIG_PATH)
    summary = summarize_runtime_projection_rows(rows, config)
    if not summary["runtime_projection_integration_pass"]:
        raise RuntimeError(f"Step 45 runtime projection integration failed: {summary}")
    out_dir = ROOT / "outputs" / "step45_runtime_projection_integration"
    write_runtime_projection_rows(rows, out_dir / "runtime_projection_integration.csv", out_dir / "runtime_projection_integration.json", summary)
    marker = "[OK] Step 45 runtime projection integration finished"
    write_log("logs/step45_runtime_projection_integration.log", [marker, f"row_count={summary['row_count']}", f"projection_pass_count={summary['projection_pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
