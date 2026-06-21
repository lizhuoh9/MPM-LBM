import json
import math
from pathlib import Path

from src.mpm_lbm.sim.lbm.relaxation_semantics import (
    relaxation_semantics_summary,
    tau_from_lattice_kinematic_viscosity,
    tau_from_legacy_external_solver_parameter,
)

ROOT = Path(__file__).resolve().parents[1]


def test_step54_lbm_relaxation_helpers_are_explicit_and_distinct():
    assert math.isclose(tau_from_legacy_external_solver_parameter(0.1), 0.1 / 3.0 + 0.5)
    assert math.isclose(tau_from_lattice_kinematic_viscosity(0.1), 3.0 * 0.1 + 0.5)
    assert not math.isclose(
        tau_from_legacy_external_solver_parameter(0.1),
        tau_from_lattice_kinematic_viscosity(0.1),
    )

    summary = relaxation_semantics_summary(0.1)
    assert summary["lbm_config_niu_semantics"] == "legacy_external_solver_relaxation_parameter"
    assert summary["default_solver_formula"] == "legacy_external_solver_parameter"
    assert summary["standard_lattice_viscosity_is_default"] is False
    assert summary["physical_viscosity_validation_claim"] is False
    assert summary["solver_behavior_changed"] is False


def test_step54_lbm_fluid_uses_legacy_helper_without_inline_formula():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    legacy_source = (ROOT / "src/lbm_fluid.py").read_text(encoding="utf-8")
    assert "from .relaxation_semantics import tau_from_legacy_external_solver_parameter" in source
    assert "tau_from_legacy_external_solver_parameter(self.niu)" in source
    assert "self.tau_f=self.niu/3.0+0.5" not in source
    assert "self.tau_f = self.niu / 3.0 + 0.5" not in source
    assert "from .mpm_lbm.sim.lbm.fluid import *" in legacy_source


def test_step54_lbm_relaxation_semantics_audit_output_passes():
    payload = read_json("outputs/step54_lbm_relaxation_semantics_audit/lbm_relaxation_semantics.json")
    summary = payload["summary"]
    assert summary["lbm_relaxation_semantics_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert summary["standard_viscosity_validation_claim"] is False
    assert summary["physical_viscosity_validation_claim"] is False
    assert summary["solver_behavior_changed"] is False

    policy = read_json("configs/step54_lbm_relaxation_semantics_policy.json")
    assert policy["legacy_tau_formula"] == "tau = niu / 3.0 + 0.5"
    assert policy["standard_lattice_kinematic_viscosity_tau_formula"] == "tau = 3.0 * nu_lbm + 0.5"
    assert policy["standard_lattice_viscosity_is_default"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
