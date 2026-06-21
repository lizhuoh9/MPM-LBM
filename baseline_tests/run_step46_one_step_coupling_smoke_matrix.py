import os

from step46_common import ROOT, STEP46_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_coupling import run_coupling_smoke_matrix, summarize_coupling_smoke_matrix, write_coupling_smoke_rows

    rows = run_coupling_smoke_matrix(STEP46_CONFIG_PATH)
    summary = summarize_coupling_smoke_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 46 one-step coupling smoke matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step46_one_step_coupling_smoke_matrix"
    write_coupling_smoke_rows(
        rows,
        out_dir / "one_step_coupling_smoke_matrix.csv",
        out_dir / "one_step_coupling_smoke_matrix.json",
        out_dir / "one_step_coupling_smoke_matrix.npz",
        summary,
    )
    marker = "[OK] Step 46 one-step coupling smoke matrix finished"
    write_log("logs/step46_one_step_coupling_smoke_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
