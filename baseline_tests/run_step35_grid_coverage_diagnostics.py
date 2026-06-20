import os

from step35_common import ROOT, fieldnames_from_rows, write_csv_rows, write_json, write_log
from src.wall_velocity_field import generate_wall_velocity_field_rows


def main():
    os.chdir(ROOT)
    rows = generate_wall_velocity_field_rows("configs/step35_squid_proxy_wall_velocity_field.json")
    coverage_rows = build_coverage_rows(rows)
    summary = {
        "row_count": len(coverage_rows),
        "pass_count": sum(1 for row in coverage_rows if bool(row["coverage_pass"])),
        "coverage_pass": all(bool(row["coverage_pass"]) for row in coverage_rows),
        "active_cell_count_min": min(int(row["active_cell_count_min"]) for row in coverage_rows),
        "active_cell_count_max": max(int(row["active_cell_count_max"]) for row in coverage_rows),
    }
    if int(summary["row_count"]) != 9 or not bool(summary["coverage_pass"]):
        raise RuntimeError(f"Step 35 grid coverage diagnostics failed: {summary}")

    out_dir = ROOT / "outputs" / "step35_grid_coverage_diagnostics"
    write_csv_rows(out_dir / "grid_coverage_diagnostics.csv", coverage_rows, fieldnames_from_rows(coverage_rows))
    write_json(out_dir / "grid_coverage_diagnostics.json", {"summary": summary, "rows": coverage_rows})
    marker = "[OK] Step 35 grid coverage diagnostics finished"
    write_log(
        "logs/step35_grid_coverage_diagnostics.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"coverage_pass={summary['coverage_pass']}",
        ],
    )
    print(f"coverage_pass={summary['coverage_pass']}")
    print(marker)


def build_coverage_rows(rows: list[dict]) -> list[dict]:
    out = []
    for grid_size in sorted({int(row["grid_size"]) for row in rows}):
        for region_id in sorted({row["region_id"] for row in rows}):
            selected = [row for row in rows if int(row["grid_size"]) == grid_size and row["region_id"] == region_id]
            active_counts = [int(row["active_cell_count"]) for row in selected]
            nonzero_phase_count = sum(1 for row in selected if float(row["velocity_norm_max"]) > 0.0)
            coverage_pass = bool(selected) and min(active_counts) > 0 and nonzero_phase_count > 0
            out.append(
                {
                    "grid_size": grid_size,
                    "region_id": region_id,
                    "phase_count": len(selected),
                    "active_cell_count_min": min(active_counts) if active_counts else 0,
                    "active_cell_count_max": max(active_counts) if active_counts else 0,
                    "velocity_nonzero_phase_count": nonzero_phase_count,
                    "coverage_pass": coverage_pass,
                }
            )
    return out


if __name__ == "__main__":
    main()
