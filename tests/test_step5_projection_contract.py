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


def test_step5_required_artifacts_exist():
    required_paths = [
        "src/projection.py",
        "baseline_tests/run_step5_projection_static_block.py",
        "baseline_tests/run_step5_projection_moving_block.py",
        "baseline_tests/run_step5_projection_after_mpm_motion.py",
        "baseline_tests/run_step5_dynamic_solid_mask_dryrun.py",
        "logs/step5_projection_static.log",
        "logs/step5_projection_moving.log",
        "logs/step5_projection_motion.log",
        "logs/step5_dynamic_solid_mask.log",
        "outputs/step5_projection_static/LBMProjection_0.vtr",
        "outputs/step5_projection_static/solid_phi.npy",
        "outputs/step5_projection_static/solid_mass.npy",
        "outputs/step5_projection_static/solid_vel.npy",
        "outputs/step5_projection_static/particles_x.npy",
        "outputs/step5_projection_moving/LBMProjection_0.vtr",
        "outputs/step5_projection_moving/solid_phi.npy",
        "outputs/step5_projection_moving/solid_mass.npy",
        "outputs/step5_projection_moving/solid_vel.npy",
        "outputs/step5_projection_moving/particles_x.npy",
        "outputs/step5_projection_motion/LBMProjection_0.vtr",
        "outputs/step5_projection_motion/LBMProjection_1.vtr",
        "outputs/step5_projection_motion/solid_phi_0.npy",
        "outputs/step5_projection_motion/solid_phi_1.npy",
        "outputs/step5_projection_motion/solid_mass_0.npy",
        "outputs/step5_projection_motion/solid_mass_1.npy",
        "outputs/step5_projection_motion/solid_vel_0.npy",
        "outputs/step5_projection_motion/solid_vel_1.npy",
        "outputs/step5_dynamic_solid_mask/LBMProjection_mask_on.vtr",
        "outputs/step5_dynamic_solid_mask/LBMProjection_mask_off.vtr",
        "outputs/step5_dynamic_solid_mask/solid_on.npy",
        "outputs/step5_dynamic_solid_mask/solid_off.npy",
        "STEP5_MPM_TO_LBM_PROJECTION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step5_projection_source_contains_required_interfaces():
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    lbm_source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    projection_source = (ROOT / "src/mpm_lbm/sim/coupling/projection.py").read_text(encoding="utf-8")
    legacy_projection_source = (ROOT / "src/projection.py").read_text(encoding="utf-8")

    required_keywords = [
        "class MPMToLBMProjector3D",
        "def clear_projection",
        "def inside_lbm",
        "def project_particles",
        "def normalize_projection",
        "def project",
        "def get_stats",
        "projected_mass",
        "projected_volume_raw",
        "projected_volume_clamped",
        "max_phi_raw",
        "active_cell_count",
        "vel_scale_norm_to_lbm",
        "solid_phi",
        "solid_mass",
        "solid_vel",
        "cell_volume_norm",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in projection_source]
    assert missing == []

    assert "MPMToLBMProjector3D" in init_source
    assert "from .mpm_lbm.sim.coupling.projection import *" in legacy_projection_source
    assert "astype(np.int8)" in lbm_source


def test_step5_scripts_do_not_implement_force_coupling():
    script_paths = [
        ROOT / "baseline_tests/run_step5_projection_static_block.py",
        ROOT / "baseline_tests/run_step5_projection_moving_block.py",
        ROOT / "baseline_tests/run_step5_projection_after_mpm_motion.py",
        ROOT / "baseline_tests/run_step5_dynamic_solid_mask_dryrun.py",
    ]
    script_sources = [path.read_text(encoding="utf-8") for path in script_paths]
    forbidden_tokens = [
        "set_uniform_cell_force(",
        "set_spherical_cell_force(",
        "build_dummy_hydro_force(",
        "penalty",
        "momentum_exchange",
        "moving_bounce_back",
        "ReducedSquidFSI",
    ]

    offenders = []
    for source in script_sources:
        offenders.extend(token for token in forbidden_tokens if token in source)
    assert offenders == []

    dryrun_source = (ROOT / "baseline_tests/run_step5_dynamic_solid_mask_dryrun.py").read_text(
        encoding="utf-8"
    )
    assert ".step(" not in dryrun_source


def test_step5_logs_record_successful_baselines():
    static_log = read_log(ROOT / "logs/step5_projection_static.log")
    moving_log = read_log(ROOT / "logs/step5_projection_moving.log")
    motion_log = read_log(ROOT / "logs/step5_projection_motion.log")
    mask_log = read_log(ROOT / "logs/step5_dynamic_solid_mask.log")

    assert "Starting on arch=cuda" in static_log
    assert "[OK] Step 5 static block projection baseline finished" in static_log
    assert "relative_mass_error" in static_log
    assert "max_solid_speed_lbm" in static_log
    assert "Assign may lose precision: i8 <- f64" not in static_log

    assert "Starting on arch=cuda" in moving_log
    assert "[OK] Step 5 moving block velocity projection baseline finished" in moving_log
    assert "projected_mean_solid_vel" in moving_log
    assert "target_u_lbm=(0.03, 0.0, 0.0)" in moving_log

    assert "Starting on arch=cuda" in motion_log
    assert "[OK] Step 5 projection after MPM motion baseline finished" in motion_log
    assert "center_x_initial" in motion_log
    assert "center_x_final" in motion_log

    assert "Starting on arch=cuda" in mask_log
    assert "[OK] Step 5 dynamic solid mask dry run finished" in mask_log
    assert "solid_on_count" in mask_log
    assert "reinit_count" in mask_log


def test_step5_report_acceptance_complete():
    report = (ROOT / "STEP5_MPM_TO_LBM_PROJECTION_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 5 final commit",
        "- [x] `src/projection.py` exists",
        "- [x] `src/__init__.py` exports `MPMToLBMProjector3D`",
        "- [x] `LBMFluid3D.init_geo()` dtype cleanup is applied",
        "- [x] `MPMToLBMProjector3D.clear_projection()` clears `solid_phi`, `solid_mass`, `solid_vel`",
        "- [x] `MPMToLBMProjector3D.project_particles()` writes `solid_phi`",
        "- [x] `MPMToLBMProjector3D.project_particles()` writes `solid_mass`",
        "- [x] `MPMToLBMProjector3D.project_particles()` writes `solid_vel`",
        "- [x] solid velocity uses normalized-to-LBM lattice velocity scaling",
        "- [x] volume fraction uses `current_volume = vol0 * Jp`",
        "- [x] `solid_phi` is clamped to `[0, 1]`",
        "- [x] projected raw/clamped volume diagnostics are recorded",
        "- [x] static block projection baseline passes",
        "- [x] moving block velocity projection baseline passes",
        "- [x] projection after MPM motion baseline passes",
        "- [x] dynamic solid mask dry-run baseline passes",
        "- [x] projected_mass relative error < 1e-5 in required baselines",
        "- [x] static block projected `solid_vel` is approximately zero",
        "- [x] moving block projected `solid_vel` matches `target_u_lbm`",
        "- [x] particle `center_x` increases after motion baseline",
        "- [x] active_cell_count > 0",
        "- [x] `solid_phi` finite",
        "- [x] `solid_mass` finite",
        "- [x] `solid_vel` finite",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] `cell_force` remains zero",
        "- [x] `hydro_force` remains zero",
        "- [x] no penalty force is implemented",
        "- [x] no momentum exchange is implemented",
        "- [x] no moving bounce-back is implemented",
        "- [x] no FSI force coupling is implemented",
        "- [x] logs are saved under `logs/`",
        "- [x] outputs are saved under `outputs/`",
        "- [x] `STEP5_MPM_TO_LBM_PROJECTION_REPORT.md` is complete",
        "- [x] `pytest -q` passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
