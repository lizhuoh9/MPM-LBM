# Step 36 Controlled Moving-Wall Bounce-Back Velocity Application Smoke

## Scope

Step 36 is controlled moving-wall bounce-back velocity application smoke.

Step 36 is opt-in and experimental. It applies wall velocity only through the existing `solid_vel` channel after projection updates `lbm.solid_vel` and before `step_moving_bounceback()` consumes that field.

Step 36 does not change moving bounce-back formulas. Step 36 does not update LBM populations outside the existing bounce-back step. Step 36 does not implement a jet model. Step 36 does not implement squid swimming. Step 36 does not implement real squid validation.

The default `boundary_motion_mode` remains static. The default `wall_velocity_application_mode` remains disabled. The default `quality_check_enabled` remains false. The default `quality_check_strict` remains false. The default `reaction_transfer_mode` remains engineering.

## Implementation

The application path is guarded by `wall_velocity_application_mode == "solid_vel_experimental"` and `wall_velocity_application_config_path == "configs/step36_wall_velocity_application_solid_vel_experimental.json"`.

The Step 36 application config validates that:

- `target_lbm_field == "solid_vel"`.
- `application_policy == "additive_capped"`.
- `wall_velocity_scale == 0.05`.
- `wall_velocity_cap_lbm == 0.01`.
- `apply_to_lbm_solid_vel == true`.
- `apply_to_lbm_populations == false`.
- `modify_bounceback_formula == false`.

The driver writes `wall_velocity_application_report.json` only in experimental application cases. Static cases keep the application mode disabled and write no application report.

## Evidence

The accepted Step 36 evidence is under:

- `outputs/step36_wall_velocity_application_config_validation/`
- `outputs/step36_wall_velocity_application_report/`
- `outputs/step36_static_regression_smoke/`
- `outputs/step36_experimental_application_smoke/`
- `outputs/step36_static_vs_experimental_comparison/`
- `outputs/step36_mass_force_stability_diagnostics/`
- `outputs/step36_wall_velocity_application_quality/`
- `outputs/step36_quality_report_aggregation/`
- `outputs/step36_step35_regression_guard/`
- `outputs/step36_artifact_manifest/`

The smoke set contains three static rows and three experimental rows: 32^3 moving-boundary engineering, 48^3 moving-boundary engineering, and 48^3 moving-boundary link-area.

## Limits

Step 36 is a short controlled smoke. It is not a production solver claim, not a propulsion model, not a free-body model, and not real squid validation. It only verifies that a capped diagnostic wall velocity can be applied to `lbm.solid_vel` without destabilizing the short moving-boundary smoke cases.
