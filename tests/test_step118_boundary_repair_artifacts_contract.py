import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "outputs/step118_lbm_open_boundary_stability_repair"

REQUIRED_ROWS = {
    "duct_only_48_legacy_boundary_500step_reference",
    "duct_only_48_regularized_boundary_500step_reference",
    "duct_only_48_regularized_limited_boundary_500step",
    "duct_only_48_convective_outlet_boundary_500step",
    "duct_only_96_regularized_limited_boundary_1000step",
    "duct_only_96_convective_outlet_boundary_1000step",
    "static_two_flap_96_best_boundary_1000step",
    "duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded",
}


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_step118_committed_artifacts_have_required_reports_rows_and_no_validation_claims():
    solver = _read_json(OUTPUT_DIR / "solver_report.json")
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")
    comparison = _read_json(OUTPUT_DIR / "boundary_variant_comparison.json")
    first_failure = _read_json(OUTPUT_DIR / "first_failure_diagnostics.json")

    assert solver["step"] == 118
    assert solver["fluent_validation_claim_allowed"] is False
    assert solver["figure_29_3_parity_claim_allowed"] is False
    assert solver["full_fsi_rerun_done"] is False
    assert solver["validation_claim_allowed"] is False
    assert solver["step119_quasi2d_allowed"] is False
    assert solver["final_classification"] in {
        "boundary_repair_success_go_to_quasi2d",
        "boundary_repair_partial_continue_lbm",
        "boundary_repair_failed_revisit_lbm_solver",
    }
    assert matrix["step"] == 118
    assert REQUIRED_ROWS.issubset({row["name"] for row in matrix["runs"]})
    assert comparison["step"] == 118
    assert "best_boundary_semantics" in comparison
    assert first_failure["step"] == 118


def test_step118_row_artifacts_record_stability_diagnostics_and_boundary_settings():
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")

    for row in matrix["runs"]:
        row_dir = OUTPUT_DIR / row["name"]
        finite = _read_json(row_dir / "finite_stability_report.json")
        metadata = _read_json(row_dir / "run_metadata.json")
        boundary = _read_json(row_dir / "duct_boundary_condition_report.json")
        first_failure = _read_json(row_dir / "first_failure_diagnostics.json")

        assert metadata["step"] == 118
        assert metadata["fluent_validation_claim_allowed"] is False
        assert metadata["full_fsi_rerun_done"] is False
        assert metadata["validation_claim_allowed"] is False
        assert boundary["validation_claim_allowed"] is False
        assert "open_boundary_limiter_enabled" in boundary
        assert "stability_timeseries_trend_summary" in finite
        assert "first_failure_detector" in finite
        assert "population_stats_final" in finite
        assert "first_failure_detector" in first_failure

        if row["requested_window_completed"] is False:
            assert row["step118_validation_claimed"] is False
        else:
            assert row["steps_completed"] == row["requested_n_steps"]
            assert row["executed_nx"] == row["requested_nx"]


def test_step118_report_and_docs_keep_quasi2d_and_fsi_blocked_until_boundary_gates_pass():
    report = (ROOT / "STEP118_LBM_OPEN_BOUNDARY_STABILITY_REPAIR_REPORT.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs/118_lbm_open_boundary_stability_repair.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for text in (report, docs):
        assert "Step119 quasi-2D remains blocked" in text
        assert "No Fluent validation is claimed" in text
        assert "No full FSI validation is claimed" in text
    assert "Step 118 LBM open-boundary stability repair" in readme
