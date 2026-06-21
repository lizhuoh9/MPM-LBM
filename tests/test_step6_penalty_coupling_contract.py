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


def test_step6_required_artifacts_exist():
    required_paths = [
        "src/coupling.py",
        "baseline_tests/run_step6_penalty_force_field.py",
        "baseline_tests/run_step6_lbm_response_to_moving_solid.py",
        "baseline_tests/run_step6_two_way_mpm_reaction.py",
        "baseline_tests/run_step6_coupled_smoke.py",
        "logs/step6_penalty_force_field.log",
        "logs/step6_lbm_response.log",
        "logs/step6_two_way_reaction.log",
        "logs/step6_coupled_smoke.log",
        "outputs/step6_penalty_force_field/LBMForce_0.vtr",
        "outputs/step6_penalty_force_field/cell_force.npy",
        "outputs/step6_penalty_force_field/hydro_force.npy",
        "outputs/step6_lbm_response/LBMFluid_100.vtr",
        "outputs/step6_lbm_response/cell_force.npy",
        "outputs/step6_lbm_response/hydro_force.npy",
        "outputs/step6_two_way_reaction/particles_x.npy",
        "outputs/step6_two_way_reaction/particles_v.npy",
        "outputs/step6_two_way_reaction/particles_F.npy",
        "outputs/step6_two_way_reaction/particles_J.npy",
        "outputs/step6_coupled_smoke/LBMFluid_20.vtr",
        "outputs/step6_coupled_smoke/particles_x.npy",
        "outputs/step6_coupled_smoke/particles_v.npy",
        "outputs/step6_coupled_smoke/particles_F.npy",
        "outputs/step6_coupled_smoke/particles_J.npy",
        "outputs/step6_coupled_smoke/cell_force.npy",
        "outputs/step6_coupled_smoke/hydro_force.npy",
        "STEP6_PENALTY_COUPLING_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step6_coupling_source_contains_required_interfaces():
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    coupling_source = (ROOT / "src/mpm_lbm/sim/coupling/penalty.py").read_text(encoding="utf-8")
    legacy_coupling_source = (ROOT / "src/coupling.py").read_text(encoding="utf-8")

    required_keywords = [
        "class PenaltyFSICoupler3D",
        "def clear_force_fields",
        "def inside_lbm",
        "def build_penalty_force",
        "def add_lbm_reaction_to_mpm_grid",
        "def get_stats",
        "cell_force",
        "hydro_force",
        "solid_phi",
        "solid_vel",
        "beta_lbm",
        "force_cap_lbm",
        "force_density_scale_lbm_to_norm",
        "grid_f_ext",
        "net_cell_force",
        "net_hydro_force",
        "net_reaction_grid_force",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in coupling_source]
    assert missing == []

    assert "PenaltyFSICoupler3D" in init_source
    assert "from .mpm_lbm.sim.coupling.penalty import *" in legacy_coupling_source


def test_step6_scripts_do_not_use_forbidden_methods():
    source_paths = [
        ROOT / "src/mpm_lbm/sim/coupling/penalty.py",
        ROOT / "baseline_tests/run_step6_penalty_force_field.py",
        ROOT / "baseline_tests/run_step6_lbm_response_to_moving_solid.py",
        ROOT / "baseline_tests/run_step6_two_way_mpm_reaction.py",
        ROOT / "baseline_tests/run_step6_coupled_smoke.py",
    ]
    forbidden_tokens = [
        "moving_bounce_back",
        "momentum_exchange",
        "two_phase",
        "contact_angle",
        "ReducedSquidFSI",
        "update_dynamic_solid(",
        "reinitialize_new_fluid_cells(",
    ]

    offenders = []
    for path in source_paths:
        source = path.read_text(encoding="utf-8")
        offenders.extend(f"{path.name}: {token}" for token in forbidden_tokens if token in source)
    assert offenders == []


def test_step6_logs_record_successful_baselines():
    force_log = read_log(ROOT / "logs/step6_penalty_force_field.log")
    lbm_log = read_log(ROOT / "logs/step6_lbm_response.log")
    reaction_log = read_log(ROOT / "logs/step6_two_way_reaction.log")
    smoke_log = read_log(ROOT / "logs/step6_coupled_smoke.log")

    assert "[OK] Step 6 penalty force field baseline finished" in force_log
    assert "active_force_cell_count" in force_log
    assert "cell_force_max_norm" in force_log
    assert "hydro_force_max_norm" in force_log
    assert "net_cell_force" in force_log
    assert "net_hydro_force" in force_log

    assert "[OK] Step 6 LBM response baseline finished" in lbm_log
    assert "initial_fluid_mean_ux" in lbm_log
    assert "final_fluid_mean_ux" in lbm_log
    assert "active_force_cell_count" in lbm_log
    assert "cell_force_max_norm" in lbm_log
    assert "hydro_force_max_norm" in lbm_log

    assert "[OK] Step 6 MPM reaction baseline finished" in reaction_log
    assert "initial_solid_mean_vx_norm" in reaction_log
    assert "final_solid_mean_vx_norm" in reaction_log
    assert "max_reaction_grid_force_norm" in reaction_log
    assert "net_reaction_grid_force" in reaction_log

    assert "[OK] Step 6 coupled smoke baseline finished" in smoke_log
    assert "initial_fluid_mean_ux" in smoke_log
    assert "final_fluid_mean_ux" in smoke_log
    assert "initial_solid_mean_vx_norm" in smoke_log
    assert "final_solid_mean_vx_norm" in smoke_log
    assert "completed_lbm_steps=20" in smoke_log
    assert "total_mpm_substeps=200" in smoke_log


def test_step6_report_acceptance_complete():
    report = (ROOT / "STEP6_PENALTY_COUPLING_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 6 final commit",
        "- [x] `src/coupling.py` exists",
        "- [x] `src/__init__.py` exports `PenaltyFSICoupler3D`",
        "- [x] `PenaltyFSICoupler3D.clear_force_fields()` exists",
        "- [x] `PenaltyFSICoupler3D.build_penalty_force()` exists",
        "- [x] `PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid()` exists",
        "- [x] `build_penalty_force()` writes nonzero `lbm.cell_force` when projected solid moves",
        "- [x] `build_penalty_force()` writes `lbm.hydro_force`",
        "- [x] `hydro_force = -cell_force`",
        "- [x] moving solid +x gives `net_cell_force_x > 0`",
        "- [x] moving solid +x gives `net_hydro_force_x < 0`",
        "- [x] `net_cell_force + net_hydro_force` approximately zero",
        "- [x] LBM response baseline shows fluid mean ux increases",
        "- [x] MPM reaction baseline shows solid mean vx decreases",
        "- [x] coupled smoke baseline completes 20 LBM steps",
        "- [x] coupled smoke baseline completes 200 MPM substeps",
        "- [x] `rho_min > 0.95`",
        "- [x] `rho_max < 1.05`",
        "- [x] `lbm_max_v < 0.1`",
        "- [x] `mpm_min_J > 0`",
        "- [x] `mpm_max_speed < 10`",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no moving bounce-back",
        "- [x] no momentum exchange",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no `update_dynamic_solid()` in Step 6 baselines",
        "- [x] no `reinitialize_new_fluid_cells()` in Step 6 baselines",
        "- [x] no `external/taichi_LBM3D` edits",
        "- [x] logs are saved under `logs/`",
        "- [x] outputs are saved under `outputs/`",
        "- [x] `STEP6_PENALTY_COUPLING_REPORT.md` is complete",
        "- [x] `pytest -q` passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
