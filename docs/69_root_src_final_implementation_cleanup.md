# Step 69 Root src Final Implementation Cleanup

Step69 turns the root `src/` post-Step68 state into an audited compatibility
surface.

It performs three cleanup actions:

1. Regenerates the current root inventory from the live tree.
2. Moves the six remaining support implementations into canonical package
   locations and leaves root shims behind.
3. Refreshes `src.__init__` squid-region exports to point at canonical
   modules without making `import src` eager.

## Canonical Owners

| Area | Canonical owner |
| --- | --- |
| Squid region projection and quality | `src/mpm_lbm/sim/squid_proxy/` |
| Squid region driver diagnostics | `src/mpm_lbm/diagnostics/` |
| Wall velocity support helpers | `src/mpm_lbm/sim/wall_velocity/` |

The legacy root files remain for compatibility only. They contain no
implementation bodies.

## Evidence

Step69 writes:

```text
outputs/step69_current_root_inventory_audit/
outputs/step69_remaining_support_migration_audit/
outputs/step69_import_execution_audit/
outputs/step69_legacy_shim_audit/
outputs/step69_root_src_final_cleanup_audit/
outputs/step69_src_init_export_audit/
outputs/step69_code_placement_audit/
outputs/step69_no_simulation_audit/
outputs/step69_step68_regression_guard/
outputs/step69_artifact_manifest/
```

The final cleanup contract is:

```text
current_step_specific_proxy_remaining_count = 0
current_root_step_specific_implementation_count = 0
current_migration_required_count = 0
current_unknown_requires_review_count = 0
migrated_support_count = 6
remaining_migration_required_count = 0
same_object_count = public_symbol_count
```

## Boundaries

Step69 is not a solver activation step. It does not run a driver, create
Step69 driver-run output, write VTR, write particle NPY, edit vendored
`external/taichi_LBM3D`, or edit `data/real_geometry_candidates`.
