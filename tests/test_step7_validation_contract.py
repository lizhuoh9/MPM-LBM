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


def test_step7_required_artifacts_exist():
    required_paths = [
        "src/mpm_lbm/diagnostics/fsi_diagnostics.py",
        "baseline_tests/run_step7_couette_like_validation.py",
        "baseline_tests/run_step7_momentum_impulse_diagnostics.py",
        "baseline_tests/run_step7_beta_sweep.py",
        "baseline_tests/run_step7_long_coupled_stability.py",
        "logs/step7_couette_like.log",
        "logs/step7_momentum_impulse.log",
        "logs/step7_beta_sweep.log",
        "logs/step7_long_stability.log",
        "outputs/step7_couette_like/LBMFluid_100.vtr",
        "outputs/step7_couette_like/particles_x.npy",
        "outputs/step7_couette_like/particles_v.npy",
        "outputs/step7_couette_like/ux_profile_y.npy",
        "outputs/step7_couette_like/diagnostics.npz",
        "outputs/step7_momentum_impulse/diagnostics_timeseries.npz",
        "outputs/step7_momentum_impulse/LBMFluid_100.vtr",
        "outputs/step7_beta_sweep/beta_sweep_results.csv",
        "outputs/step7_beta_sweep/beta_sweep_results.npz",
        "outputs/step7_long_stability/LBMFluid_100.vtr",
        "outputs/step7_long_stability/particles_x.npy",
        "outputs/step7_long_stability/particles_v.npy",
        "outputs/step7_long_stability/particles_F.npy",
        "outputs/step7_long_stability/particles_J.npy",
        "outputs/step7_long_stability/diagnostics_timeseries.npz",
        "STEP7_FSI_VALIDATION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step7_diagnostics_source_contains_required_interfaces():
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    diagnostics_source = (ROOT / "src/mpm_lbm/diagnostics/fsi_diagnostics.py").read_text(encoding="utf-8")

    required_keywords = [
        "class FSIDiagnostics3D",
        "lbm_fluid_stats",
        "mpm_particle_stats",
        "projection_zone_fluid_mean_velocity",
        "far_field_fluid_mean_velocity",
        "projected_solid_mean_velocity",
        "force_stats",
        "solid_mean_velocity_norm",
        "solid_momentum_norm",
        "lbm_velocity_profile_x_over_y",
        "diagnostic-only",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in diagnostics_source]
    assert missing == []

    assert "FSIDiagnostics3D" in init_source


def test_step7_scripts_do_not_use_forbidden_methods():
    source_paths = [
        ROOT / "src/mpm_lbm/diagnostics/fsi_diagnostics.py",
        ROOT / "baseline_tests/run_step7_couette_like_validation.py",
        ROOT / "baseline_tests/run_step7_momentum_impulse_diagnostics.py",
        ROOT / "baseline_tests/run_step7_beta_sweep.py",
        ROOT / "baseline_tests/run_step7_long_coupled_stability.py",
    ]
    forbidden_tokens = [
        "moving_bounce_back",
        "momentum_exchange",
        "sharp_interface",
        "two_phase",
        "contact_angle",
        "ReducedSquidFSI",
    ]

    offenders = []
    for path in source_paths:
        source = path.read_text(encoding="utf-8")
        offenders.extend(f"{path.name}: {token}" for token in forbidden_tokens if token in source)
    assert offenders == []


def test_step7_logs_record_successful_baselines():
    couette_log = read_log(ROOT / "logs/step7_couette_like.log")
    impulse_log = read_log(ROOT / "logs/step7_momentum_impulse.log")
    beta_log = read_log(ROOT / "logs/step7_beta_sweep.log")
    long_log = read_log(ROOT / "logs/step7_long_stability.log")

    assert "[OK] Step 7 Couette-like validation finished" in couette_log
    assert "initial_projection_zone_fluid_mean_ux" in couette_log
    assert "final_projection_zone_fluid_mean_ux" in couette_log
    assert "far_field_fluid_mean_ux" in couette_log

    assert "[OK] Step 7 momentum impulse diagnostics finished" in impulse_log
    assert "max_force_balance_error" in impulse_log
    assert "mean_force_balance_error" in impulse_log
    assert "cumulative_cell_impulse_x" in impulse_log
    assert "cumulative_hydro_impulse_x" in impulse_log

    assert "[OK] Step 7 beta sweep finished" in beta_log
    assert "beta_lbm=3.000000000e-04" in beta_log
    assert "beta_lbm=1.000000000e-03" in beta_log

    assert "[OK] Step 7 long coupled stability finished" in long_log
    assert "completed_lbm_steps=100" in long_log
    assert "total_mpm_substeps=1000" in long_log


def test_step7_report_acceptance_complete():
    report = (ROOT / "STEP7_FSI_VALIDATION_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 7 final commit",
        "- [x] `src/diagnostics.py` exists",
        "- [x] `src/__init__.py` exports `FSIDiagnostics3D`",
        "- [x] `FSIDiagnostics3D.lbm_fluid_stats()` exists",
        "- [x] `FSIDiagnostics3D.mpm_particle_stats()` exists",
        "- [x] `FSIDiagnostics3D.projection_zone_fluid_mean_velocity()` exists",
        "- [x] `FSIDiagnostics3D.far_field_fluid_mean_velocity()` exists",
        "- [x] `FSIDiagnostics3D.projected_solid_mean_velocity()` exists",
        "- [x] `FSIDiagnostics3D.force_stats()` exists",
        "- [x] `FSIDiagnostics3D.solid_mean_velocity_norm()` exists",
        "- [x] `FSIDiagnostics3D.lbm_velocity_profile_x_over_y()` exists",
        "- [x] Couette-like validation passes",
        "- [x] projection zone fluid ux increases",
        "- [x] projection zone fluid ux > far-field ux",
        "- [x] global fluid ux > 0",
        "- [x] solid mean vx decreases",
        "- [x] momentum / impulse diagnostics pass",
        "- [x] force balance error is small",
        "- [x] cumulative cell impulse x > 0",
        "- [x] cumulative hydro impulse x < 0",
        "- [x] beta sweep passes",
        "- [x] beta sweep has stable 3.0e-4 row",
        "- [x] beta sweep has stable 1.0e-3 row",
        "- [x] fluid response is non-decreasing with beta within tolerance",
        "- [x] solid slowdown is non-decreasing with beta within tolerance",
        "- [x] long coupled stability completes 100 LBM steps",
        "- [x] long coupled stability completes 1000 MPM substeps",
        "- [x] active_force_cell_count > 0",
        "- [x] `rho_min > 0.95`",
        "- [x] `rho_max < 1.05`",
        "- [x] `lbm_max_v < 0.1`",
        "- [x] `mpm_min_J > 0`",
        "- [x] `mpm_max_speed < 10`",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no moving bounce-back",
        "- [x] no momentum exchange",
        "- [x] no sharp-interface FSI",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no `external/taichi_LBM3D` edits",
        "- [x] logs are saved under `logs/`",
        "- [x] outputs are saved under `outputs/`",
        "- [x] `STEP7_FSI_VALIDATION_REPORT.md` is complete",
        "- [x] `pytest -q` passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
