import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_32_probe_audit import build_canonical_driver_32_probe_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step61_32_probe_quality_passes_current_artifacts():
    rows, summary = build_canonical_driver_32_probe_audit(ROOT)
    assert summary["probe_32_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert int(summary["runtime_warning_count"]) >= 0
    assert all(row["pass"] is True for row in rows)
    assert all(row["n_grid"] == 32 for row in rows)
    assert all(row["n_particles"] == 1024 for row in rows)
    assert all(float(row["rho_min_min"]) > 0.9 for row in rows)
    assert all(float(row["rho_max_max"]) < 1.1 for row in rows)
    assert all(float(row["lbm_max_v_max"]) < 0.5 for row in rows)
    assert all(float(row["mpm_min_J_min"]) > 0.0 for row in rows)
    assert all(int(row["bb_link_count_max"]) > 0 for row in rows)


def test_step61_32_probe_quality_artifact_passes():
    payload = read_json("outputs/step61_32_probe_quality/probe_32_quality.json")
    summary = payload["summary"]
    assert summary["probe_32_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert int(summary["driver_run_called_count"]) == 1
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert all(row["pass"] is True for row in payload["rows"])


def test_step61_runtime_summary_is_recorded_as_soft_warning_only():
    payload = read_json("outputs/step61_32_probe_matrix/probe_32_matrix.json")
    summary = payload["summary"]
    assert float(summary["total_elapsed_seconds"]) > 0.0
    assert summary["slowest_row_name"] == "canonical_driver_moving_boundary_engineering_32_1step"
    assert float(summary["slowest_elapsed_seconds"]) > 0.0
    assert int(summary["runtime_warning_count"]) >= 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
