from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step112_output_guard_blocks_synthetic_replay_and_overclaims():
    report = read_json(ROOT / "outputs" / "step112_output_guard" / "output_guard_report.json")
    summary = report["summary"]
    assert summary["output_guard_pass"] is True
    assert summary["all_candidate_curves_real_solver"] is True
    assert summary["real_driver_run_called_count"] >= summary["successful_real_rows"]
    assert summary["real_monitor_source_count"] == summary["successful_real_rows"]
    assert summary["synthetic_candidate_curve_count"] == 0
    assert summary["proxy_curve_replay_evidence_mode_count"] == 0
    assert summary["solver_curve_generated_from_reference_count"] == 0
    assert summary["reference_curve_used_only_for_error_metrics"] is True
    assert summary["validation_claim_count"] == 0
    assert summary["direct_equivalence_claim_count"] == 0
    assert summary["official_case_file_count"] == 0
    assert summary["official_mesh_file_count"] == 0
    assert summary["official_journal_file_count"] == 0
    assert summary["official_case_data_h5_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
