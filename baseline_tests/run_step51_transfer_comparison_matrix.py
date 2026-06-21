import os

from step51_common import ROOT, STEP51_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_envelope import (
        run_transfer_comparison_matrix,
        summarize_transfer_comparison_matrix,
        write_transfer_envelope_outputs,
    )

    rows = run_transfer_comparison_matrix(STEP51_CONFIG_PATH)
    summary = summarize_transfer_comparison_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 51 transfer comparison matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_transfer_comparison_matrix"
    write_transfer_envelope_outputs(
        rows,
        out_dir / "transfer_comparison_matrix.csv",
        out_dir / "transfer_comparison_matrix.json",
        out_dir / "transfer_comparison_matrix.npz",
        summary,
    )
    marker = "[OK] Step 51 transfer comparison matrix finished"
    write_log("logs/step51_transfer_comparison_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
