# Step 39 Controlled Jet-Cycle Proxy Multi-Cycle Stability Envelope

Step 39 is controlled jet-cycle proxy multi-cycle stability envelope.

Step 39 repeats tethered proxy diagnostics over two cycles.
Step 39 does not validate a real jet.
Step 39 does not implement free-body motion.
Step 39 does not implement squid swimming.
Step 39 does not implement real squid validation.
Step 39 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Scope

Step 39 extends the Step 38 one-cycle diagnostic surface to a two-cycle, 80-step envelope. It keeps the same tethered fixed-frame setup, zero background target velocity, strict quality checks, and opt-in wall-velocity application path for experimental rows.

The driver matrix is:

- `static_48_moving_boundary`: static boundary motion, engineering transfer.
- `experimental_48_moving_boundary`: prescribed kinematics plus opt-in `solid_vel_experimental`, engineering transfer.
- `static_48_link_area`: static boundary motion, link-area transfer.
- `experimental_48_link_area`: prescribed kinematics plus opt-in `solid_vel_experimental`, link-area transfer.

All four rows use 48^3, 4096 particles, 80 LBM steps, 5 MPM substeps per LBM step, strict geometry quality checks, no VTK output, no particle output, and zero `target_u_lbm`.

## Results

The multi-cycle driver wrote `outputs/step39_multicycle_driver/multicycle_driver_results.json` with `row_count=4`, `stable_count=4`, `quality_pass_count=4`, `min_completed_lbm_steps=80`, and `min_total_mpm_substeps=400`.

The global driver envelope remained bounded:

- `min_rho_min_global=0.9870661497116089`
- `max_rho_max_global=1.0107489824295044`
- `max_lbm_max_v_global=0.008082426153123379`
- `min_mpm_min_J_global=0.9909238219261169`
- `min_projected_mass_min=0.022940337657928467`
- `min_active_cell_count=4884`
- `min_bb_link_count_max=6692`

The two experimental rows each wrote 80 wall-velocity application reports. The maximum applied velocity norm was `0.007021783310068709`, below the configured cap of `0.01`, and `lbm_population_update_count` stayed zero.

The multicycle proxy diagnostics wrote `outputs/step39_multicycle_proxy_diagnostics/multicycle_proxy_diagnostics.json` with `cycle_count=2`, `cycle_period_steps=40`, `row_count=8`, and `multicycle_proxy_pass=true`.

The cycle-to-cycle drift summary wrote `outputs/step39_cycle_to_cycle_drift_summary/cycle_to_cycle_drift.json` with `row_count=4` and all rows passing. The largest listed drifts remained inside the conservative envelope:

- `abs(projected_mass_drift) <= 5.587935447692871e-09`
- `abs(lbm_max_v_drift) <= 0.0018947357311844826`
- `abs(rho_min_drift_cycle2_minus_cycle1) <= 0.0009014010429382324`
- `abs(rho_max_drift_cycle2_minus_cycle1) <= 0.0030274391174316406`

The force and impulse-proxy summary wrote 8 passing per-cycle rows. The maximum cycle-to-cycle impulse-proxy drift was `0.014891386032104492`. These are existing-diagnostics proxies only.

## Guardrails

The tethered guard wrote `outputs/step39_tethered_no_free_body_guard/tethered_no_free_body_guard.json` and passed:

- `free_body_state_file_count=0`
- `body_trajectory_output_count=0`
- `rigid_body_integrator_enabled=false`
- `body_position_state_enabled=false`
- `swimming_displacement_claim_enabled=false`
- `target_u_lbm_zero_for_cycle_configs=true`

Step 39 keeps all solver, coupler, projection, MPM, LBM, and moving bounce-back formulas unchanged. It also leaves `external/taichi_LBM3D` untouched.

## Artifacts

Primary artifacts:

- `configs/step39_multicycle_static_48_moving_boundary.json`
- `configs/step39_multicycle_experimental_48_moving_boundary.json`
- `configs/step39_multicycle_static_48_link_area.json`
- `configs/step39_multicycle_experimental_48_link_area.json`
- `src/multicycle_proxy_diagnostics.py`
- `baseline_tests/step39_common.py`
- `baseline_tests/run_step39_multicycle_driver.py`
- `baseline_tests/run_step39_multicycle_proxy_diagnostics.py`
- `baseline_tests/run_step39_cycle_to_cycle_drift_summary.py`
- `baseline_tests/run_step39_wall_velocity_multicycle_quality.py`
- `baseline_tests/run_step39_static_vs_experimental_multicycle_comparison.py`
- `baseline_tests/run_step39_engineering_vs_link_area_multicycle_comparison.py`
- `baseline_tests/run_step39_force_impulse_multicycle_summary.py`
- `baseline_tests/run_step39_tethered_no_free_body_guard.py`
- `baseline_tests/run_step39_quality_report_aggregation.py`
- `baseline_tests/run_step39_step38_regression_guard.py`
- `baseline_tests/run_step39_artifact_manifest.py`
- `tests/test_step39_multicycle_jet_proxy_stability_contract.py`

Output artifacts are under `outputs/step39_*` and logs are under `logs/step39_*`.

## Decision

Step 39 can be accepted when the recorded verification commands pass and the commit is pushed. A reasonable next step is a controlled parameter-sensitivity smoke that keeps the same tethered proxy-only scope.
