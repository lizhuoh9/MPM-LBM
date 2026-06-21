# Step 68 Step-Specific Proxy Migration To experiments/steps Report

## Scope

Step68 migrates the Step63 inventory `step_specific_proxy_remaining` files from root `src/` into `experiments/steps/`.

This step is a code-placement and compatibility migration. It does not run new simulations, activate runtime geometry, activate wall velocity, validate real squid behavior, or change solver formulas.

Base commit:

```text
f28cfc8fb3a3811220c6d98472198a3187ebda41
test: add steps63-67 solver completion batch a
```

## Migration Summary

| Area | Target package | Files |
| --- | --- | ---: |
| real geometry feasibility | `experiments/steps/real_geometry_feasibility/` | 1 |
| shared runtime geometry wall velocity proxy | `experiments/steps/runtime_geometry_wall_velocity_shared/` | 8 |
| Step48 10-step proxy | `experiments/steps/step48_10step_proxy/` | 4 |
| Step49 20-step proxy | `experiments/steps/step49_20step_proxy/` | 4 |
| Step50 one-cycle proxy | `experiments/steps/step50_one_cycle_proxy/` | 4 |
| Step51 transfer comparison proxy | `experiments/steps/step51_transfer_comparison_proxy/` | 4 |
| Step52 48 feasibility proxy | `experiments/steps/step52_48_feasibility_proxy/` | 4 |
| Step53 support scaling audit | `experiments/steps/step53_support_scaling_audit/` | 5 |

Total migrated files:

```text
policy_migration_count = 34
inventory_step_specific_proxy_remaining_count = 34
missing_inventory_paths = []
extra_policy_paths = []
```

Root files now remain as compatibility shims and import from the experiment packages.

## Evidence Summary

| Evidence | Result |
| --- | --- |
| Step68 policy audit | pass, 34 policy migrations match 34 Step63 inventory rows |
| Step68 migration audit | pass, 34 experiment implementations, 34 root shims, root step-specific implementation count 0 |
| Step68 import execution audit | pass, 317 public symbols import through experiment and legacy paths with same object identity |
| Step68 legacy shim audit | pass, 34 shims, 0 legacy implementation bodies |
| Step68 experiment boundary audit | pass, 0 Step68 executable driver calls, 0 Step68 driver dirs, 0 VTR, 0 particle NPY |
| Step68 Step63-67 regression guard | pass, 8 required Batch A artifacts still green |
| Step68 artifact manifest | pass, 64 Step68 files, 0.820 MB, no protected external or real-geometry data edits |

`real_geometry_feasibility` is a quarantined historical experiment helper. It was moved out of root `src/` and is not under `src/mpm_lbm/sim`; Step68 does not execute it.

## Protected Boundaries

Step68 preserves:

```text
No new driver.run execution
No driver.initialize execution
No driver.step_once execution
No outputs/step68_driver_runs
No VTR
No particle NPY
No external/taichi_LBM3D edit
No data/real_geometry_candidates edit
No runtime solver behavior activation
No physics feature expansion
```

## Verification

Runners:

```text
baseline_tests/run_step68_step_specific_proxy_policy_audit.py
baseline_tests/run_step68_step_specific_proxy_migration_audit.py
baseline_tests/run_step68_import_execution_audit.py
baseline_tests/run_step68_legacy_shim_audit.py
baseline_tests/run_step68_experiment_boundary_audit.py
baseline_tests/run_step68_step63_67_regression_guard.py
baseline_tests/run_step68_artifact_manifest.py
```

All Step68 runners passed before this report was written.

Full focused and repository pytest results are recorded in the final commit/push response.

Final validation results before commit:

```text
focused Step68 pytest: 12 passed
full pytest with D:\working\taichi\env\python.exe: 802 passed
full pytest with D:\TOOL\Anaconda\python.exe: 802 passed
```
