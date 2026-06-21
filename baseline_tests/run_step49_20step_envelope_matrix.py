import os

from step49_common import ROOT, STEP49_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_envelope import run_twenty_step_envelope_matrix, summarize_twenty_step_envelope_matrix, write_twenty_step_envelope_rows

    rows = run_twenty_step_envelope_matrix(STEP49_CONFIG_PATH)
    summary = summarize_twenty_step_envelope_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 49 twenty-step envelope matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_20step_envelope_matrix"
    write_twenty_step_envelope_rows(
        rows,
        out_dir / "twenty_step_envelope_matrix.csv",
        out_dir / "twenty_step_envelope_matrix.json",
        out_dir / "twenty_step_envelope_matrix.npz",
        summary,
    )
    marker = "[OK] Step 49 20-step envelope matrix finished"
    write_log("logs/step49_20step_envelope_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
