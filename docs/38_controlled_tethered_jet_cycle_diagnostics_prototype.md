# Step 38 Controlled Tethered Jet-Cycle Diagnostics Prototype

Step 38 is controlled tethered jet-cycle diagnostics prototype.

Step 38 uses proxy cavity-volume and funnel-aperture diagnostics only.
Step 38 does not validate a real jet.
Step 38 does not implement free-body motion.
Step 38 does not implement squid swimming.
Step 38 does not implement real squid validation.
Step 38 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Scope

Step 38 extends the Step 37 accepted wall-velocity application path from a 20-step short-window envelope to one 40-step prescribed kinematic cycle. The work remains tethered because all diagnostics are evaluated in the fixed simulation frame with zero background target velocity and no body-position integration state.

The driver matrix is:

- `static_48_moving_boundary`: static boundary motion, engineering transfer.
- `experimental_48_moving_boundary`: prescribed kinematics plus opt-in `solid_vel_experimental`, engineering transfer.
- `static_48_link_area`: static boundary motion, link-area transfer.
- `experimental_48_link_area`: prescribed kinematics plus opt-in `solid_vel_experimental`, link-area transfer.

All four rows use 48^3, 4096 particles, 40 LBM steps, 5 MPM substeps per LBM step, strict geometry quality checks, no VTK output, no particle output, and zero `target_u_lbm`.

## Results

The cycle driver wrote `outputs/step38_cycle_driver/cycle_driver_results.json` with `row_count=4`, `stable_count=4`, `quality_pass_count=4`, `min_completed_lbm_steps=40`, and `min_total_mpm_substeps=200`.

The global driver envelope remained bounded:

- `min_rho_min_global=0.9873017072677612`
- `max_rho_max_global=1.0107487440109253`
- `max_lbm_max_v_global=0.007916591130197048`
- `min_mpm_min_J_global=0.9909240007400513`
- `min_projected_mass_min=0.02294033393263817`
- `min_active_cell_count=4856`
- `min_bb_link_count_max=6652`

The two experimental rows each wrote 40 wall-velocity application reports. The maximum applied velocity norm was `0.007021783310068709`, below the configured cap of `0.01`, and `lbm_population_update_count` stayed zero.

The schedule-derived cycle proxy wrote `outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.json` with `cycle_period_steps=40`, `schedule_row_count=81`, `phase_alignment_pass=true`, `cavity_volume_cycle_pass=true`, and `funnel_aperture_cycle_pass=true`.

The cavity proxy remained closed over the cycle:

- `cavity_volume_scale_min=0.6`
- `cavity_volume_scale_max=1.0`
- `expelled_volume_proxy=0.0027022723369117957`
- `refill_volume_proxy=0.0027022723369117957`
- `net_cycle_volume_proxy=0.0`

The funnel proxy opened and closed:

- `funnel_aperture_min=0.35`
- `funnel_aperture_max=1.0`
- `funnel_open_sample_count=27`
- `funnel_closed_or_rest_sample_count=54`

The force and impulse-proxy summary wrote four passing rows. These are existing-diagnostics integrals only; they are not a propulsion model.

## Artifacts

Primary artifacts:

- `configs/step38_cycle_static_48_moving_boundary.json`
- `configs/step38_cycle_experimental_48_moving_boundary.json`
- `configs/step38_cycle_static_48_link_area.json`
- `configs/step38_cycle_experimental_48_link_area.json`
- `src/jet_cycle_proxy_diagnostics.py`
- `src/tethered_cycle_diagnostics.py`
- `baseline_tests/step38_common.py`
- `baseline_tests/run_step38_cycle_driver.py`
- `baseline_tests/run_step38_cycle_proxy_diagnostics.py`
- `baseline_tests/run_step38_static_vs_experimental_cycle_comparison.py`
- `baseline_tests/run_step38_engineering_vs_link_area_cycle_comparison.py`
- `baseline_tests/run_step38_wall_velocity_cycle_quality.py`
- `baseline_tests/run_step38_force_impulse_proxy_summary.py`
- `baseline_tests/run_step38_tethered_no_free_body_guard.py`
- `baseline_tests/run_step38_quality_report_aggregation.py`
- `baseline_tests/run_step38_step37_regression_guard.py`
- `baseline_tests/run_step38_artifact_manifest.py`
- `tests/test_step38_tethered_jet_cycle_diagnostics_contract.py`

Output artifacts are under `outputs/step38_*` and logs are under `logs/step38_*`.

## Decision

Step 38 can be accepted when the recorded verification commands pass and the commit is pushed. A reasonable next step is a controlled multi-cycle proxy stability envelope that repeats the same tethered diagnostics over two or three prescribed cycles without adding free-body motion or swimming claims.
