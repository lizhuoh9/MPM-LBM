import os

from step47_common import ROOT, STEP47_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_envelope import run_short_step_envelope_matrix, summarize_short_step_envelope_matrix, write_short_step_envelope_rows

    rows = run_short_step_envelope_matrix(STEP47_CONFIG_PATH)
    summary = summarize_short_step_envelope_matrix(rows)
    if not summary["matrix_pass"]:
        raise RuntimeError(f"Step 47 short-step envelope matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step47_short_step_envelope_matrix"
    write_short_step_envelope_rows(
        rows,
        out_dir / "short_step_envelope_matrix.csv",
        out_dir / "short_step_envelope_matrix.json",
        out_dir / "short_step_envelope_matrix.npz",
        summary,
    )
    marker = "[OK] Step 47 short-step envelope matrix finished"
    write_log("logs/step47_short_step_envelope_matrix.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
