from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step111_real_lbm_preflow_report_contract():
    report = read_json(ROOT / "outputs" / "step111_real_lbm_preflow" / "preflow_report.json")
    summary = report["summary"]
    row = report["rows"][0]
    assert summary["preflow_pass"] is True
    assert row["preflow_source"] == "real_lbm_simulation"
    assert row["real_lbm_step_called"] is True
    assert row["completed_lbm_substeps"] == 6000
    assert row["restart_written"] is True
    assert row["restart_reload_arrays_match"] is True
    assert row["restart_metadata_matches_config"] is True
    assert Path(ROOT / row["restart_path"]).is_file()
    assert 0.019 <= row["inlet_plane_mean_ux_final"] <= 0.021
    assert row["mid_duct_plane_mean_ux_final"] > 0.0001
    assert row["outlet_plane_mean_ux_final"] > 0.0001
    assert row["rho_min_final"] > 0.9
    assert row["rho_max_final"] < 1.2
    assert row["has_nan"] is False
    assert row["has_inf"] is False
