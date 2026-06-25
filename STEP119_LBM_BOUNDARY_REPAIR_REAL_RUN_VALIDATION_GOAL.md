# Step119 Goal: LBM Boundary Repair Real-Run Validation

## Source Context

This goal is derived from the review of remote `main` commit
`56ea7ad16a717b072387c7374ee278e267b2c847`
(`feat: add step118 lbm boundary stability repair`).

Step118 is accepted as a repair/diagnostic surface, not as proof of physical
repair success. Step118 added boundary variants, limiter fields, stability
diagnostics, a runner, tests, and schema artifacts. Its committed rows are
explicitly marked `synthetic_diagnostic_mode`, so they do not prove 48^3 or
96^3 long-window LBM stability.

## One-Sentence Objective

Use the Step118 limited/convective open-boundary variants in real,
non-synthetic LBM-only runs to determine whether the boundary repair actually
resolves the Step117 96^3 long-window instability, and decide whether the
quasi-2D gate can remain closed or be reopened later.

## Non-Goals

- Do not run full FSI.
- Do not run quasi-2D.
- Do not claim Fluent parity or Figure 29.3 parity.
- Do not claim physical validation from limiter-bounded rows.
- Do not put expensive 48^3 or 96^3 long-window rows inside pytest.
- Do not hide failures behind synthetic artifacts.

## Required Implementation

### P0: Real-Run Runner Infrastructure

Add:

`experiments/steps/step119_lbm_boundary_repair_real_run_validation.py`

The runner must reuse the Step118 repair surface where practical, but Step119
defaults must be real/non-synthetic. It must write to:

`outputs/step119_lbm_boundary_repair_real_run_validation/`

Required CLI features:

- `--row`
- `--resume`
- `--force`
- `--output-interval`
- `--stop-on-first-failure`
- `--checkpoint-every`
- `--max-wall-seconds`
- `--allow-large-real-rows`

The runner must support one-row execution so large Taichi initialization cost
does not multiply across unrelated rows. If a real row is too expensive for the
current environment, it must be skipped or bounded honestly and reported as
incomplete, not replaced by a validation claim.

### P1: Real 48^3 Boundary Variant Comparison

The required 48^3 real rows are:

1. `duct_only_48_legacy_boundary_500step_reference_real`
2. `duct_only_48_regularized_boundary_500step_reference_real`
3. `duct_only_48_regularized_limited_boundary_500step_real`
4. `duct_only_48_convective_outlet_boundary_500step_real`

Success criteria for new boundary variants:

- `synthetic_diagnostic_mode=false`
- `requested_window_completed=true`
- `finite_pass=true`
- `density_gate_pass=true`
- `mass_drift_gate_pass=true`
- `population_gate_pass=true`
- `first_failure_reason=null`
- `flux_imbalance_rel_tail_mean < 0.1`
- `mass_total_delta_rel_final < 0.005`
- `mach_proxy_observed_max < 0.2`
- better than Step117 regularized `flux_imbalance_rel_final=0.4503`

If neither limited nor convective improves on the legacy/regularized references
at 48^3, Step119 must stop before 96^3 and classify:

`boundary_repair_failed_revisit_lbm_solver`

### P2: Real 96^3 Duct-Only Validation

Only run this phase if P1 shows at least one improved new boundary variant.

Required rows:

1. `duct_only_96_regularized_limited_boundary_1000step_real`
2. `duct_only_96_convective_outlet_boundary_1000step_real`

Recommended reference row:

3. `duct_only_96_legacy_boundary_1000step_real_reference`

Success criteria:

- `synthetic_diagnostic_mode=false`
- `requested_window_completed=true`
- `rho_min_global > 0.85`
- `rho_max_global < 1.15`
- `abs(mass_drift_final) < 0.05`
- `max_v_global < 0.2`
- `mach_proxy_observed_max < 0.35`, ideally `< 0.2`
- negative population fraction tail/final `< 1e-3`
- no first failure from negative density, high density, mass drift, or max-v
- outlet flux tail mean is nonzero
- flux imbalance tail mean is not near 1

Step117 96^3 regularized failed catastrophically, with density and mass drift
far outside acceptable range. Step119 must make this comparison explicit.

### P3: Real 96^3 Static Two-Flap Validation

Only run this phase if P2 passes for at least one boundary variant.

Required row:

`static_two_flap_96_best_boundary_1000step_real`

Required additional artifacts:

- `flap_region_flow_summary.json`
- `throat_speed_summary.json`
- `recirculation_proxy_summary.json`

The report must state that this is static-flap LBM-only, not FSI.

### P4: Real First-Failure Localization

For real rows, especially 96^3 rows, write `first_failure_diagnostics.json`
with at least:

- `first_failure_step`
- `first_failure_reason`
- `first_failure_location`
- `first_failure_cell`
- `first_negative_density_step`
- `first_high_density_step`
- `first_mass_drift_step`
- `first_max_v_step`
- `boundary_x_min_negative_population_count_tail`
- `boundary_x_max_negative_population_count_tail`
- `f_min`
- `F_min`
- `f_max`
- `F_max`
- `boundary_plane_where_failure_started`

The report must answer whether failure starts at inlet, outlet,
wall/open-boundary corner, or interior, and whether limited/convective variants
change the first-failure location.

### P5: Limiter Activation Accounting

Limited boundary is a numerical bounding strategy, not physical validation.
Add or compute lightweight limiter activation diagnostics:

- `open_boundary_limiter_enabled`
- `rho_clip_used`
- `velocity_clip_used`
- `noneq_limiter_used`
- `population_floor_used`
- `limiter_activation_count`
- `limiter_activation_fraction`
- `rho_clip_count`
- `velocity_clip_count`
- `noneq_clip_count`
- `population_floor_count`

It is acceptable for Step119 to compute conservative post-process estimates
from boundary fields rather than introducing invasive Taichi counters, as long
as the artifact names and validation gates are explicit.

If limiter activation is high, the report must classify the row as
numerically bounded rather than physically trustworthy.

### P6: Artifact Structure

Top-level output directory:

`outputs/step119_lbm_boundary_repair_real_run_validation/`

Required top-level files:

- `solver_report.json`
- `run_matrix_summary.json`
- `boundary_variant_real_run_comparison.json`
- `first_failure_global_summary.json`
- `limiter_activation_summary.json`
- `step119_gate_report.json`
- `README.md`

Required row files:

- `run_metadata.json`
- `driver_config.json`
- `duct_boundary_condition_report.json`
- `finite_stability_report.json`
- `first_failure_diagnostics.json`
- `fluid_diagnostics_timeseries.csv`
- `density_drift_timeseries.csv`
- `boundary_flux_timeseries.csv`
- `stability_diagnostics_timeseries.csv`

Static two-flap rows must additionally write:

- `flap_region_flow_summary.json`
- `throat_speed_summary.json`
- `recirculation_proxy_summary.json`

### P7: Final Classification

The final report must choose exactly one:

1. `boundary_repair_success_go_to_quasi2d`
2. `boundary_repair_partial_continue_lbm`
3. `boundary_repair_failed_revisit_lbm_solver`

Opening the quasi-2D gate requires all of:

- 48^3 best boundary improves on old regularized and is not materially worse
  than legacy.
- 96^3 duct-only best boundary completes 1000 steps and passes stability gates.
- 96^3 static two-flap best boundary completes 1000 steps and passes stability
  gates.
- First-failure detector reports no failure.
- Population gate passes.
- Limiter activation is not uncontrolled.
- Physical-nu official-like strict row remains skip/report-only, not validation.
- No Fluent claim and no FSI claim.

If any 96^3 or static two-flap gate fails, Step119 must keep quasi-2D blocked.

## Required Tests

Add:

1. `tests/test_step119_real_run_runner_contract.py`
2. `tests/test_step119_boundary_repair_real_artifacts_contract.py`
3. `tests/test_step119_limiter_activation_summary_contract.py`
4. `tests/test_step119_gate_report_contract.py`

Test coverage requirements:

- A tiny real row, preferably 8x6x6 for 5-10 steps, must exercise the real
  runner path with `synthetic_diagnostic_mode=false`.
- Tests must verify real-row schema without requiring large 48^3/96^3 windows.
- Tests must verify strict tau skip behavior.
- Tests must verify committed artifacts do not claim validation if rows are
  incomplete.
- Tests must verify high limiter activation blocks validation claims.
- Tests must verify final classification is one of the three allowed values.
- Tests must verify no Fluent and no FSI claim.

## Required Documentation

Add/update:

- `STEP119_LBM_BOUNDARY_REPAIR_REAL_RUN_VALIDATION_REPORT.md`
- `docs/119_lbm_boundary_repair_real_run_validation.md`
- `README.md`
- output directory `README.md`

The report must distinguish:

- real tiny/smoke rows,
- large rows that were executed,
- large rows that were intentionally skipped or incomplete,
- why quasi-2D remains blocked unless all gates pass.

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  src\mpm_lbm\sim\diagnostics\lbm_stability_diagnostics.py `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step118_lbm_open_boundary_stability_repair.py `
  experiments\steps\step119_lbm_boundary_repair_real_run_validation.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step119_real_run_runner_contract.py `
  tests\test_step119_boundary_repair_real_artifacts_contract.py `
  tests\test_step119_limiter_activation_summary_contract.py `
  tests\test_step119_gate_report_contract.py `
  tests\test_step118_lbm_stability_diagnostics_contract.py `
  tests\test_step118_open_boundary_limiter_contract.py `
  tests\test_step118_boundary_repair_runner_contract.py `
  tests\test_step118_boundary_repair_artifacts_contract.py `
  tests\test_step117_long_window_artifacts_contract.py `
  tests\test_step117_long_window_runner_contract.py `
  tests\test_step116_lbm_boundary_diagnostics_contract.py `
  tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py `
  tests\test_step114_fluent_solver_physics_repair_contract.py `
  tests\test_step104_fluent_duct_flap_setup_repair_contract.py `
  tests\test_step106_outlet_boundary_flow_propagation_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step113_mirrored_duct_flap_geometry_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

## Done Criteria

Step119 is complete only when:

- The detailed goal file exists and is referenced by the active Codex goal.
- Step119 runner, tests, docs, reports, and artifacts exist.
- The runner can generate non-synthetic tiny real-row artifacts.
- Large real rows are either executed and reported, or explicitly skipped behind
  honest environment/time gates.
- The gate report keeps quasi-2D blocked unless all required evidence exists.
- Focused Step119/Step118/Step117 regression tests pass.
- Full repository pytest passes or any failure is diagnosed and fixed.
- `git diff --check` passes.
- Changes are committed with a conventional commit message and pushed to
  `origin/main`.
