import os

from step52_common import ROOT, STEP52_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_48_feasibility_envelope import (
        run_48_feasibility_matrix,
        summarize_48_feasibility_matrix,
        write_48_feasibility_rows,
    )

    rows = run_48_feasibility_matrix(STEP52_CONFIG_PATH)
    summary = summarize_48_feasibility_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 52 48 feasibility matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_48_feasibility_matrix"
    write_48_feasibility_rows(
        rows,
        out_dir / "feasibility_matrix.csv",
        out_dir / "feasibility_matrix.json",
        out_dir / "feasibility_matrix.npz",
        summary,
    )
    marker = "[OK] Step 52 48 feasibility matrix finished"
    write_log("logs/step52_48_feasibility_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
