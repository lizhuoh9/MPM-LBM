import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step82_wall_velocity_solid_vel_quality_artifact_passes():
    payload = read_json("outputs/step82_wall_velocity_solid_vel_quality/wall_velocity_solid_vel_quality.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step82_wall_velocity_solid_vel_quality_pass"] is True
    assert summary["pass_count"] == summary["row_count"]
    assert summary["wall_velocity_application_report_pass_count"] == 1
    assert summary["boundary_motion_interface_report_pass_count"] == 1
    assert summary["finite_wall_velocity_report_count"] == 1
    assert summary["capped_wall_velocity_report_count"] == 1
    checks = {row["check"]: row for row in payload["rows"]}
    assert checks["rho_min_min"]["pass"] is True
    assert checks["rho_max_max"]["pass"] is True
    assert checks["lbm_max_v_max"]["pass"] is True
    assert checks["mpm_min_J_min"]["pass"] is True
    assert checks["mpm_max_speed_max"]["pass"] is True
    assert checks["projected_mass_final"]["pass"] is True
    assert checks["active_cell_count_final"]["pass"] is True
    assert checks["bb_link_count_max"]["pass"] is True
    assert checks["max_grid_reaction_norm_max_finite"]["pass"] is True
    assert checks["wall_velocity_application_report_pass"]["pass"] is True
    assert checks["boundary_motion_interface_report_pass"]["pass"] is True
    assert checks["lbm_population_update_count"]["actual"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
