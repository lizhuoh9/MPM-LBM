import os

from step44_common import STEP44_CONFIG_PATH, ROOT, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_update import compute_runtime_displaced_copy_rows, summarize_runtime_displaced_copy_rows, write_runtime_copy_rows
    from src.diagnostic_geometry_update_config import DiagnosticGeometryUpdateConfig

    config = DiagnosticGeometryUpdateConfig.from_json(STEP44_CONFIG_PATH)
    rows = compute_runtime_displaced_copy_rows(STEP44_CONFIG_PATH)
    summary = summarize_runtime_displaced_copy_rows(rows, config)
    if not summary["runtime_copy_pass"]:
        raise RuntimeError(f"Step 44 runtime displaced copy failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_runtime_displaced_copy"
    write_runtime_copy_rows(rows, out_dir / "runtime_displaced_copy.csv", out_dir / "runtime_displaced_copy.json", summary)
    marker = "[OK] Step 44 runtime displaced copy finished"
    write_log("logs/step44_runtime_displaced_copy.log", [marker, f"row_count={summary['row_count']}", f"runtime_copy_pass={summary['runtime_copy_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
