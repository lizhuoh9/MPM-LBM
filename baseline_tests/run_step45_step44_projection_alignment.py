import os

from step45_common import ROOT, STEP45_CONFIG_PATH, read_json, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection import compute_runtime_projection_rows
    from src.runtime_geometry_projection_consistency import compare_step44_projection_smoke, summarize_step44_projection_alignment

    step44_rows = read_json("outputs/step44_projection_only_smoke/projection_only_smoke.json")["rows"]
    step45_rows = compute_runtime_projection_rows(STEP45_CONFIG_PATH)
    rows = compare_step44_projection_smoke(step44_rows, step45_rows)
    summary = summarize_step44_projection_alignment(rows)
    if not summary["alignment_pass"]:
        raise RuntimeError(f"Step 45 Step 44 projection alignment failed: {summary}")
    out_dir = ROOT / "outputs" / "step45_step44_projection_alignment"
    write_csv_rows(out_dir / "step44_projection_alignment.csv", rows)
    write_json(out_dir / "step44_projection_alignment.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 45 Step 44 projection alignment finished"
    write_log("logs/step45_step44_projection_alignment.log", [marker, f"row_count={summary['row_count']}", f"alignment_pass={summary['alignment_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
