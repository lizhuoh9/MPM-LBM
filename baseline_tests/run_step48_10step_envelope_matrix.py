import os

from step48_common import ROOT, STEP48_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_10step_envelope import run_ten_step_envelope_matrix, summarize_ten_step_envelope_matrix, write_ten_step_envelope_rows

    rows = run_ten_step_envelope_matrix(STEP48_CONFIG_PATH)
    summary = summarize_ten_step_envelope_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 48 ten-step envelope matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step48_10step_envelope_matrix"
    write_ten_step_envelope_rows(
        rows,
        out_dir / "ten_step_envelope_matrix.csv",
        out_dir / "ten_step_envelope_matrix.json",
        out_dir / "ten_step_envelope_matrix.npz",
        summary,
    )
    marker = "[OK] Step 48 10-step envelope matrix finished"
    write_log("logs/step48_10step_envelope_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
