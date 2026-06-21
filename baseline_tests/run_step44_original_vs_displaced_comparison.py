import os

from step44_common import STEP44_CONFIG_PATH, ROOT, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_update import compute_runtime_displaced_copy_rows, original_vs_displaced_rows, summarize_original_vs_displaced

    runtime = compute_runtime_displaced_copy_rows(STEP44_CONFIG_PATH)
    rows = original_vs_displaced_rows(runtime)
    summary = summarize_original_vs_displaced(rows)
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 44 original-vs-displaced comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_original_vs_displaced_comparison"
    write_csv_rows(out_dir / "original_vs_displaced.csv", rows)
    write_json(out_dir / "original_vs_displaced.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 44 original-vs-displaced comparison finished"
    write_log("logs/step44_original_vs_displaced_comparison.log", [marker, f"row_count={summary['row_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
