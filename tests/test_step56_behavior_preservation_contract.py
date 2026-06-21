import json
import math
from pathlib import Path

from src.mpm_lbm.evidence.behavior_preservation_audit import build_behavior_preservation_audit
from src.mpm_lbm.sim.lbm.relaxation_semantics import (
    tau_from_lattice_kinematic_viscosity,
    tau_from_legacy_external_solver_parameter,
)
from src.mpm_lbm.sim.units.mapper import GridUnitMapper


ROOT = Path(__file__).resolve().parents[1]


def test_step56_behavior_preservation_audit_passes_current_source():
    rows, summary = build_behavior_preservation_audit(ROOT)
    assert summary["behavior_preservation_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    assert summary["object_construction_required_for_lbm_fluid_or_mpm_solid"] is False
    assert all(row["pass"] is True for row in rows)


def test_step56_behavior_preservation_artifact_passes():
    payload = read_json("outputs/step56_behavior_preservation_audit/behavior_preservation_audit.json")
    summary = payload["summary"]
    assert summary["behavior_preservation_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step56_tau_and_unit_mapper_semantics_are_unchanged():
    mapper = GridUnitMapper(n_grid=32, dx_norm=1.0 / 32.0, lbm_dt_phys=0.004)
    assert math.isclose(tau_from_legacy_external_solver_parameter(0.1), 0.5333333333333333)
    assert math.isclose(tau_from_lattice_kinematic_viscosity(0.1), 0.8)
    assert mapper.norm_to_lbm_coord([0.0625, 0.5, 0.9375]).tolist() == [2.0, 16.0, 30.0]
    assert mapper.norm_to_lbm_index([0.0625, 0.5, 0.9375]).tolist() == [2, 16, 30]
    assert mapper.lbm_coord_to_norm([2.0, 16.0, 30.0]).tolist() == [0.0625, 0.5, 0.9375]
    assert mapper.velocity_norm_to_lbm([0.234375, 0.0, 0.0]).tolist() == [0.03, 0.0, 0.0]
    assert mapper.velocity_lbm_to_norm([0.03, 0.0, 0.0]).tolist() == [0.234375, 0.0, 0.0]


def test_step56_artifact_manifest_and_step55_regression_guard_pass():
    manifest = read_json("outputs/step56_artifact_manifest/artifact_summary.json")
    regression = read_json("outputs/step56_step55_regression_guard/step55_regression_guard.json")
    assert manifest["artifact_budget_pass"] is True
    assert int(manifest["protected_external_taichi_lbm3d_step56_file_count"]) == 0
    assert int(manifest["protected_real_geometry_candidates_step56_file_count"]) == 0
    assert regression["summary"]["step55_regression_guard_pass"] is True
    assert int(regression["summary"]["row_count"]) == int(regression["summary"]["pass_count"])


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
