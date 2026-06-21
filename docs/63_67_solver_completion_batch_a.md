# Step 63-67 Solver Completion Batch A

Batch A is a solver-completion maintenance batch. It freezes new simulations while moving remaining solver-support implementations from root `src/*.py` into canonical packages.

## Canonical Ownership

| Area | Canonical owner |
| --- | --- |
| Motion interfaces and configs | `src/mpm_lbm/sim/motion/` |
| Wall velocity application, config, and field | `src/mpm_lbm/sim/wall_velocity/` |
| Runtime geometry projection | `src/mpm_lbm/sim/runtime_geometry/` |
| Diagnostic geometry | `src/mpm_lbm/diagnostics/` |
| Geometry displacement runtime support | `src/mpm_lbm/sim/geometry_displacement/` |
| Geometry displacement diagnostics | `src/mpm_lbm/diagnostics/` |
| Squid proxy support | `src/mpm_lbm/sim/squid_proxy/` |
| Real geometry pure support | `src/mpm_lbm/sim/geometry/` |

Root files that were migrated now remain only as compatibility shims.

## Evidence Model

Batch A uses generic evidence modules:

```text
src/mpm_lbm/evidence/batch_migration_audit.py
src/mpm_lbm/evidence/batch_import_execution_audit.py
src/mpm_lbm/evidence/batch_legacy_shim_audit.py
src/mpm_lbm/evidence/batch_behavior_preservation_audit.py
```

These modules are policy-driven by:

```text
configs/step64_motion_wall_velocity_migration_policy.json
configs/step65_runtime_geometry_migration_policy.json
configs/step66_diagnostic_geometry_displacement_migration_policy.json
configs/step67_squid_proxy_real_geometry_migration_policy.json
```

The public symbol lists come from AST discovery and are fixed in policy files. The import audit confirms canonical and legacy imports resolve to the same objects.

## Runtime Boundary

Batch A does not activate runtime geometry, wall velocity, squid behavior, or real geometry simulation. It preserves existing behavior and prepares ownership for later activation gates.
