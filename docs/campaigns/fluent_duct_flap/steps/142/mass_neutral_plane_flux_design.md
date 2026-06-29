# Step142 Mass-Neutral Plane-Flux Controller Design

## Scope

Step142 is a design and contract step only. It introduces a default-disabled
mass-neutral plane-flux controller surface and report artifacts for a future
diagnostic. It does not run a real 48^3 row, does not run 500 steps, does not
modify Step121 phases, and does not enable selected96.

## Source Decision

Step141 reported:

```text
decision_case = density_feedback_isolation_insufficient
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

Therefore Step142 must stay in a design-only envelope. The next executable
proposal, if accepted later, is a bounded Step143 48^3 / 250-step diagnostic,
not a Step142 500-step final-evidence row.

## Design A

Design A is the preferred future runtime design:

```text
mode = global_mass_error_density_offset
mass_error = (mass_total - mass_initial) / mass_initial
rho_mass_feedback = clamp(-gain_mass * mass_error, -cap_mass, cap_mass)
target_rho = outlet_rho + rho_mass_feedback + existing_rho_feedback
```

The intended controller is global and mass-neutral in sign. Positive accumulated
mass reduces outlet target density through a bounded feedback term; negative
mass drift increases it. This design should be activated only in a later real
diagnostic step after Step142's report-only contract is accepted.

Default-disabled config fields:

```text
open_boundary_mass_neutral_flux_control_enabled = false
open_boundary_mass_neutral_flux_control_mode = disabled
open_boundary_mass_neutral_mass_error_gain = 0.0
open_boundary_mass_neutral_mass_error_cap = 0.0
open_boundary_mass_neutral_correction_blend = 0.0
open_boundary_mass_neutral_reference_mass_mode = initial
```

Allowed modes:

```text
disabled
global_mass_error_density_offset
outlet_population_projection_report_only
```

## Design B

Design B is a fallback telemetry design:

```text
mode = outlet_population_projection_report_only
```

It is report-only in Step142. It may expose planned outlet-population projection
telemetry, but it must not write populations, change boundary reconstruction, or
claim physical repair in Step142.

## Activation Boundary

Step142 leaves runtime behavior inactive:

```text
mass_neutral_runtime_behavior_active = false
step142_real_48_run_executed = false
step142_500step_run_executed = false
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

No Step121 phase named `planeflux_mass_neutral_design48` is added in Step142.
That name is only a future Step143 phase proposal.
