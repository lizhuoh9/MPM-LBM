import os

from step35_common import ROOT, write_log
from src.wall_velocity_field import generate_wall_velocity_field_rows, summarize_wall_velocity_rows, write_wall_velocity_rows


def main():
    os.chdir(ROOT)
    rows = generate_wall_velocity_field_rows("configs/step35_squid_proxy_wall_velocity_field.json")
    summary = summarize_wall_velocity_rows(rows)
    assert_summary(summary, rows)
    out_dir = ROOT / "outputs" / "step35_wall_velocity_field"
    write_wall_velocity_rows(rows, out_dir / "wall_velocity_field.csv", out_dir / "wall_velocity_field.json", summary=summary)
    marker = "[OK] Step 35 generate wall velocity field finished"
    write_log(
        "logs/step35_generate_wall_velocity_field.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"max_velocity_norm={summary['max_velocity_norm']:.12g}",
            f"min_active_cell_count={summary['min_active_cell_count']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


def assert_summary(summary: dict, rows: list[dict]) -> None:
    if int(summary["row_count"]) != 63:
        raise RuntimeError(f"unexpected Step 35 wall velocity row count: {summary}")
    for key in ("finite_pass", "bounds_pass", "coverage_pass", "diagnostic_only_pass", "no_lbm_update_pass"):
        if not bool(summary[key]):
            raise RuntimeError(f"Step 35 wall velocity summary failed {key}: {summary}")
    if any(int(row["active_cell_count"]) <= 0 for row in rows):
        raise RuntimeError("Step 35 wall velocity row has zero active coverage")
    if any(bool(row["apply_to_lbm"]) or bool(row["lbm_population_update_enabled"]) for row in rows):
        raise RuntimeError("Step 35 wall velocity rows attempted LBM application")


if __name__ == "__main__":
    main()
