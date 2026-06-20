# Step 41 Controlled Jet-Cycle Proxy Selected-Parameter 64 Feasibility

Step 41 is controlled jet-cycle proxy selected-parameter 64^3 feasibility.
Step 41 selects one accepted wall velocity scale from Step 40.
Step 41 remains tethered and proxy-only.
Step 41 does not validate a real jet.
Step 41 does not validate jet propulsion.
Step 41 does not implement free-body motion.
Step 41 does not implement squid swimming.
Step 41 does not implement real squid validation.
Step 41 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Matrix

Step 41 runs one `64^3` cycle with `n_lbm_steps = 40`, `mpm_substeps_per_lbm_step = 5`, and `n_particles = 4096`.

The selected wall-velocity application config is:

- `configs/step41_wall_velocity_application_scale_0050_64.json`

It keeps `wall_velocity_scale = 0.05`, `wall_velocity_cap_lbm = 0.01`, `application_policy = additive_capped`, applies only to `lbm.solid_vel`, and leaves LBM populations, MPM state, projection, and bounce-back formulas unchanged.

The four driver rows are:

- `configs/step41_64_static_moving_boundary.json`
- `configs/step41_64_experimental_moving_boundary_scale_0050.json`
- `configs/step41_64_static_link_area.json`
- `configs/step41_64_experimental_link_area_scale_0050.json`

All four rows use `target_u_lbm = [0.0, 0.0, 0.0]`, strict quality checks, no VTK output, and no particle output. The Step 41 64^3 configs use `dynamic_solid_threshold = 0.75` as a configuration-level boundary activation threshold; this keeps the selected Step 40 wall-velocity scale and cap unchanged.

## Results

The driver wrote `outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json`.

Summary:

- `row_count = 4`
- `stable_count = 4`
- `quality_pass_count = 4`
- `static_row_count = 2`
- `experimental_row_count = 2`
- `engineering_row_count = 2`
- `link_area_row_count = 2`
- `min_completed_lbm_steps = 40`
- `min_total_mpm_substeps = 200`
- `min_rho_min_global = 0.9690961241722107`
- `max_rho_max_global = 1.0409393310546875`
- `max_lbm_max_v_global = 0.012116076424717903`
- `min_mpm_min_J_global = 0.9959453344345093`
- `min_projected_mass_min = 0.02294033206999302`
- `max_applied_velocity_norm = 0.00721642344030184`

The 64^3 feasibility summary wrote `outputs/step41_64_feasibility_summary/feasibility_summary.json` with `feasibility_pass = true`.

## Comparison Outputs

Static vs experimental 64^3 comparison:

- output: `outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.json`
- `row_count = 2`
- `comparison_pass = true`
- both experimental rows had positive applied velocity and finite bounded deltas

Engineering vs link-area 64^3 comparison:

- output: `outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.json`
- `row_count = 1`
- `comparison_pass = true`
- `link_area_scale_final = 0.8088821768760681`
- `max_applied_velocity_norm_delta = 0.0`

## Wall Velocity And Cycle Proxy

Wall-velocity quality wrote `outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json`.

- `row_count = 2`
- `quality_pass = true`
- `selected_scale = 0.05`
- `cap_value = 0.01`
- `min_timeseries_row_count = 40`
- `min_applied_cell_count = 5056`
- `max_applied_velocity_norm = 0.00721642344030184`
- `max_lbm_population_update_count = 0`

Cycle proxy diagnostics wrote `outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json`.

- `cycle_period_steps = 40`
- `cycle_count = 1`
- `cycle_proxy_64_pass = true`
- `phase_alignment_pass = true`
- `cavity_volume_cycle_pass = true`
- `funnel_aperture_cycle_pass = true`
- `expelled_volume_proxy = 0.0027022723369117957`
- `refill_volume_proxy = 0.0027022723369117957`
- `net_cycle_volume_proxy = 0.0`

## Guards

The tethered no-free-body guard wrote `outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json` with `guard_pass = true`, `free_body_state_file_count = 0`, and `body_trajectory_output_count = 0`.

The Step 40 regression guard wrote `outputs/step41_step40_regression_guard/step40_regression_guard.json` with `regression_pass = true`.

The artifact manifest wrote `outputs/step41_artifact_manifest/artifact_summary.json` with `large_file_count = 0`, `step41_total_size_mb = 3.450411796569824`, and `total_size_mb = 161.83606433868408`.

## Interpretation Boundary

Step 41 supports only this controlled statement: the existing tethered moving-wall proxy path can run one selected `0.05` wall-velocity-scale cycle at `64^3` with finite, bounded diagnostics and strict quality reports.

The result is a feasibility artifact for the existing proxy path. It is not a free-body, swimming, propulsion, two-phase, contact-angle, or production solver claim.
