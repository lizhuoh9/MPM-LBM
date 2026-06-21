import os

from step45_common import ROOT, STEP45_CONFIG_PATH, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection import compute_original_projection_rows, compute_runtime_projection_rows
    from src.runtime_geometry_projection_consistency import compare_original_vs_runtime_projection, summarize_original_vs_runtime_projection

    original_rows = compute_original_projection_rows(STEP45_CONFIG_PATH)
    runtime_rows = compute_runtime_projection_rows(STEP45_CONFIG_PATH)
    rows = compare_original_vs_runtime_projection(original_rows, runtime_rows)
    summary = summarize_original_vs_runtime_projection(rows)
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 45 original-vs-runtime projection comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step45_original_vs_runtime_projection_comparison"
    write_csv_rows(out_dir / "original_vs_runtime_projection.csv", rows)
    write_json(out_dir / "original_vs_runtime_projection.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 45 original-vs-runtime projection comparison finished"
    write_log("logs/step45_original_vs_runtime_projection_comparison.log", [marker, f"row_count={summary['row_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
