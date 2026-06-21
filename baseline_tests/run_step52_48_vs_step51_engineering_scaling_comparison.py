import os

from step52_common import ROOT, feasibility_rows, read_json, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_48_feasibility_diagnostics import compare_48_vs_step51_engineering

    step51_rows = read_json("outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json")["rows"]
    step52_rows = feasibility_rows()
    artifact_ratio = matrix_artifact_size_ratio()
    comparison_rows, summary = compare_48_vs_step51_engineering(step51_rows, step52_rows, artifact_ratio)
    if not summary["scaling_pass"]:
        raise RuntimeError(f"Step 52 48 vs Step 51 engineering scaling comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_48_vs_step51_engineering_scaling_comparison"
    write_csv_rows(out_dir / "scaling_comparison.csv", comparison_rows)
    write_json(out_dir / "scaling_comparison.json", {"summary": summary, "rows": comparison_rows})
    marker = "[OK] Step 52 48 vs Step 51 engineering scaling comparison finished"
    write_log("logs/step52_48_vs_step51_engineering_scaling_comparison.log", [marker, f"scaling_pass={summary['scaling_pass']}", f"active_cell_ratio={summary['active_cell_count_ratio_48_vs_32']}"])
    print(marker)


def matrix_artifact_size_ratio() -> float:
    step51 = ROOT / "outputs" / "step51_transfer_comparison_matrix" / "transfer_comparison_matrix.json"
    step52 = ROOT / "outputs" / "step52_48_feasibility_matrix" / "feasibility_matrix.json"
    if not step51.is_file() or not step52.is_file() or step51.stat().st_size == 0:
        return 1.0
    return float(step52.stat().st_size) / float(step51.stat().st_size)


if __name__ == "__main__":
    main()
