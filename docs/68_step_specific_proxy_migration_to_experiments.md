# Step 68 Step-Specific Proxy Migration To experiments/steps

Step68 moves step-specific proxy implementation out of root `src/` and into `experiments/steps/`.

## Why

Step63 inventory classified 34 root files as `step_specific_proxy_remaining` with target owner `experiments/steps`. Keeping those implementations in root `src/` would blur the boundary between reusable solver packages and historical step experiments.

## Result

The migrated packages are:

```text
experiments/steps/real_geometry_feasibility/
experiments/steps/runtime_geometry_wall_velocity_shared/
experiments/steps/step48_10step_proxy/
experiments/steps/step49_20step_proxy/
experiments/steps/step50_one_cycle_proxy/
experiments/steps/step51_transfer_comparison_proxy/
experiments/steps/step52_48_feasibility_proxy/
experiments/steps/step53_support_scaling_audit/
```

Root files now act as compatibility shims so older imports continue to work.

## Boundary

Step68 does not activate solver behavior. It does not run real geometry feasibility, runtime geometry, wall velocity, squid behavior, or any new driver row. The migrated experiment modules preserve historical code ownership and import compatibility only.

## Evidence

Primary evidence:

```text
outputs/step68_step_specific_proxy_policy_audit/audit.json
outputs/step68_step_specific_proxy_migration_audit/audit.json
outputs/step68_import_execution_audit/audit.json
outputs/step68_legacy_shim_audit/audit.json
outputs/step68_experiment_boundary_audit/audit.json
outputs/step68_step63_67_regression_guard/audit.json
outputs/step68_artifact_manifest/artifact_summary.json
```

Key current values:

```text
policy_migration_count = 34
root_step_specific_implementation_count = 0
same_object_count = 317
driver_run_call_count = 0
step68_driver_run_output_dir_count = 0
step68_vtr_count = 0
step68_particle_npy_count = 0
```
