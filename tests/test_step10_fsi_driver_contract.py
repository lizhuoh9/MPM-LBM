import json
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


def test_step10_required_artifacts_exist():
    required_paths = [
        "src/mpm_lbm/sim/drivers/fsi_config.py",
        "src/fsi_driver.py",
        "src/mpm_lbm/sim/io/run_utils.py",
        "configs/step10_penalty_default.json",
        "configs/step10_moving_boundary_default.json",
        "configs/step10_mode_matrix.json",
        "baseline_tests/run_step10_driver_penalty_mode.py",
        "baseline_tests/run_step10_driver_moving_boundary_mode.py",
        "baseline_tests/run_step10_driver_mode_matrix.py",
        "baseline_tests/run_step10_performance_profile.py",
        "logs/step10_driver_penalty.log",
        "logs/step10_driver_moving_boundary.log",
        "logs/step10_mode_matrix.log",
        "logs/step10_performance_profile.log",
        "outputs/step10_driver_penalty/LBMFluid_20.vtr",
        "outputs/step10_driver_penalty/particles_x.npy",
        "outputs/step10_driver_penalty/particles_v.npy",
        "outputs/step10_driver_penalty/particles_F.npy",
        "outputs/step10_driver_penalty/particles_J.npy",
        "outputs/step10_driver_penalty/diagnostics_timeseries.npz",
        "outputs/step10_driver_penalty/diagnostics_timeseries.csv",
        "outputs/step10_driver_moving_boundary/LBMFluid_20.vtr",
        "outputs/step10_driver_moving_boundary/particles_x.npy",
        "outputs/step10_driver_moving_boundary/particles_v.npy",
        "outputs/step10_driver_moving_boundary/particles_F.npy",
        "outputs/step10_driver_moving_boundary/particles_J.npy",
        "outputs/step10_driver_moving_boundary/diagnostics_timeseries.npz",
        "outputs/step10_driver_moving_boundary/diagnostics_timeseries.csv",
        "outputs/step10_mode_matrix/mode_matrix_results.csv",
        "outputs/step10_mode_matrix/mode_matrix_results.npz",
        "outputs/step10_performance_profile/performance_results.csv",
        "outputs/step10_performance_profile/performance_results.npz",
        "STEP10_FSI_DRIVER_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step10_source_contains_required_interfaces():
    sources = []
    for rel_path in ("src/mpm_lbm/sim/drivers/fsi_config.py", "src/fsi_driver.py", "src/mpm_lbm/sim/io/run_utils.py"):
        path = ROOT / rel_path
        if path.is_file():
            sources.append(path.read_text(encoding="utf-8"))
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    combined = "\n".join(sources)

    required_keywords = [
        "class FSIDriverConfig",
        "class FSIDriver3D",
        "coupling_mode",
        "step_once",
        "run",
        "collect_diagnostics",
        "export_outputs",
        "save_timeseries",
        "PenaltyFSICoupler3D",
        "MovingBoundaryFSICoupler3D",
        "MPMToLBMProjector3D",
        "FSIDiagnostics3D",
        "diagnostics_timeseries",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in combined]
    assert missing == []
    assert "FSIDriverConfig" in init_source
    assert "FSIDriver3D" in init_source


def test_step10_config_files_are_valid_json():
    config_paths = [
        ROOT / "configs/step10_penalty_default.json",
        ROOT / "configs/step10_moving_boundary_default.json",
        ROOT / "configs/step10_mode_matrix.json",
    ]

    for path in config_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    penalty = json.loads(config_paths[0].read_text(encoding="utf-8"))
    moving = json.loads(config_paths[1].read_text(encoding="utf-8"))
    matrix = json.loads(config_paths[2].read_text(encoding="utf-8"))

    assert penalty["coupling_mode"] == "penalty"
    assert moving["coupling_mode"] == "moving_boundary"
    assert moving["mb_force_cap_norm"] == 0.0001
    assert matrix["modes"] == ["none", "penalty", "moving_boundary"]


def test_step10_scripts_respect_mode_boundaries():
    source_paths = [
        ROOT / "src/mpm_lbm/sim/drivers/fsi_config.py",
        ROOT / "src/fsi_driver.py",
        ROOT / "src/mpm_lbm/sim/io/run_utils.py",
        ROOT / "baseline_tests/run_step10_driver_penalty_mode.py",
        ROOT / "baseline_tests/run_step10_driver_moving_boundary_mode.py",
        ROOT / "baseline_tests/run_step10_driver_mode_matrix.py",
        ROOT / "baseline_tests/run_step10_performance_profile.py",
    ]
    forbidden_tokens = [
        "two_phase",
        "contact_angle",
        "ReducedSquidFSI",
    ]

    offenders = []
    for path in source_paths:
        if path.is_file():
            source = path.read_text(encoding="utf-8")
            offenders.extend(f"{path.name}: {token}" for token in forbidden_tokens if token in source)

    assert offenders == []

    driver_source = (ROOT / "src/fsi_driver.py").read_text(encoding="utf-8")
    assert 'coupling_mode == "none"' in driver_source
    assert 'coupling_mode == "penalty"' in driver_source
    assert 'coupling_mode == "moving_boundary"' in driver_source
    assert "step_moving_bounceback" in driver_source
    assert "build_penalty_force" in driver_source


def test_step10_logs_record_successful_baselines():
    penalty_log = read_log(ROOT / "logs/step10_driver_penalty.log")
    moving_log = read_log(ROOT / "logs/step10_driver_moving_boundary.log")
    matrix_log = read_log(ROOT / "logs/step10_mode_matrix.log")
    perf_log = read_log(ROOT / "logs/step10_performance_profile.log")
    combined_logs = "\n".join([penalty_log, moving_log, matrix_log, perf_log])

    assert "[OK] Step 10 driver penalty mode finished" in penalty_log
    assert "[OK] Step 10 driver moving-boundary mode finished" in moving_log
    assert "[OK] Step 10 driver mode matrix finished" in matrix_log
    assert "[OK] Step 10 performance profile finished" in perf_log

    required_log_tokens = [
        "coupling_mode",
        "completed_lbm_steps",
        "total_mpm_substeps",
        "cell_force_max_norm",
        "hydro_force_max_norm",
        "rho_min",
        "rho_max",
        "lbm_max_v",
        "mpm_min_J",
        "mpm_max_speed",
    ]
    missing = [token for token in required_log_tokens if token not in combined_logs]
    assert missing == []


def test_step10_report_acceptance_complete():
    report = (ROOT / "STEP10_FSI_DRIVER_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 10 final commit",
        "- [x] src/fsi_config.py exists",
        "- [x] src/fsi_driver.py exists",
        "- [x] src/run_utils.py exists",
        "- [x] src/__init__.py exports FSIDriverConfig",
        "- [x] src/__init__.py exports FSIDriver3D",
        "- [x] configs/step10_penalty_default.json exists",
        "- [x] configs/step10_moving_boundary_default.json exists",
        "- [x] configs/step10_mode_matrix.json exists",
        "- [x] FSIDriverConfig validates coupling_mode",
        "- [x] FSIDriver3D supports coupling_mode=\"none\"",
        "- [x] FSIDriver3D supports coupling_mode=\"penalty\"",
        "- [x] FSIDriver3D supports coupling_mode=\"moving_boundary\"",
        "- [x] penalty driver baseline completes 20 LBM steps",
        "- [x] penalty driver baseline completes 200 MPM substeps",
        "- [x] penalty driver baseline has cell_force_max_norm > 0",
        "- [x] moving-boundary driver baseline completes 20 LBM steps",
        "- [x] moving-boundary driver baseline completes 200 MPM substeps",
        "- [x] moving-boundary driver baseline has bb_link_count > 0",
        "- [x] moving-boundary driver baseline has active_reaction_particle_count > 0",
        "- [x] moving-boundary driver baseline keeps cell_force_max_norm == 0",
        "- [x] mode matrix baseline completes",
        "- [x] mode matrix includes none, penalty, moving_boundary",
        "- [x] performance profile baseline completes",
        "- [x] common diagnostics_timeseries.npz is saved",
        "- [x] common diagnostics_timeseries.csv is saved",
        "- [x] mode_matrix_results.csv is saved",
        "- [x] mode_matrix_results.npz is saved",
        "- [x] performance_results.csv is saved",
        "- [x] performance_results.npz is saved",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] mpm_max_speed < 10",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] logs are saved under logs/",
        "- [x] outputs are saved under outputs/",
        "- [x] STEP10_FSI_DRIVER_REPORT.md is complete",
        "- [x] pytest -q passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
