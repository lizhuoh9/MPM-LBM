# Step 37 Controlled Moving-Wall Application Short-Window Envelope

## Scope

Step 37 is controlled moving-wall application short-window envelope.

Step 37 remains opt-in and experimental. Step 37 uses the existing solid_vel channel. It extends the accepted Step 36 `solid_vel_experimental` application path from 5-step smoke to a 20-step short-window envelope.

Step 37 does not change moving bounce-back formulas. Step 37 does not update LBM populations outside the existing bounce-back step. Step 37 does not implement a jet model. Step 37 does not implement squid swimming. Step 37 does not implement real squid validation.

The default boundary_motion_mode remains static. The default wall_velocity_application_mode remains disabled. The default quality_check_enabled remains false. The default quality_check_strict remains false. The default reaction_transfer_mode remains engineering.

## Matrix

Step 37 runs four 48^3 rows for 20 LBM steps and 100 MPM substeps:

- Static moving-boundary engineering.
- Experimental moving-boundary engineering.
- Static moving-boundary link-area.
- Experimental moving-boundary link-area.

The experimental rows use `wall_velocity_application_mode = "solid_vel_experimental"` and write per-step `wall_velocity_application_timeseries` artifacts. Static rows keep wall velocity application disabled.

## Evidence

The accepted Step 37 evidence is under:

- `outputs/step37_application_window_driver/`
- `outputs/step37_application_envelope_summary/`
- `outputs/step37_static_vs_experimental_envelope/`
- `outputs/step37_engineering_vs_link_area_envelope/`
- `outputs/step37_mass_force_bounceback_envelope/`
- `outputs/step37_wall_velocity_timeseries_quality/`
- `outputs/step37_quality_report_aggregation/`
- `outputs/step37_step36_regression_guard/`
- `outputs/step37_artifact_manifest/`

The four driver rows completed 20 LBM steps and 100 MPM substeps. The experimental rows each wrote 20 wall velocity application reports. The maximum applied velocity norm is 0.007021783310068709, under the 0.01 cap. No direct LBM population update is reported.

## Limits

Step 37 is a short-window envelope only. It is not a jet model, not a propulsion model, not free-body motion, not squid swimming, and not real squid validation.
