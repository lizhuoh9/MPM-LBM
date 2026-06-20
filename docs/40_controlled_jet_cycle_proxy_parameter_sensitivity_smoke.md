# Step 40 Controlled Jet-Cycle Proxy Parameter Sensitivity Smoke

Step 40 is controlled jet-cycle proxy parameter sensitivity smoke.
Step 40 varies wall velocity scale only.
Step 40 remains tethered and proxy-only.
Step 40 does not validate a real jet.
Step 40 does not validate jet propulsion.
Step 40 does not implement free-body motion.
Step 40 does not implement squid swimming.
Step 40 does not implement real squid validation.
Step 40 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Matrix

Step 40 runs a one-cycle `48^3` parameter smoke with `n_lbm_steps = 40` and `mpm_substeps_per_lbm_step = 5`.

The static baseline rows are:

- `configs/step40_static_48_moving_boundary.json`
- `configs/step40_static_48_link_area.json`

The experimental rows use `solid_vel_experimental` wall-velocity application over:

- `wall_velocity_scale = 0.025`
- `wall_velocity_scale = 0.05`
- `wall_velocity_scale = 0.075`

Each scale is tested for both `engineering` and `link_area_experimental` transfer.

## Parameter Controls

The Step 40 application configs are:

- `configs/step40_wall_velocity_application_scale_0025.json`
- `configs/step40_wall_velocity_application_scale_0050.json`
- `configs/step40_wall_velocity_application_scale_0075.json`

All three use `wall_velocity_cap_lbm = 0.01`, apply only to `lbm.solid_vel`, do not update LBM populations, do not apply to MPM or projection, and do not modify bounce-back formulas.

## Results

The parameter-sweep driver wrote `outputs/step40_parameter_sweep_driver/parameter_sweep_results.json`.

Summary:

- `row_count = 8`
- `stable_count = 8`
- `static_row_count = 2`
- `experimental_row_count = 6`
- `scale_count = 3`
- `transfer_mode_count = 2`
- `min_completed_lbm_steps = 40`
- `min_total_mpm_substeps = 200`
- `min_rho_min_global = 0.9828528761863708`
- `max_rho_max_global = 1.0134063959121704`
- `max_lbm_max_v_global = 0.01099871564656496`
- `min_mpm_min_J_global = 0.9909236431121826`
- `max_applied_velocity_norm = 0.00967813097947864`

The applied wall velocity increased with scale and stayed below the configured cap. No cap hit was observed in this smoke.

## Output Families

Step 40 writes:

- parameter config validation outputs
- parameter sweep driver outputs
- parameter sensitivity summary outputs
- static-vs-parameter comparison outputs
- engineering-vs-link-area comparison outputs
- cap saturation diagnostic outputs
- force and impulse proxy response outputs
- tethered no-free-body guard outputs
- quality report aggregation outputs
- Step 39 regression guard outputs
- artifact manifest outputs

## Interpretation Boundary

The Step 40 results support only a controlled proxy statement: the existing tethered moving-wall application path stays finite, stable, cap-respecting, and diagnostically bounded across the tested wall-velocity scales.

The results do not establish physical propulsion accuracy, body translation, or a production sharp-interface solver claim.
