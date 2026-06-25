import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "outputs/step117_regularized_lbm_long_window_fluid_validation"

REQUIRED_ROWS = {
    "duct_only_48_legacy_boundary_500step_full",
    "duct_only_48_regularized_boundary_500step_full",
    "duct_only_96_regularized_boundary_1000step_full",
    "static_two_flap_96_regularized_1000step_full",
    "duct_only_96_regularized_boundary_physical_nu_report_only_100step_guarded",
}


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_step117_committed_artifacts_have_required_reports_and_rows():
    solver = _read_json(OUTPUT_DIR / "solver_report.json")
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")
    comparison = _read_json(OUTPUT_DIR / "regularized_vs_legacy_comparison.json")
    surrogate = _read_json(OUTPUT_DIR / "reynolds_relaxed_surrogate_report.json")

    assert solver["step"] == 117
    assert solver["fluent_validation_claim_allowed"] is False
    assert solver["full_fsi_rerun_done"] is False
    assert solver["official_mesh_or_case_used"] is False
    assert matrix["step"] == 117
    assert REQUIRED_ROWS.issubset({row["name"] for row in matrix["runs"]})
    assert comparison["comparison_result"] in {
        "regularized_better_than_legacy_for_long_window",
        "regularized_comparable_but_not_better",
        "regularized_not_acceptable_for_long_window",
        "insufficient_completed_rows",
    }
    assert surrogate["target_reynolds_number"] == 26666.67
    assert surrogate["physical_reynolds_direct_simulation_feasible_with_current_lbm"] is False


def test_step117_committed_artifacts_do_not_hide_incomplete_rows_as_validation():
    solver = _read_json(OUTPUT_DIR / "solver_report.json")
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")
    incomplete = set(matrix["incomplete_required_rows"])

    for row in matrix["runs"]:
        row_dir = OUTPUT_DIR / row["name"]
        finite = _read_json(row_dir / "finite_stability_report.json")
        metadata = _read_json(row_dir / "run_metadata.json")
        boundary = _read_json(row_dir / "duct_boundary_condition_report.json")

        assert metadata["full_fsi_rerun_done"] is False
        assert metadata["fluent_validation_claim_allowed"] is False
        assert boundary["validation_claim_allowed"] is False
        assert "long_window_gates" in finite
        assert "timeseries_trend_summary" in finite

        if row["requested_window_completed"] is False:
            assert row["name"] in incomplete
            assert row["step117_validation_claimed"] is False
        else:
            assert row["steps_completed"] == row["requested_n_steps"]
            assert row["executed_nx"] == row["requested_nx"]

    if incomplete:
        assert solver["step118_quasi2d_allowed"] is False


def test_step117_static_flap_artifacts_remain_fluid_only():
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")
    static_rows = [row for row in matrix["runs"] if row["geometry_mode"] == "static_two_flap"]
    assert static_rows

    for row in static_rows:
        row_dir = OUTPUT_DIR / row["name"]
        metadata = _read_json(row_dir / "run_metadata.json")
        assert metadata["fluid_only"] is True
        assert metadata["full_fsi_rerun_done"] is False

        if row.get("profile_only") or row.get("skipped_due_to_tau_margin"):
            continue

        flap = _read_json(row_dir / "flap_region_flow_summary.json")
        throat = _read_json(row_dir / "throat_speed_summary.json")
        recirculation = _read_json(row_dir / "recirculation_proxy_summary.json")
        assert flap["static_flap_fluid_only"] is True
        assert throat["finite_pass"] in (True, False)
        assert recirculation["proxy_name"] == "negative_ux_fraction_near_flaps"
