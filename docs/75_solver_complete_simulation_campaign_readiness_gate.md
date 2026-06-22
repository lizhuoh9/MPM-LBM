# Step75 Solver-Complete Simulation Campaign Readiness Gate

Step75 closes the Step71 through Step74 audit sequence with a gate-only
readiness decision. It aggregates committed evidence and produces a bounded
decision for the next step.

## Scope

Step75 may:

- read committed Step71, Step72, Step73, and Step74 artifacts
- verify that all activation gates remain closed
- record an inactive Step76 minimal safe rebaseline campaign proposal
- emit lightweight JSON, CSV, log, and Markdown evidence

Step75 may not:

- run `FSIDriver3D`
- call `driver.initialize`, `driver.step_once`, or `driver.run`
- execute projection smoke
- activate runtime geometry, wall velocity, real geometry, or squid proxy paths
- add 48^3 or 64^3 rows
- write VTR or particle NPY outputs
- edit `external/taichi_LBM3D` or `data/real_geometry_candidates`
- change solver formulas, tau semantics, or production-readiness claims

## Decision

```text
gate_status = ready_for_step76_rebaseline_only
post_gate_simulation_allowed = true
allowed_next_step = Step76
allowed_next_step_scope = minimal safe rebaseline only
activation_features_allowed_in_next_step = []
```

The decision is intentionally narrow. Step76 may start from one minimal
32^3/one-step moving-boundary engineering rebaseline row. All advanced
activation features remain disabled.

## Evidence Files

- `outputs/step75_precondition_artifact_audit/precondition_artifact.json`
- `outputs/step75_activation_gate_closure_audit/activation_gate_closure.json`
- `outputs/step75_post_gate_campaign_policy_audit/post_gate_campaign_policy.json`
- `outputs/step75_solver_complete_gate_audit/solver_complete_gate.json`
- `outputs/step75_no_simulation_audit/no_simulation.json`
- `outputs/step75_output_artifact_policy_audit/output_artifact_policy.json`
- `outputs/step75_step74_regression_guard/step74_regression_guard.json`
- `outputs/step75_artifact_manifest/artifact_summary.json`

## Interpretation

Step75 means the repository has enough audit evidence to attempt a very small
Step76 rebaseline. It does not mean the solver is physically validated, ready
for production, ready for real squid geometry, or ready for larger grids.
