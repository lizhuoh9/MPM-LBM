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


def test_step9_required_artifacts_exist():
    required_paths = [
        "src/moving_boundary_coupling.py",
        "baseline_tests/run_step9_moving_boundary_reaction_field.py",
        "baseline_tests/run_step9_moving_boundary_two_way_mpm_reaction.py",
        "baseline_tests/run_step9_moving_boundary_coupled_smoke.py",
        "baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py",
        "logs/step9_mb_reaction_field.log",
        "logs/step9_mb_two_way_reaction.log",
        "logs/step9_mb_coupled_smoke.log",
        "logs/step9_compare_modes.log",
        "outputs/step9_mb_reaction_field/LBMFluid_0.vtr",
        "outputs/step9_mb_reaction_field/grid_f_ext.npy",
        "outputs/step9_mb_reaction_field/hydro_force.npy",
        "outputs/step9_mb_reaction_field/diagnostics.npz",
        "outputs/step9_mb_two_way_reaction/particles_x.npy",
        "outputs/step9_mb_two_way_reaction/particles_v.npy",
        "outputs/step9_mb_two_way_reaction/particles_F.npy",
        "outputs/step9_mb_two_way_reaction/particles_J.npy",
        "outputs/step9_mb_two_way_reaction/diagnostics.npz",
        "outputs/step9_mb_coupled_smoke/LBMFluid_20.vtr",
        "outputs/step9_mb_coupled_smoke/particles_x.npy",
        "outputs/step9_mb_coupled_smoke/particles_v.npy",
        "outputs/step9_mb_coupled_smoke/particles_F.npy",
        "outputs/step9_mb_coupled_smoke/particles_J.npy",
        "outputs/step9_mb_coupled_smoke/diagnostics_timeseries.npz",
        "outputs/step9_compare_modes/comparison_results.csv",
        "outputs/step9_compare_modes/comparison_results.npz",
        "STEP9_MOVING_BOUNDARY_REACTION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step9_source_contains_required_interfaces():
    source = (ROOT / "src/moving_boundary_coupling.py").read_text(encoding="utf-8")
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    lbm_source = (ROOT / "src/lbm_fluid.py").read_text(encoding="utf-8")

    required_keywords = [
        "class MovingBoundaryFSICoupler3D",
        "add_moving_boundary_reaction_to_mpm_grid",
        "clear_reaction_diagnostics",
        "force_density_scale_lbm_to_norm",
        "reaction_scale",
        "force_cap_norm",
        "phi_min",
        "grid_f_ext",
        "hydro_force",
        "bb_link_count",
        "active_reaction_particle_count",
        "net_particle_reaction_force",
        "net_grid_reaction_force",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in source + lbm_source]
    assert missing == []
    assert "MovingBoundaryFSICoupler3D" in init_source


def test_step9_scripts_respect_mode_boundaries():
    moving_boundary_scripts = [
        ROOT / "baseline_tests/run_step9_moving_boundary_reaction_field.py",
        ROOT / "baseline_tests/run_step9_moving_boundary_two_way_mpm_reaction.py",
        ROOT / "baseline_tests/run_step9_moving_boundary_coupled_smoke.py",
    ]
    comparison_script = ROOT / "baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py"
    source_paths = [
        ROOT / "src/moving_boundary_coupling.py",
        *moving_boundary_scripts,
        comparison_script,
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

    for path in moving_boundary_scripts:
        if path.is_file():
            source = path.read_text(encoding="utf-8")
            if "PenaltyFSICoupler3D" in source:
                offenders.append(f"{path.name}: PenaltyFSICoupler3D")

    if comparison_script.is_file():
        comparison_source = comparison_script.read_text(encoding="utf-8")
        assert "PenaltyFSICoupler3D" in comparison_source

    assert offenders == []


def test_step9_logs_record_successful_baselines():
    reaction_log = read_log(ROOT / "logs/step9_mb_reaction_field.log")
    two_way_log = read_log(ROOT / "logs/step9_mb_two_way_reaction.log")
    smoke_log = read_log(ROOT / "logs/step9_mb_coupled_smoke.log")
    compare_log = read_log(ROOT / "logs/step9_compare_modes.log")
    combined_logs = "\n".join([reaction_log, two_way_log, smoke_log, compare_log])

    assert "[OK] Step 9 moving-boundary reaction field finished" in reaction_log
    assert "[OK] Step 9 moving-boundary MPM reaction finished" in two_way_log
    assert "[OK] Step 9 moving-boundary coupled smoke finished" in smoke_log
    assert "[OK] Step 9 penalty vs moving-boundary comparison finished" in compare_log

    required_log_tokens = [
        "active_reaction_particle_count",
        "net_grid_reaction_force_x",
        "cell_force_max_norm=0.000000000e+00",
        "bb_link_count",
    ]
    missing = [token for token in required_log_tokens if token not in combined_logs]
    assert missing == []


def test_step9_report_acceptance_complete():
    report = (ROOT / "STEP9_MOVING_BOUNDARY_REACTION_REPORT.md").read_text(encoding="utf-8")

    required_checks = [
        "- [x] main is on the Step 9 final commit",
        "- [x] src/moving_boundary_coupling.py exists",
        "- [x] src/__init__.py exports MovingBoundaryFSICoupler3D",
        "- [x] MovingBoundaryFSICoupler3D exists",
        "- [x] clear_reaction_diagnostics() exists",
        "- [x] add_moving_boundary_reaction_to_mpm_grid() exists",
        "- [x] force_density_scale_lbm_to_norm is documented and used",
        "- [x] moving-boundary hydro_force can write to MPMSolid3D.grid_f_ext",
        "- [x] reaction field baseline completes",
        "- [x] reaction field baseline has active_reaction_particle_count > 0",
        "- [x] reaction field baseline has net_grid_reaction_force_x < 0 for +x moving solid",
        "- [x] two-way MPM reaction baseline completes",
        "- [x] two-way MPM reaction baseline shows final_solid_mean_vx_norm < initial_solid_mean_vx_norm",
        "- [x] moving-boundary coupled smoke completes 20 LBM steps",
        "- [x] moving-boundary coupled smoke completes 200 MPM substeps",
        "- [x] comparison baseline completes",
        "- [x] comparison baseline shows penalty mode stable",
        "- [x] comparison baseline shows moving-boundary mode stable",
        "- [x] moving-boundary mode keeps cell_force_max_norm == 0",
        "- [x] moving-boundary mode has bb_link_count > 0",
        "- [x] penalty mode has cell_force_max_norm > 0",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] mpm_max_speed < 10",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] logs are saved under logs/",
        "- [x] outputs are saved under outputs/",
        "- [x] STEP9_MOVING_BOUNDARY_REACTION_REPORT.md is complete",
        "- [x] pytest -q passes",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
