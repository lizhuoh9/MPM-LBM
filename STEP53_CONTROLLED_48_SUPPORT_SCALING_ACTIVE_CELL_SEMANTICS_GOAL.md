# Step 53 Controlled 48 Support Scaling And Active-Cell Semantics Goal

## Short Goal Reference

Implement Step 53 exactly as this file specifies. Step 53 is a controlled
post-processing audit over accepted Step 51 and Step 52 artifacts. It must
explain and guard the support-scaling semantics exposed by Step 52, especially
the fact that 48^3 projected `active_cell_count` did not grow while
`applied_cell_count` did grow. Step 53 must not add solver rows, rerun new
physics matrices, introduce 48^3 `link_area_experimental`, extend cycle count,
change formulas, change defaults, or make physical, grid-convergence, real-jet,
squid-swimming, or production-readiness claims.

## Background

Step 52 accepted a 48^3 engineering-only one-cycle diagnostic feasibility
probe. It ran exactly two rows:

```text
engineering_static_48_40step
engineering_runtime_geometry_plus_wall_velocity_48_40step
```

The Step 52 artifacts are stable, finite, bounded, diagnostic-only, and
non-persistent. The important Step 52 observation is:

```text
active_cell_count_32 = 648
active_cell_count_48 = 648
active_cell_count_growth_observed = false
active_cell_count_non_decreasing = true

applied_cell_count_32 = 648
applied_cell_count_48 = 2136
applied_cell_count_ratio_48_vs_32 = 3.2962962962962963
applied_cell_count_growth_observed = true

bb_link_count_32 = 3888
bb_link_count_48 = 3888
bb_link_count_ratio_48_vs_32 = 1.0

grid_convergence_claim = false
physical_validation_claim = false
```

Step 53 exists because the next engineering decision should not treat
`active_cell_count` as a grid-convergence or physical-resolution metric. The
support counters need explicit names, semantics, and regression guards before a
later step considers 48^3 `link_area_experimental` or longer-cycle work.

## Required Scope

Step 53 must prove, through checked-in configs, source modules, baseline
runners, CSV/JSON outputs, logs, docs, report, and contract tests:

1. All referenced Step 51 and Step 52 artifacts exist, are readable, and have
   the required accepted structure.
2. The Step 51 32^3 engineering combined row and Step 52 48^3 engineering
   combined row are matched phase-by-phase across 40 phases.
3. Support counters are separated into:

```text
projected active-cell support
applied wall-cell support
bounce-back link support
projected mass proxy
wall velocity support
density / velocity / force / impulse diagnostic envelope
```

4. `active_cell_count_growth_observed = false` is explicitly reported and is
   not treated as a Step 53 failure when no grid-convergence or physical claim
   is made.
5. `active_cell_count_non_decreasing = true` is required.
6. `applied_cell_count_growth_observed = true` is required and is interpreted
   only as diagnostic wall-application support growth.
7. `bb_link_count` behavior is explicitly reported as a diagnostic bounce-back
   proxy, not a boundary-area convergence metric.
8. Force and impulse proxy ratios are finite and interpreted as diagnostic
   proxies only.
9. Claim guards prevent docs, reports, configs, runners, tests, and outputs
   from making physical, grid-convergence, production, real-jet, or squid
   swimming claims.
10. Step 52 remains green through a regression guard.
11. Artifact budget remains small and repository size remains below 400 MB.

## Explicit Non-Goals

Step 53 must not implement or claim:

```text
64^3 run
multi-cycle run
48^3 link_area_experimental run
full transfer-mode matrix
new 48^3 runtime-only row
new 48^3 wall-only row
new 32^3 solver rerun
new physics matrix run
free-body motion
body trajectory
squid swimming
real jet validation
jet propulsion validation
real squid validation
grid convergence validation
physical validation
production readiness
production moving-geometry solver
link_area superiority
solver formula change
default behavior change
external/taichi_LBM3D edit
raw real geometry or scan data
VTR output
particle NPY output
dense displacement output
persistent projected state
persistent displaced geometry
persistent LBM solid_vel
```

## Reference Artifacts

Step 53 must read only accepted committed artifacts. The reference artifact
config must point to:

```text
outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json
outputs/step51_artifact_manifest/artifact_summary.json
outputs/step52_48_feasibility_matrix/feasibility_matrix.json
outputs/step52_48_vs_step51_engineering_scaling_comparison/scaling_comparison.json
outputs/step52_artifact_manifest/artifact_summary.json
outputs/step52_state_mutation_guard/state_mutation_guard.json
outputs/step52_step51_regression_guard/step51_regression_guard.json
```

The main audit row identities are:

```text
step51 row: engineering_runtime_geometry_plus_wall_velocity_32_40step
step52 row: engineering_runtime_geometry_plus_wall_velocity_48_40step
step52 static row: engineering_static_48_40step
```

Step 53 may optionally read the Step 51 static row as reference context, but it
must not require a new solver run.

## Files To Add

Configs:

```text
configs/step53_support_scaling_active_cell_semantics_audit.json
configs/step53_step51_step52_reference_artifacts.json
configs/step53_metric_semantics_policy.json
```

Source:

```text
src/runtime_geometry_wall_velocity_support_scaling_config.py
src/runtime_geometry_wall_velocity_support_scaling_audit.py
src/runtime_geometry_wall_velocity_support_scaling_diagnostics.py
src/runtime_geometry_wall_velocity_support_scaling_claim_guard.py
src/runtime_geometry_wall_velocity_support_scaling_artifact_guard.py
```

Baseline runners:

```text
baseline_tests/step53_common.py
baseline_tests/run_step53_reference_artifact_validation.py
baseline_tests/run_step53_phasewise_support_scaling_audit.py
baseline_tests/run_step53_active_cell_semantics_audit.py
baseline_tests/run_step53_applied_wall_support_scaling_audit.py
baseline_tests/run_step53_bounceback_support_scaling_audit.py
baseline_tests/run_step53_metric_claim_guard.py
baseline_tests/run_step53_step52_regression_guard.py
baseline_tests/run_step53_artifact_manifest.py
```

Tests and docs:

```text
tests/test_step53_support_scaling_active_cell_semantics_contract.py
docs/53_controlled_48_support_scaling_active_cell_semantics.md
STEP53_CONTROLLED_48_SUPPORT_SCALING_ACTIVE_CELL_SEMANTICS_REPORT.md
```

## Required Outputs

Step 53 must write small CSV/JSON/log artifacts under Step 53 specific
directories:

```text
outputs/step53_reference_artifact_validation/
outputs/step53_phasewise_support_scaling_audit/
outputs/step53_active_cell_semantics_audit/
outputs/step53_applied_wall_support_scaling_audit/
outputs/step53_bounceback_support_scaling_audit/
outputs/step53_metric_claim_guard/
outputs/step53_step52_regression_guard/
outputs/step53_artifact_manifest/
logs/step53_*.log
```

Step 53 should not write NPZ. If a later revision adds NPZ, it may contain only
compact summary arrays and must not contain dense fields, particles, geometry
dumps, VTR data, raw scan data, or real geometry.

## Phasewise Support Scaling Audit

The phasewise audit must compare the 32^3 Step 51 engineering combined row and
the 48^3 Step 52 engineering combined row. Each phase row must include:

```text
phase
active_cell_count_32
active_cell_count_48
active_cell_count_ratio_48_vs_32
active_cell_count_delta_48_minus_32
applied_cell_count_32
applied_cell_count_48
applied_cell_count_ratio_48_vs_32
applied_cell_count_delta_48_minus_32
bb_link_count_32
bb_link_count_48
bb_link_count_ratio_48_vs_32
bb_link_count_delta_48_minus_32
projected_mass_32
projected_mass_48
projected_mass_delta_48_minus_32
rho_min_32
rho_min_48
rho_max_32
rho_max_48
lbm_max_v_32
lbm_max_v_48
hydro_force_norm_32
hydro_force_norm_48
hydro_force_ratio_48_vs_32
impulse_proxy_32
impulse_proxy_48
impulse_proxy_ratio_48_vs_32
```

The summary must include:

```text
phase_count = 40
matched_phase_count = 40
phase_sequence_starts_at_0 = true
phase_sequence_ends_at_0975 = true
all_values_finite = true
all_ratios_finite = true
active_cell_count_growth_observed = false
active_cell_count_non_decreasing = true
applied_cell_count_growth_observed = true
applied_cell_count_ratio_48_vs_32 = 3.2962962962962963
bb_link_count_48 > 0
rho_min_48 > 0.95
rho_max_48 < 1.05
lbm_max_v_48 < 0.1
grid_convergence_claim = false
physical_validation_claim = false
production_readiness_claim = false
```

## Active-Cell Semantics Audit

The active-cell audit must explicitly state that `active_cell_count` is not a
grid-convergence metric in this diagnostic envelope.

Required fields:

```text
active_cell_count_32
active_cell_count_48
active_cell_count_ratio
active_cell_count_growth_observed
active_cell_count_non_decreasing
active_cell_count_used_as_grid_convergence_metric = false
active_cell_count_growth_required_for_pass = false
active_cell_growth_failure_is_step53_failure = false
active_cell_semantics_status
step54_link_area_allowed
step54_block_reason
grid_convergence_claim = false
physical_validation_claim = false
production_readiness_claim = false
```

Allowed `active_cell_semantics_status` values:

```text
resolution_invariant_under_current_diagnostic
non_decreasing_but_not_resolution_scaling
unresolved_requires_metric_rename_or_projection_audit
```

If the status is `unresolved_requires_metric_rename_or_projection_audit`, then
`step54_link_area_allowed` must be false. If the status is one of the other two
accepted values, `step54_link_area_allowed` may be true only as a diagnostic
next-step permission, not as physical validation.

## Applied Wall Support Audit

The applied support audit must make applied wall-cell support a first-class
diagnostic metric.

Required fields:

```text
applied_cell_count_32 = 648
applied_cell_count_48 = 2136
applied_cell_count_ratio_48_vs_32 = 3.2962962962962963
applied_cell_count_growth_observed = true
applied_cell_support_growth_pass = true
applied_cell_fraction_32 = applied_cell_count_32 / 32^3
applied_cell_fraction_48 = applied_cell_count_48 / 48^3
applied_cell_fraction_ratio
applied_cell_count_per_active_cell_32
applied_cell_count_per_active_cell_48
applied_cell_growth_is_physical_validation = false
wall_support_growth_claim = diagnostic_only
```

The report language must use `wall-application support growth`. It must not use
that growth as grid convergence, physical boundary accuracy improvement, or
production readiness evidence.

## Bounce-Back Support Audit

The bounce-back audit must report the current diagnostic bounce-back proxy
behavior.

Required fields:

```text
bb_link_count_32
bb_link_count_48
bb_link_count_ratio
bb_link_growth_observed
bb_link_non_decreasing
bb_link_used_as_area_convergence_metric = false
bb_link_support_status
```

Allowed `bb_link_support_status` values:

```text
resolution_invariant_under_current_diagnostic
non_decreasing_but_not_area_convergence
unresolved_requires_boundary_link_metric_audit
```

## Force And Impulse Proxy Audit

The phasewise and summary diagnostics must include:

```text
hydro_force_max_norm_32
hydro_force_max_norm_48
hydro_force_ratio_48_vs_32
impulse_proxy_32
impulse_proxy_48
impulse_proxy_ratio_48_vs_32
force_impulse_ratios_finite = true
force_impulse_interpretation = diagnostic_proxy_only
```

No force or impulse ratio may be described as physical improvement, physical
degradation, propulsion performance, or swimming evidence.

## Claim Guard

All docs, reports, configs, runners, tests, and outputs must avoid claims that
Step 53 proves or implements:

```text
real jet validation
jet propulsion validation
squid swimming
real squid validation
grid convergence validation
physical validation
production readiness
production moving geometry solver
link_area superiority
48^3 physical validation
```

The claim guard must require these explicit flags:

```text
grid_convergence_claim = false
physical_validation_claim = false
production_readiness_claim = false
active_cell_count_is_grid_convergence_metric = false
applied_cell_growth_is_physical_validation = false
bb_link_used_as_area_convergence_metric = false
force_impulse_interpretation = diagnostic_proxy_only
```

## Regression Guards

Step 53 must verify that Step 52 remains green:

```text
Step 52 report exists
Step 52 matrix row_count == 2
Step 52 stable_count == 2
Step 52 scaling comparison pass remains true
Step 52 active_cell_count_growth_observed remains explicitly reported
Step 52 applied_cell_count_growth_observed remains true
Step 52 state guard remains green
Step 52 artifact budget remains green
Step 51 regression evidence remains green
```

## Artifact Budget

Step 53 must report:

```text
step53_file_count
step53_total_size_mb < 5
repo total_size_mb < 400
large_file_count == 0
step53_vtr_count == 0
step53_particle_npy_count == 0
step53_dense_displacement_output_count == 0
step53_displaced_particle_output_count == 0
scan_data_file_count == 0
raw_candidate_large_file_count == 0
private_absolute_path_count == 0
geo_all_fluid_dat_count_added == 0
```

## Acceptance Criteria

All of the following must be true:

```text
Step 53 detailed goal file exists
Step 53 main config exists
Step 53 reference artifact config exists
Step 53 metric semantics policy exists
all referenced files are readable
no new solver row is required
no new transfer mode is introduced
diagnostic_only == true
post_processing_only == true
Step 51 transfer comparison matrix exists
Step 52 feasibility matrix exists
Step 52 scaling comparison exists
Step 51 artifact summary exists
Step 52 artifact summary exists
matched_phase_count == 40
phase sequence starts at 0.0
phase sequence ends at 0.975
all compared values are finite
all ratios are finite
active_cell_count_48 >= active_cell_count_32
active_cell_count_growth_observed is explicitly reported
active_cell_count_used_as_grid_convergence_metric == false
active_cell_count_growth_required_for_pass == false
active_cell_semantics_status is in the accepted enum
active_cell_count_growth_observed == false is allowed only when no grid-convergence claim is made
applied_cell_count_32 == 648
applied_cell_count_48 == 2136
applied_cell_count_48 > applied_cell_count_32
applied_cell_count_growth_observed == true
applied_cell_count_ratio_48_vs_32 is finite
applied_cell_count_ratio_48_vs_32 > 1.0
applied_cell_support_growth_pass == true
wall support growth claim is diagnostic-only
bb_link_count_48 > 0
bb_link_used_as_area_convergence_metric == false
force_impulse_ratios_finite == true
force_impulse_interpretation == diagnostic_proxy_only
grid_convergence_claim == false
physical_validation_claim == false
production_readiness_claim == false
applied_cell_growth_is_physical_validation == false
Step 52 report exists
Step 52 matrix row_count == 2
Step 52 stable_count == 2
Step 52 scaling comparison pass remains true
Step 52 active_cell_count_growth_observed remains explicitly reported
Step 52 applied_cell_count_growth_observed remains true
Step 52 state guard remains green
Step 52 artifact budget remains green
Step 51 regression evidence remains green
Step 53 artifact budget passes
step53_total_size_mb < 5
repo total_size_mb < 400
large_file_count == 0
step53_vtr_count == 0
step53_particle_npy_count == 0
step53_dense_displacement_output_count == 0
step53_displaced_particle_output_count == 0
scan_data_file_count == 0
raw_candidate_large_file_count == 0
private_absolute_path_count == 0
geo_all_fluid_dat_count_added == 0
no protected solver formula changes
no external/taichi_LBM3D edits
no data/real_geometry_candidates edits
no real jet validation claim
no jet propulsion validation claim
no squid swimming claim
no real squid validation claim
no grid convergence claim
no physical validation claim
no production readiness claim
logs/step53_pytest.log exists
pytest -q passes
Step 53 contract test passes
git diff --check passes
```

## Implementation Phases

1. Write this detailed goal file and create a short goal that references it.
2. Add Step 53 configs and source modules for loading references, building
   phasewise support rows, summarizing semantics, scanning claims, and checking
   artifact budgets.
3. Add baseline runners that write the required CSV/JSON/log artifacts.
4. Add docs, report, and a contract test that checks the committed artifact
   surfaces without importing heavy solver package initializers.
5. Run py_compile, every Step 53 runner, Step 53 contract test, full pytest,
   artifact manifest refresh after pytest logs exist, `git diff --check`, and
   protected-path status checks.
6. Commit and push all Step 53 code, configs, docs, tests, logs, outputs, and
   report to `origin/main`.

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\runtime_geometry_wall_velocity_support_scaling_config.py `
  src\runtime_geometry_wall_velocity_support_scaling_audit.py `
  src\runtime_geometry_wall_velocity_support_scaling_diagnostics.py `
  src\runtime_geometry_wall_velocity_support_scaling_claim_guard.py `
  src\runtime_geometry_wall_velocity_support_scaling_artifact_guard.py `
  baseline_tests\step53_common.py `
  baseline_tests\run_step53_reference_artifact_validation.py `
  baseline_tests\run_step53_phasewise_support_scaling_audit.py `
  baseline_tests\run_step53_active_cell_semantics_audit.py `
  baseline_tests\run_step53_applied_wall_support_scaling_audit.py `
  baseline_tests\run_step53_bounceback_support_scaling_audit.py `
  baseline_tests\run_step53_metric_claim_guard.py `
  baseline_tests\run_step53_step52_regression_guard.py `
  baseline_tests\run_step53_artifact_manifest.py `
  tests\test_step53_support_scaling_active_cell_semantics_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_reference_artifact_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_phasewise_support_scaling_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_active_cell_semantics_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_applied_wall_support_scaling_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_bounceback_support_scaling_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_metric_claim_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_step52_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step53_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step53_support_scaling_active_cell_semantics_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Step 54 Decision Rule

Step 53 must report a Step 54 recommendation:

```text
if active_cell_semantics_status != unresolved_requires_metric_rename_or_projection_audit:
    Step 54 may do a diagnostic-only 48^3 link_area_experimental two-row comparison.
else:
    Step 54 must first do metric rename or projection diagnostic clarification.

if applied wall support audit fails:
    Step 54 must not expand grid, cycle, or transfer mode.

if bounce-back support audit is unresolved:
    Step 54 must not treat bb_link_count as an area-convergence metric.
```

The recommended route remains:

```text
Step 53 = support-scaling / active-cell semantics audit
Step 54 = 48^3 link_area_experimental two-row comparison only if Step 53 has no unresolved blocker
Step 55 = consider longer diagnostic duration
```
