import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step55_compatibility_shim_audit_passes():
    payload = read_json("outputs/step55_compatibility_shim_audit/compatibility_shim_audit.json")
    summary = payload["summary"]
    assert summary["compatibility_shim_audit_pass"] is True
    assert int(summary["surface_count"]) == int(summary["pass_count"])
    assert summary["source_text_check_only"] is True
    assert summary["avoid_heavy_runtime_imports_in_hook"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step55_lazy_compatibility_surfaces_are_source_visible():
    src_init = read_text("src/__init__.py")
    assert "_EXPORT_MODULES" in src_init
    assert "def __getattr__(name):" in src_init
    assert '"LBMFluid3D": "src.lbm_fluid"' in src_init

    fluid = read_text("src/mpm_lbm/sim/lbm/fluid.py")
    legacy_fluid = read_text("src/lbm_fluid.py")
    assert "LBMFluid3D" in fluid
    assert "class LBMFluid3D" in fluid
    assert "legacy_getattr" not in fluid
    assert "from .mpm_lbm.sim.lbm.fluid import *" in legacy_fluid

    index = read_text("src/mpm_lbm/evidence/repository_evidence_index.py")
    assert '_LEGACY_MODULE = "src.repository_evidence_index"' in index
    assert "build_repository_evidence_index" in index

    step52 = read_text("experiments/steps/step52_48_feasibility_proxy/envelope.py")
    legacy_step52 = read_text("src/runtime_geometry_wall_velocity_48_feasibility_envelope.py")
    assert "legacy_getattr" not in step52
    assert "run_48_feasibility_matrix" in step52
    assert "from experiments.steps.step52_48_feasibility_proxy.envelope import *" in legacy_step52


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
