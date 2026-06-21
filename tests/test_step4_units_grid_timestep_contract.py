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


def test_step4_required_artifacts_exist():
    required_paths = [
        "src/mpm_lbm/sim/drivers/sim_config.py",
        "src/units.py",
        "baseline_tests/run_step4_units_consistency.py",
        "baseline_tests/run_step4_shared_domain.py",
        "baseline_tests/run_step4_time_sync_dummy.py",
        "logs/step4_units_consistency.log",
        "logs/step4_shared_domain.log",
        "logs/step4_time_sync_dummy.log",
        "outputs/step4_shared_domain/particle_lbm_indices.npy",
        "outputs/step4_shared_domain/particles_x.npy",
        "outputs/step4_time_sync_dummy/LBMFluid_20.vtr",
        "outputs/step4_time_sync_dummy/particles_x.npy",
        "outputs/step4_time_sync_dummy/particles_v.npy",
        "outputs/step4_time_sync_dummy/particles_F.npy",
        "outputs/step4_time_sync_dummy/particles_J.npy",
        "STEP4_UNITS_GRID_TIMESTEP_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step4_source_contains_required_interfaces():
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    sim_source = (ROOT / "src/mpm_lbm/sim/drivers/sim_config.py").read_text(encoding="utf-8")
    units_source = (ROOT / "src/mpm_lbm/sim/units/mapper.py").read_text(encoding="utf-8")
    solid_source = (ROOT / "src/mpm_lbm/sim/mpm/solid.py").read_text(encoding="utf-8")
    legacy_units_source = (ROOT / "src/units.py").read_text(encoding="utf-8")

    required_keywords = [
        "class UnifiedSimConfig",
        "mpm_substeps_per_lbm_step",
        "lbm_dt_phys",
        "make_lbm_config",
        "make_mpm_config",
        "class GridUnitMapper",
        "norm_to_lbm_coord",
        "lbm_coord_to_norm",
        "norm_to_lbm_index",
        "lbm_index_to_norm_center",
        "velocity_lbm_to_norm",
        "velocity_norm_to_lbm",
        "acceleration_lbm_to_norm",
        "acceleration_norm_to_lbm",
        "viscosity_lbm_to_norm",
        "viscosity_norm_to_lbm",
    ]
    combined_source = "\n".join([sim_source, units_source])
    missing = [keyword for keyword in required_keywords if keyword not in combined_source]
    assert missing == []

    assert "UnifiedSimConfig" in init_source
    assert "GridUnitMapper" in init_source
    assert "from .mpm_lbm.sim.units.mapper import *" in legacy_units_source
    assert "set_uniform_velocity" in solid_source


def test_step4_scripts_do_not_implement_projection_or_fsi_force():
    script_sources = [
        (ROOT / "baseline_tests/run_step4_shared_domain.py").read_text(encoding="utf-8"),
        (ROOT / "baseline_tests/run_step4_time_sync_dummy.py").read_text(encoding="utf-8"),
    ]
    forbidden_tokens = [
        ".solid_phi",
        ".solid_vel",
        ".cell_force",
        ".hydro_force",
        "set_dummy_solid_phi_block",
        "set_uniform_cell_force",
        "build_dummy_hydro_force",
        "update_dynamic_solid",
        "reinitialize_new_fluid_cells",
        "ReducedSquidFSI",
    ]

    offenders = []
    for source in script_sources:
        offenders.extend(token for token in forbidden_tokens if token in source)
    assert offenders == []


def test_step4_logs_record_successful_baselines():
    units_log = read_log(ROOT / "logs/step4_units_consistency.log")
    shared_log = read_log(ROOT / "logs/step4_shared_domain.log")
    sync_log = read_log(ROOT / "logs/step4_time_sync_dummy.log")

    assert "[OK] Step 4 units consistency baseline finished" in units_log
    assert "u_lbm=0.03 -> u_norm=0.234375" in units_log
    assert "a_norm=9.8 -> a_lbm=0.0050176" in units_log

    assert "Starting on arch=cuda" in shared_log
    assert "[OK] Step 4 shared domain baseline finished" in shared_log
    assert "index_min=" in shared_log
    assert "index_max=" in shared_log

    assert "Starting on arch=cuda" in sync_log
    assert "[OK] Step 4 time sync dummy baseline finished" in sync_log
    assert "lbm_step=0020" in sync_log
    assert "total_mpm_substeps=200" in sync_log


def test_step4_report_acceptance_complete():
    report = (ROOT / "STEP4_UNITS_GRID_TIMESTEP_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 4 final commit",
        "- [x] `src/sim_config.py` exists",
        "- [x] `src/units.py` exists",
        "- [x] `src/__init__.py` exports `UnifiedSimConfig` and `GridUnitMapper`",
        "- [x] `MPMSolid3D` has `set_uniform_velocity()`",
        "- [x] LBM and MPM use the same `n_grid`",
        "- [x] `nx = ny = nz = n_grid`",
        "- [x] `dx_norm = 1 / n_grid`",
        "- [x] `lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt`",
        "- [x] position mapping works",
        "- [x] velocity round trip works",
        "- [x] acceleration round trip works",
        "- [x] viscosity round trip works",
        "- [x] `LBMFluid3D` and `MPMSolid3D` can initialize in one script",
        "- [x] shared-domain particle indices are valid",
        "- [x] synchronized dummy loop runs",
        "- [x] `total_mpm_substeps = n_lbm_steps * mpm_substeps_per_lbm_step`",
        "- [x] LBM rho remains stable",
        "- [x] MPM `min_J > 0`",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no MPM -> LBM projection is implemented",
        "- [x] no FSI force coupling is implemented",
        "- [x] logs are saved under `logs/`",
        "- [x] outputs are saved under `outputs/`",
        "- [x] `STEP4_UNITS_GRID_TIMESTEP_REPORT.md` is complete",
        "- [x] `pytest -q` passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
