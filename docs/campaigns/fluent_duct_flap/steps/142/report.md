# Step142 Mass-Neutral Plane-Flux Controller Design Report

## Decision

Step142 implements only the code and artifact contract for a future
mass-neutral plane-flux controller diagnostic. Step142 did not run a 500-step row.
It did not run a real 48^3 row, did not add a Step121 phase, and did not enable
selected96.

The source decision remains the Step141 audit:

```text
decision_case = density_feedback_isolation_insufficient
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

Step142 therefore blocks a direct 500-step final-evidence run. The only
proposal emitted by Step142 is a later Step143 bounded 48^3 / 250-step
diagnostic named:

```text
planeflux_mass_neutral_design48
```

That phase is not present in Step121 during Step142.

## Implemented Surface

`LBMConfig` now exposes default-disabled mass-neutral fields:

```text
open_boundary_mass_neutral_flux_control_enabled
open_boundary_mass_neutral_flux_control_mode
open_boundary_mass_neutral_mass_error_gain
open_boundary_mass_neutral_mass_error_cap
open_boundary_mass_neutral_correction_blend
open_boundary_mass_neutral_reference_mass_mode
```

The fields are threaded through Step118 config construction, Step116 config
reports, Step120 spec/report metadata, and `LBMFluid3D.get_open_boundary_limiter_stats`.
The new fields are not added to `SOLVER_STATE_HASH_FIELDS`, so existing Step141
and earlier solver-state hashes are not retroactively redefined.

## Artifacts

Step142 artifact root:

```text
outputs/step142_mass_neutral_plane_flux_design
```

Generated files:

```text
outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json
outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.md
```

The readiness report records:

```text
status = design_ready
step142_real_48_run_executed = false
step142_500step_run_executed = false
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
step143_250step_diagnostic_proposal_allowed = true
```

## Design Summary

Design A is `global_mass_error_density_offset`, planned for a future activated
diagnostic:

```text
mass_error = (mass_total - mass_initial) / mass_initial
rho_mass_feedback = clamp(-gain_mass * mass_error, -cap_mass, cap_mass)
target_rho = outlet_rho + rho_mass_feedback + existing_rho_feedback
```

Design B is `outlet_population_projection_report_only`, a fallback telemetry
surface that remains population-write-free in Step142.

## Gate State

Step142 does not claim selected 96^3, quasi-2D, FSI, Fluent validation,
Figure 29.3 parity, or production readiness. The current campaign state remains
`48_candidates_failed`.
