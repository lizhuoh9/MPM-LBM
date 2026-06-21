import os

from step50_common import ROOT, STEP50_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_envelope import run_one_cycle_envelope_matrix, summarize_one_cycle_envelope_matrix, write_one_cycle_envelope_rows

    rows = run_one_cycle_envelope_matrix(STEP50_CONFIG_PATH)
    summary = summarize_one_cycle_envelope_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 50 one-cycle envelope matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_one_cycle_envelope_matrix"
    write_one_cycle_envelope_rows(
        rows,
        out_dir / "one_cycle_envelope_matrix.csv",
        out_dir / "one_cycle_envelope_matrix.json",
        out_dir / "one_cycle_envelope_matrix.npz",
        summary,
    )
    marker = "[OK] Step 50 one-cycle envelope matrix finished"
    write_log("logs/step50_one_cycle_envelope_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
