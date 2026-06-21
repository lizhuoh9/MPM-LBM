import os

from step44_common import ROOT, STEP44_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_projection import compute_projection_only_rows, summarize_projection_only_rows, write_projection_only_rows

    rows = compute_projection_only_rows(STEP44_CONFIG_PATH)
    summary = summarize_projection_only_rows(rows)
    if not summary["projection_smoke_pass"]:
        raise RuntimeError(f"Step 44 projection-only smoke failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_projection_only_smoke"
    write_projection_only_rows(rows, out_dir / "projection_only_smoke.csv", out_dir / "projection_only_smoke.json")
    marker = "[OK] Step 44 projection-only smoke finished"
    write_log("logs/step44_projection_only_smoke.log", [marker, f"row_count={summary['row_count']}", f"projection_pass_count={summary['projection_pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
