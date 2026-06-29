# Step148 Goal: Our-Solver Fluent Official Case Reproduction

## Source Contract

This step changes direction after Step147. It must not continue the LBM-only
outlet-controller repair line.

Step147 facts to preserve:

- Step147 ran exactly four `48^3 / 250-step` LBM-only rows.
- The relief rows improved short-window mass and flow metrics but reported
  compact x-profile collapse at x=24, step 240.
- `step148_500step_probe_proposal_allowed = false`.
- selected96, selected-static, `96^3`, Fluent, FSI validation, and validation
  claims remain blocked.

Step148 is not a Fluent run and not a design-only report. It must use this
repository's own MPM-LBM/FSI solver path to run a bounded reproduction of the
Fluent official two-way FSI duct/flap case and emit solver-side monitors for
later error localization.

The checked source ref from the prior pushed Step147 baseline is:

```text
origin/main = 67e05ebbce10e92f5331dde20b424e7b5c081b7b
```

## Hard Scope Boundaries

Step148 must:

- Run our solver, not Fluent.
- Use an FSI driver / MPM-LBM coupling path, not Step121.
- Produce real solver-side monitor artifacts.
- Preserve private official payload boundaries.
- Keep validation and selected-boundary claims blocked.

Step148 must not:

- Use `planeflux_saturation_stationarity48`.
- Use any Step121 phase or LBM-only row.
- Run selected96 or selected-static.
- Run a `96^3` row.
- Run a 500-step LBM-only probe.
- Commit official Fluent payloads, meshes, journals, or monitor CSVs.
- Claim Fluent parity, Figure 29.3 parity, FSI validation, or production
  readiness.
- Hide a failed solver launch behind a design-only artifact.

## Private Official Input Boundary

Official inputs may exist locally only under:

```text
benchmarks/private/fluent_fsi_2way/
```

Expected optional local files:

```text
benchmarks/private/fluent_fsi_2way/fsi_2way.zip
benchmarks/private/fluent_fsi_2way/flap.msh
benchmarks/private/fluent_fsi_2way/steady_fluid_flow.jou
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

If `official_monitor.csv` is missing, Step148 still runs our solver and Step149
must report `official_reference_missing` / `missing_official_monitor` rather
than fabricate comparison metrics.

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/148/goal.md
docs/campaigns/fluent_duct_flap/steps/148/report.md
experiments/steps/step148_our_solver_fluent_official_case_reproduction.py
tests/test_step148_our_solver_fluent_official_case_reproduction_contract.py
```

Generate:

```text
outputs/step148_our_solver_fluent_official_case/solver_run_manifest.json
outputs/step148_our_solver_fluent_official_case/solver_case_mapping_report.json
outputs/step148_our_solver_fluent_official_case/solver_monitor.csv
outputs/step148_our_solver_fluent_official_case/solver_force_monitor.csv
outputs/step148_our_solver_fluent_official_case/solver_reproduction_summary.json
outputs/step148_our_solver_fluent_official_case/geometry_mapping_report.json
outputs/step148_our_solver_fluent_official_case/unit_mapping_report.json
outputs/step148_our_solver_fluent_official_case/coupling_diagnostics_summary.json
```

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
README.md
```

## Runner Command

The runner must support:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step148_our_solver_fluent_official_case_reproduction `
  --official-private-root benchmarks\private\fluent_fsi_2way `
  --output-dir outputs\step148_our_solver_fluent_official_case `
  --grid 48 `
  --n-steps 250 `
  --force
```

For local/contract tests, it may also support smaller grids and shorter windows,
but the committed Step148 artifact must be from the bounded `grid = 48`,
`n_steps = 250` command unless a concrete failure stage prevents completion.

## Required Step148 Implementation Shape

Implement a step-specific wrapper with explicit functions:

```python
create_fluent_official_proxy_fsi_config()
run_our_solver_fsi_case()
extract_solver_monitors()
write_solver_case_mapping_report()
```

If official mesh import is unavailable, report:

```json
{
  "official_geometry_mode": "proxy_from_current_fluent_duct_flap",
  "official_mesh_imported": false,
  "geometry_gap_reported": true
}
```

This fallback is acceptable only if the solver run is real and monitor outputs
are generated from our MPM-LBM/FSI path.

## Solver Configuration Requirements

Fluid:

- Duct/flap geometry from official/private mesh metadata if available.
- Otherwise use the current procedural duct/flap proxy.
- Inlet velocity maps to the official tutorial inlet velocity.
- Outlet pressure maps to the official pressure outlet.
- Viscosity/Re mapping uses existing Fluent-like mapping surfaces.

Solid:

- Flap geometry mapped from official mesh/proxy.
- Fixed-base constraint.
- Material density, Young's modulus, and damping from existing Fluent proxy
  configuration.
- Monitor point is the official/proxy flap tip.

Coupling:

- Two-way MPM-LBM path attempted.
- Use the strongest currently implemented FSI mode, such as moving-boundary or
  the current production-like FSI driver mode.
- Force accumulation enabled.
- Monitor fluid force on the flap.
- Monitor flap-tip displacement and velocity.

## Required Monitor Columns

`solver_monitor.csv` and/or `solver_force_monitor.csv` must expose these
schema-compatible columns:

```text
time_s
step
flap_tip_total_displacement_m
flap_tip_x_displacement_m
flap_tip_y_displacement_m
flap_tip_velocity_m_per_s
fluid_force_x_n
fluid_force_y_n
fluid_force_magnitude_n
```

## Required Summary Fields

`solver_reproduction_summary.json` must include:

```json
{
  "step": 148,
  "our_solver_run_executed": true,
  "solver_monitor_found": true,
  "solver_monitor_rows": "> 0",
  "fsi_coupling_mode": "...",
  "fluid_solver": "LBM",
  "solid_solver": "MPM",
  "two_way_coupling_attempted": true,
  "official_payload_committed": false,
  "official_monitor_committed": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

If the solver cannot run, the summary must set `our_solver_run_executed = false`
and use a concrete `failure_stage`:

```text
geometry_mapping_failed
unit_mapping_failed
fsi_driver_launch_failed
nonfinite
monitor_extraction_failed
coupling_force_missing
solid_motion_missing
```

## Step148 Contract Tests

Add tests that prove:

1. The runner is not a Step121 wrapper and does not reference Step121 phases.
2. The runner exposes the required wrapper functions.
3. A tiny/short test run either executes our solver and writes monitors or fails
   with a concrete `failure_stage`.
4. `solver_monitor.csv` has all required monitor columns when the run executes.
5. Geometry, unit, mapping, and coupling diagnostic reports are written.
6. Private official payloads are never committed.
7. Summary flags keep validation, selected96, selected-static, Fluent parity,
   FSI validation, and production readiness blocked.
8. Current docs record that the active track moved away from LBM-only outlet
   repair and toward our-solver official-case reproduction.

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step148-red `
  tests\test_step148_our_solver_fluent_official_case_reproduction_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step148_our_solver_fluent_official_case_reproduction `
  --official-private-root benchmarks\private\fluent_fsi_2way `
  --output-dir outputs\step148_our_solver_fluent_official_case `
  --grid 48 `
  --n-steps 250 `
  --force

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step148-focused `
  tests\test_step148_our_solver_fluent_official_case_reproduction_contract.py
```

## Completion Criteria

Step148 is complete only when:

- The goal is committed under this path.
- A RED contract test fails before implementation.
- Step148 runner exists and is not Step121/LBM-only.
- Step148 executes our solver or reports a concrete failure stage.
- Committed Step148 artifacts include the required manifests/reports/monitors.
- Current docs point to Step148 as the active track.
- Validation and selected-boundary claims remain blocked.
- Focused tests pass.
- JSON artifacts load successfully.
- `git diff --check` passes.
- The final commit is pushed to `origin/main`, with remote ref proof.
