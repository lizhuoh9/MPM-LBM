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


def test_step8_required_artifacts_exist():
    required_paths = [
        "baseline_tests/run_step8_static_bounceback_regression.py",
        "baseline_tests/run_step8_prescribed_moving_wall_couette.py",
        "baseline_tests/run_step8_projected_mpm_moving_boundary.py",
        "baseline_tests/run_step8_momentum_exchange_diagnostics.py",
        "logs/step8_static_bounceback_regression.log",
        "logs/step8_prescribed_moving_wall.log",
        "logs/step8_projected_mpm_boundary.log",
        "logs/step8_momentum_exchange.log",
        "outputs/step8_static_bounceback_regression/LBMStatic_100.vtr",
        "outputs/step8_static_bounceback_regression/LBMMovingZero_100.vtr",
        "outputs/step8_static_bounceback_regression/velocity_difference.npy",
        "outputs/step8_static_bounceback_regression/rho_difference.npy",
        "outputs/step8_prescribed_moving_wall/LBMFluid_1000.vtr",
        "outputs/step8_prescribed_moving_wall/ux_profile_y.npy",
        "outputs/step8_prescribed_moving_wall/diagnostics.npz",
        "outputs/step8_projected_mpm_boundary/LBMFluid_100.vtr",
        "outputs/step8_projected_mpm_boundary/particles_x.npy",
        "outputs/step8_projected_mpm_boundary/particles_v.npy",
        "outputs/step8_projected_mpm_boundary/solid.npy",
        "outputs/step8_projected_mpm_boundary/solid_phi.npy",
        "outputs/step8_projected_mpm_boundary/diagnostics.npz",
        "outputs/step8_momentum_exchange/momentum_exchange_timeseries.npz",
        "outputs/step8_momentum_exchange/LBMFluid_500.vtr",
        "STEP8_MOVING_BOUNCEBACK_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step8_lbm_source_contains_required_interfaces():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")

    required_keywords = [
        "def step(",
        "streaming_moving_bounceback",
        "step_moving_bounceback",
        "clear_moving_boundary_diagnostics",
        "get_moving_boundary_stats",
        "bb_link_count",
        "bb_max_correction",
        "bb_net_fluid_impulse",
        "bb_net_solid_force",
        "solid_vel",
        "hydro_force",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in source]
    assert missing == []


def test_step8_scripts_do_not_use_forbidden_methods():
    source_paths = [
        ROOT / "src/mpm_lbm/sim/lbm/fluid.py",
        ROOT / "baseline_tests/run_step8_static_bounceback_regression.py",
        ROOT / "baseline_tests/run_step8_prescribed_moving_wall_couette.py",
        ROOT / "baseline_tests/run_step8_projected_mpm_moving_boundary.py",
        ROOT / "baseline_tests/run_step8_momentum_exchange_diagnostics.py",
    ]
    forbidden_tokens = [
        "two_phase",
        "contact_angle",
        "ReducedSquidFSI",
    ]

    offenders = []
    existing_paths = [path for path in source_paths if path.is_file()]
    for path in existing_paths:
        source = path.read_text(encoding="utf-8")
        offenders.extend(f"{path.name}: {token}" for token in forbidden_tokens if token in source)
    assert offenders == []


def test_step8_logs_record_successful_baselines():
    static_log = read_log(ROOT / "logs/step8_static_bounceback_regression.log")
    moving_wall_log = read_log(ROOT / "logs/step8_prescribed_moving_wall.log")
    projected_log = read_log(ROOT / "logs/step8_projected_mpm_boundary.log")
    momentum_log = read_log(ROOT / "logs/step8_momentum_exchange.log")
    combined_logs = "\n".join([static_log, moving_wall_log, projected_log, momentum_log])

    assert "[OK] Step 8 static bounce-back regression finished" in static_log
    assert "[OK] Step 8 prescribed moving wall Couette finished" in moving_wall_log
    assert "[OK] Step 8 projected MPM moving boundary finished" in projected_log
    assert "[OK] Step 8 momentum-exchange diagnostics finished" in momentum_log

    required_log_tokens = [
        "bb_link_count",
        "bb_max_correction",
        "bb_net_fluid_impulse_x",
        "bb_net_solid_force_x",
        "cell_force_max_norm=0.000000000e+00",
    ]
    missing = [token for token in required_log_tokens if token not in combined_logs]
    assert missing == []


def test_step8_report_acceptance_complete():
    report = (ROOT / "STEP8_MOVING_BOUNCEBACK_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 8 final commit",
        "- [x] original lbm.step() still exists",
        "- [x] lbm.step_moving_bounceback() exists",
        "- [x] LBMFluid3D.streaming_moving_bounceback() exists",
        "- [x] LBMFluid3D.clear_moving_boundary_diagnostics() exists",
        "- [x] LBMFluid3D.get_moving_boundary_stats() exists",
        "- [x] bb_link_count field exists",
        "- [x] bb_max_correction field exists",
        "- [x] bb_net_fluid_impulse field exists",
        "- [x] bb_net_solid_force field exists",
        "- [x] zero wall velocity moving bounce-back is close to static bounce-back",
        "- [x] prescribed moving wall drives fluid along wall velocity",
        "- [x] projected MPM moving boundary drives fluid along projected solid velocity",
        "- [x] moving wall +x gives bb_net_fluid_impulse_x > 0",
        "- [x] moving wall +x gives bb_net_solid_force_x < 0",
        "- [x] link-wise force balance error is small",
        "- [x] hydro_force is nonzero for moving wall diagnostics",
        "- [x] cell_force remains zero in Step 8 moving-bounceback baselines",
        "- [x] PenaltyFSICoupler3D is not used in Step 8 moving-bounceback baselines",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] logs are saved under logs/",
        "- [x] outputs are saved under outputs/",
        "- [x] STEP8_MOVING_BOUNCEBACK_REPORT.md is complete",
        "- [x] pytest -q passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
