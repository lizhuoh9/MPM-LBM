# Compatibility And Deprecation Policy

Step70 freezes the root `src` compatibility surface.

```text
compatibility_surface_audit_pass = true
src_init_export_count = 38
legacy_shim_target_count = 8
stale_export_count = 0
forbidden_target_count = 0
same_object_count = 38
heavy_import_during_src_import = false
```

`src.__init__` exports are classified as:

```text
canonical_target_required
legacy_shim_target_allowed
approved_legacy_tooling_allowed
forbidden_target
```

Legacy shim targets remain allowed only when the root file is a compatibility
shim and importing through the root path resolves to the same object as the
canonical module.

The source of truth is:

```text
configs/step70_compatibility_surface_policy.json
outputs/step70_compatibility_surface_audit/audit.json
```
