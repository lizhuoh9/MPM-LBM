import json
from pathlib import Path

import pytest

from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig


ROOT = Path(__file__).resolve().parents[1]


def test_step110_preflow_restart_exists_and_reloads():
    config = read_json("configs/step110_proxy_preflow_48_low_mach.json")
    report = read_json("outputs/step110_proxy_preflow/preflow_report.json")
    reload_report = read_json("outputs/step110_proxy_preflow/restart_reload_report.json")

    assert config["n_grid"] == 48
    assert config["total_lbm_substeps"] == 6000
    assert config["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert report["summary"]["preflow_pass"] is True
    assert report["summary"]["preflow_completed_lbm_substeps"] == 6000
    assert 0.019 <= report["summary"]["inlet_plane_mean_ux_final"] <= 0.021
    assert report["summary"]["mid_duct_plane_mean_ux_final"] > 0.005
    assert report["summary"]["outlet_plane_mean_ux_final"] > 0.005
    assert report["summary"]["validation_claim_allowed"] is False
    assert reload_report["restart_loaded"] is True
    assert reload_report["restart_reload_stats_match"] is True
    assert (ROOT / "outputs/step110_proxy_preflow/lbm_preflow_restart.npz").is_file()


def test_step110_driver_can_load_lbm_restart():
    config = FSIDriverConfig(lbm_restart_path="outputs/step110_proxy_preflow/lbm_preflow_restart.npz")
    assert config.lbm_restart_path == "outputs/step110_proxy_preflow/lbm_preflow_restart.npz"
    assert config.lbm_restart_scope == "rho_velocity_populations"

    with pytest.raises(ValueError):
        FSIDriverConfig(lbm_restart_required=True)

    restart_source = (ROOT / "src/mpm_lbm/sim/lbm/restart.py").read_text(encoding="utf-8")
    driver_source = (ROOT / "src/mpm_lbm/sim/drivers/fsi_driver.py").read_text(encoding="utf-8")
    assert "def load_lbm_restart_to_lbm" in restart_source
    assert "restart_n_grid_matches" in restart_source
    assert "_load_lbm_restart_if_configured" in driver_source
    assert "load_lbm_restart_to_lbm" in driver_source


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)

