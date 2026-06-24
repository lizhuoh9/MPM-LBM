import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP103_ROW = "fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke"


def test_step103_fluent_inspired_duct_flap_proxy_smoke_matrix_passes():
    payload = read_json(
        "outputs/step103_smoke_matrix/"
        "fluent_inspired_duct_flap_proxy_smoke_matrix.json"
    )
    summary = payload["summary"]
    row = payload["rows"][0]

    assert summary["step103_fluent_inspired_duct_flap_proxy_smoke_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["required_stable_count"] == 1
    assert summary["driver_run_called_count"] == 1
    assert summary["legacy_driver_module_used_count"] == 0
    assert summary["duct_flap_proxy_enabled_count"] == 1
    assert summary["grid_48_enabled_count"] == 1
    assert summary["ggui_screenshot_count"] == 1
    assert summary["ggui_video_file_count"] == 0
    assert summary["vtr_output_count"] == 0
    assert summary["particle_npy_output_count"] == 0
    assert summary["has_nan_count"] == 0
    assert summary["has_inf_count"] == 0
    assert summary["min_completed_lbm_steps"] == 5
    assert summary["min_diagnostics_row_count"] >= 6
    assert summary["runtime_code_changed"] is True
    assert summary["solver_formula_changed"] is False

    assert row["row_name"] == STEP103_ROW
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geometry_type"] == "duct_flap_proxy"
    assert row["geometry_config_path"] == "configs/step103_fluent_inspired_duct_flap_proxy_geometry_1024.json"
    assert row["duct_flap_proxy_enabled"] is True
    assert row["official_mesh_imported"] is False
    assert row["official_fluent_files_used_as_runtime_input"] is False
    assert row["n_grid"] == 48
    assert row["n_particles"] == 1024
    assert row["n_lbm_steps"] == 5
    assert row["mpm_substeps_per_lbm_step"] == 1
    assert row["completed_lbm_steps"] == 5
    assert row["diagnostics_row_count"] >= 6
    assert row["has_nan"] is False
    assert row["has_inf"] is False
    assert row["stable"] is True
    assert row["geometry_quality_report_exists"] is True
    assert row["geometry_quality_report_pass"] is True
    assert row["fluent_inspired_geometry_ratios_recorded"] is True
    assert row["ggui_screenshot_exists"] is True
    assert row["ggui_screenshot_file_count"] == 1
    assert row["ggui_render_report_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
