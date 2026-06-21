# Public API Surface

Step70 freezes the canonical import surface used by later activation-readiness
steps.

```text
public_api_surface_audit_pass = true
canonical_import_pass_count = 195
expected_count = 195
api_group_count = 9
solver_run = false
output_snapshot_unchanged = true
```

Frozen groups:

```text
driver_api
lbm_mpm_api
coupling_api
geometry_api
motion_wall_velocity_api
runtime_geometry_displacement_api
squid_proxy_api
diagnostics_api
experiments_api
```

The source of truth is:

```text
configs/step70_public_api_surface_policy.json
outputs/step70_public_api_surface_audit/audit.json
```

The experiments API entries are explicitly frozen as experiment APIs, not
solver runtime APIs.
