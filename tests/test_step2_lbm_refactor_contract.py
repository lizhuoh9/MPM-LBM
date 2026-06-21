from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_log(path):
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-16"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="ignore")


def test_step2_required_artifacts_exist():
    required_paths = [
        "src/__init__.py",
        "src/lbm_config.py",
        "src/lbm_fluid.py",
        "baseline_tests/run_lbm_refactored_smoke.py",
        "baseline_tests/run_lbm_refactored_poiseuille.py",
        "baseline_tests/run_lbm_refactored_body_force.py",
        "baseline_tests/run_lbm_refactored_dynamic_solid_dummy.py",
        "logs/step2_lbm_refactor_smoke.log",
        "logs/step2_lbm_refactor_poiseuille.log",
        "logs/step2_lbm_refactor_force.log",
        "logs/step2_lbm_refactor_dynamic_solid.log",
        "outputs/lbm_refactored_smoke/LBMFluid_500.vtr",
        "outputs/lbm_refactored_poiseuille/LBMFluid_1000.vtr",
        "outputs/lbm_refactored_force/LBMFluid_1000.vtr",
        "outputs/lbm_refactored_dynamic_solid/LBMFluid_dynamic_on_0.vtr",
        "outputs/lbm_refactored_dynamic_solid/LBMFluid_dynamic_off_1.vtr",
        "STEP2_LBM_REFACTOR_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step2_source_contains_required_interfaces():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    config_source = (ROOT / "src/mpm_lbm/sim/lbm/config.py").read_text(encoding="utf-8")
    legacy_source = (ROOT / "src/lbm_fluid.py").read_text(encoding="utf-8")
    legacy_config_source = (ROOT / "src/lbm_config.py").read_text(encoding="utf-8")

    assert "class LBMConfig" in config_source
    assert "class LBMFluid3D" in source
    assert "Compatibility shim" in legacy_source
    assert "from .mpm_lbm.sim.lbm.fluid import *" in legacy_source
    assert "Compatibility shim" in legacy_config_source
    assert "from .mpm_lbm.sim.lbm.config import *" in legacy_config_source
    assert "def step(self):" in source
    assert "self.colission()" in source
    assert "self.streaming1()" in source
    assert "self.Boundary_condition()" in source
    assert "self.streaming3()" in source
    assert "self.cell_force" in source
    assert "self.hydro_force" in source
    assert "self.solid_phi" in source
    assert "self.static_solid" in source
    assert "self.old_solid" in source
    assert "self.reinit_flag" in source
    assert "ti.static(self.force_flag" not in source
    assert "def clear_coupling_fields" in source
    assert "def copy_solid_to_static" in source
    assert "def update_dynamic_solid" in source
    assert "def reinitialize_new_fluid_cells" in source
    assert "def set_uniform_cell_force" in source
    assert "def set_spherical_cell_force" in source
    assert "def set_dummy_solid_phi_block" in source
    assert "def build_dummy_hydro_force" in source
    assert "def get_stats" in source
    assert "def export_VTK" in source


def test_step2_logs_record_successful_baselines():
    smoke_log = read_log(ROOT / "logs/step2_lbm_refactor_smoke.log")
    poiseuille_log = read_log(ROOT / "logs/step2_lbm_refactor_poiseuille.log")
    force_log = read_log(ROOT / "logs/step2_lbm_refactor_force.log")
    dynamic_log = read_log(ROOT / "logs/step2_lbm_refactor_dynamic_solid.log")

    assert "Starting on arch=cuda" in smoke_log
    assert "[OK] Step 2 refactored smoke baseline finished" in smoke_log
    assert "iter=0500" in smoke_log

    assert "Starting on arch=cuda" in poiseuille_log
    assert "[OK] Step 2 refactored Poiseuille baseline finished" in poiseuille_log
    assert "center_ux" in poiseuille_log

    assert "Starting on arch=cuda" in force_log
    assert "[OK] Step 2 refactored body-force baseline finished" in force_log
    assert "force_norm_max=1.000000e-06" in force_log

    assert "Starting on arch=cuda" in dynamic_log
    assert "[OK] Step 2 dynamic-solid dummy baseline finished" in dynamic_log
    assert "solid_on_count=512" in dynamic_log


def test_step2_report_marks_acceptance_complete():
    report = (ROOT / "STEP2_LBM_REFACTOR_REPORT.md").read_text(encoding="utf-8")

    assert "- [x] `src/lbm_fluid.py` exists" in report
    assert "- [x] `src/lbm_config.py` exists" in report
    assert "- [x] Zero `cell_force` smoke baseline completes" in report
    assert "- [x] Refactored Poiseuille baseline completes" in report
    assert "- [x] `set_uniform_cell_force()` produces a velocity response" in report
    assert "- [x] Dynamic solid dummy baseline completes" in report
    assert "- [x] `pytest` passes" in report
    assert "- [x] Yes" in report
