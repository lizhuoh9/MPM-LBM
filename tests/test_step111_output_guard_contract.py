from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step111_output_guard_blocks_synthetic_or_overclaim_paths():
    report = read_json(ROOT / "outputs" / "step111_output_guard" / "output_guard_report.json")
    summary = report["summary"]
    assert summary["output_guard_pass"] is True
    assert summary["synthetic_candidate_curve_count"] == 0
    assert summary["proxy_curve_replay_evidence_mode_count"] == 0
    assert summary["solver_curve_generated_from_reference_count"] == 0
    assert summary["real_driver_run_called_count"] == 1
    assert summary["real_lbm_preflow_run_called_count"] == 1
    assert summary["validation_claim_count"] == 0
    assert summary["direct_equivalence_claim_count"] == 0
    assert summary["official_case_file_count"] == 0
    assert summary["official_mesh_file_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step111_source_does_not_import_step110_curve_synthesis():
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src" / "mpm_lbm" / "evidence").glob("step111_*.py"))
    assert "synthesize_candidate_curve" not in source
    assert "step110_preflow_monitor_proxy_curve_replay" not in source
