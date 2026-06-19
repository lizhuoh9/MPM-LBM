import os

from step26_common import ROOT, write_csv_rows, write_json, write_log
from src.real_geometry_feasibility import compare_step25_projection_smoke


FIELDS = [
    "candidate_id",
    "geometry_type",
    "projected_mass_delta",
    "active_cell_count_delta",
    "solid_phi_min_delta",
    "solid_phi_max_delta",
    "projection_pass_both",
    "regression_pass",
]


def main():
    os.chdir(ROOT)
    result = compare_step25_projection_smoke(
        "outputs/step25_projection_smoke/projection_smoke_results.csv",
        "outputs/step26_projection_scale_diagnostics/projection_scale_results.csv",
    )
    if int(result["compared_row_count"]) != 2 or int(result["pass_count"]) != 2:
        raise RuntimeError(f"Step 25 projection regression failed: {result}")

    out_dir = ROOT / "outputs" / "step26_step25_projection_regression"
    write_csv_rows(out_dir / "step25_projection_regression.csv", result["rows"], FIELDS)
    write_json(out_dir / "step25_projection_regression.json", result)
    marker = "[OK] Step 26 Step 25 projection regression finished"
    write_log(
        "logs/step26_step25_projection_regression.log",
        [marker, f"compared_row_count={result['compared_row_count']}", f"pass_count={result['pass_count']}"],
    )
    print(f"compared_row_count={result['compared_row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
