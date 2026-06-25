import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "outputs/step119_lbm_boundary_repair_real_run_validation"

REQUIRED_ROWS = {
    "duct_only_48_legacy_boundary_500step_reference_real",
    "duct_only_48_regularized_boundary_500step_reference_real",
    "duct_only_48_regularized_limited_boundary_500step_real",
    "duct_only_48_convective_outlet_boundary_500step_real",
    "duct_only_96_regularized_limited_boundary_1000step_real",
    "duct_only_96_convective_outlet_boundary_1000step_real",
    "static_two_flap_96_best_boundary_1000step_real",
    "duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded_real",
}


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_step119_committed_artifacts_are_real_or_honestly_incomplete_and_claim_no_validation():
    solver = _read_json(OUTPUT_DIR / "solver_report.json")
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")
    comparison = _read_json(OUTPUT_DIR / "boundary_variant_real_run_comparison.json")
    first_failure = _read_json(OUTPUT_DIR / "first_failure_global_summary.json")
    limiter = _read_json(OUTPUT_DIR / "limiter_activation_summary.json")
    gate = _read_json(OUTPUT_DIR / "step119_gate_report.json")

    assert solver["step"] == 119
    assert solver["simulation_backed_artifacts"] in (True, False)
    assert solver["fluent_validation_claim_allowed"] is False
    assert solver["figure_29_3_parity_claim_allowed"] is False
    assert solver["full_fsi_rerun_done"] is False
    assert solver["validation_claim_allowed"] is False
    assert solver["step120_quasi2d_allowed"] is False
    assert solver["final_classification"] in {
        "boundary_repair_success_go_to_quasi2d",
        "boundary_repair_partial_continue_lbm",
        "boundary_repair_failed_revisit_lbm_solver",
    }
    assert matrix["step"] == 119
    assert REQUIRED_ROWS.issubset({row["name"] for row in matrix["runs"]})
    assert comparison["step"] == 119
    assert comparison["comparison_scope"] == "real non-synthetic Step119 LBM boundary repair validation"
    assert first_failure["step"] == 119
    assert limiter["step"] == 119
    assert gate["step"] == 119
    assert gate["quasi2d_allowed"] is False


def test_step119_row_artifacts_record_real_mode_gates_limiter_and_first_failure_location():
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")

    for row in matrix["runs"]:
        row_dir = OUTPUT_DIR / row["name"]
        finite = _read_json(row_dir / "finite_stability_report.json")
        metadata = _read_json(row_dir / "run_metadata.json")
        boundary = _read_json(row_dir / "duct_boundary_condition_report.json")
        first_failure = _read_json(row_dir / "first_failure_diagnostics.json")
        limiter = _read_json(row_dir / "limiter_activation_summary.json")

        assert metadata["step"] == 119
        assert metadata["fluent_validation_claim_allowed"] is False
        assert metadata["full_fsi_rerun_done"] is False
        assert metadata["validation_claim_allowed"] is False
        assert metadata["synthetic_diagnostic_mode"] is False
        assert boundary["validation_claim_allowed"] is False
        assert "open_boundary_limiter_enabled" in boundary
        assert "stability_timeseries_trend_summary" in finite
        assert "first_failure_detector" in finite
        assert "population_stats_final" in finite
        assert "limiter_activation_summary" in finite
        assert "first_failure_detector" in first_failure
        assert "first_failure_location" in first_failure
        assert "boundary_plane_where_failure_started" in first_failure
        assert "limiter_activation_count" in limiter
        assert "limiter_activation_fraction" in limiter

        if row["requested_window_completed"] is False:
            assert row["step119_validation_claimed"] is False
        else:
            assert row["steps_completed"] == row["requested_n_steps"]
            assert row["executed_nx"] == row["requested_nx"]


def test_step119_report_and_docs_keep_quasi2d_fsi_and_fluent_blocked_without_real_gates():
    report = (ROOT / "STEP119_LBM_BOUNDARY_REPAIR_REAL_RUN_VALIDATION_REPORT.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs/119_lbm_boundary_repair_real_run_validation.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for text in (report, docs):
        assert "Step119 quasi-2D remains blocked" in text
        assert "No Fluent validation is claimed" in text
        assert "No full FSI validation is claimed" in text
        assert "synthetic_diagnostic_mode=false" in text
    assert "Step 119 LBM boundary repair real-run validation" in readme
