import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step80_runtime_geometry_diagnostic_only_quality_artifact_passes():
    payload = read_json("outputs/step80_runtime_geometry_diagnostic_only_quality/runtime_geometry_diagnostic_only_quality.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step80_runtime_geometry_diagnostic_only_quality_pass"] is True
    assert summary["pass_count"] == summary["row_count"]
    assert summary["geometry_motion_interface_report_pass_count"] == 1
    checks = {row["check"]: row for row in payload["rows"]}
    assert checks["rho_min_min"]["pass"] is True
    assert checks["rho_max_max"]["pass"] is True
    assert checks["lbm_max_v_max"]["pass"] is True
    assert checks["mpm_min_J_min"]["pass"] is True
    assert checks["mpm_max_speed_max"]["pass"] is True
    assert checks["projected_mass_final"]["pass"] is True
    assert checks["geometry_motion_interface_report_pass"]["pass"] is True
    assert checks["mutation_flag_enabled_count"]["actual"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
