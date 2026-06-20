# Step 43 Controlled Squid Proxy Geometry Motion Driver Interface Contract Report

## 1. Goal

Step 43 is controlled squid proxy geometry motion driver interface.
Step 43 defines a guarded driver interface only.
Step 43 keeps geometry motion diagnostic-only.
Step 43 does not update driver geometry.
Step 43 does not displace MPM particles.
Step 43 does not update LBM solid_phi.
Step 43 does not update dynamic_solid.
Step 43 does not recompute boundary links from displaced geometry.
Step 43 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## 2. Files Created And Updated

Step 43 adds `geometry_motion_*` source modules, Step 43 configs, Step 43 baseline runners, a contract test, docs, report, logs, and committed CSV/JSON/NPZ artifacts. It updates `FSIDriverConfig`, `FSIDriver3D`, and `README.md` for the guarded report-only interface.

## 3. Explicit Non-Goals

Step 43 does not activate geometry mutation, particle displacement, LBM solid-field mutation, projection mutation, boundary-link regeneration, free-body movement, swimming, or production solver readiness. It also does not edit vendored external code.

## 4. Geometry Motion Config Validation

`outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.json` validates the prescribed diagnostic-only interface config and verifies the accepted Step 42 displacement artifact dimensions.

## 5. Geometry Motion Interface Report

`outputs/step43_geometry_motion_interface_report/geometry_motion_interface_report.json` verifies that the driver-facing interface can read Step 42 displacement evidence and emit a no-op report.

## 6. Static Driver Regression

`outputs/step43_static_driver_regression/static_driver_results.json` records two static 48^3 moving-boundary rows. These rows keep geometry motion disabled.

## 7. Diagnostic Geometry Motion No-Op Smoke

`outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json` records two diagnostic-only 48^3 moving-boundary rows. These rows write geometry-motion interface reports and keep all mutation flags disabled.

## 8. Static Vs Diagnostic No-Op Comparison

`outputs/step43_static_vs_diagnostic_noop_comparison/static_vs_diagnostic_noop.json` compares static and diagnostic-only rows by transfer mode and checks no-op equivalence for driver physics diagnostics.

## 9. No Geometry State Mutation Guard

`outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.json` records zero counts for MPM particle mutation, LBM solid-field mutation, dynamic-solid mutation, projection calls from geometry motion, boundary-link recomputation, geometry-state mutation, displaced particle output, and dense displacement-field output.

## 10. Quality Report Aggregation

`outputs/step43_quality_report_aggregation/quality_report_summary.json` aggregates the four strict geometry quality reports written by the Step 43 driver rows.

## 11. Step 42 Regression Guard

`outputs/step43_step42_regression_guard/step42_regression_guard.json` confirms that the accepted Step 42 displacement, quality, no-driver guard, and artifact-budget evidence remains present and passing.

## 12. Artifact Manifest Summary

`outputs/step43_artifact_manifest/artifact_summary.json` enforces the Step 43 artifact budget and confirms that Step 43 wrote no VTR files and no particle NPY files.

## 13. Verification Commands

The verification sequence is:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_motion_config.py src\geometry_motion_interface.py src\fsi_config.py src\fsi_driver.py baseline_tests\step43_common.py baseline_tests\run_step43_geometry_motion_config_validation.py baseline_tests\run_step43_geometry_motion_interface_report.py baseline_tests\run_step43_static_driver_regression.py baseline_tests\run_step43_diagnostic_geometry_motion_noop_smoke.py baseline_tests\run_step43_static_vs_diagnostic_noop_comparison.py baseline_tests\run_step43_no_geometry_state_mutation_guard.py baseline_tests\run_step43_quality_report_aggregation.py baseline_tests\run_step43_step42_regression_guard.py baseline_tests\run_step43_artifact_manifest.py tests\test_step43_geometry_motion_driver_interface_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step43_geometry_motion_driver_interface_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
```

## 14. GitHub Sync Information

The final commit and push information is recorded after verification and GitHub sync.

## 15. Acceptance Checklist

- [x] Step 43 detailed goal file exists.
- [x] Geometry-motion config validation passes.
- [x] Default `geometry_motion_mode` remains `static`.
- [x] Default `geometry_motion_application_mode` remains `disabled`.
- [x] Prescribed geometry-motion config is diagnostic-only.
- [x] Step 42 displacement artifact path exists.
- [x] Step 42 displacement row count is 243.
- [x] Tracked regions include `mantle_outer`.
- [x] Tracked regions include `mantle_cavity_proxy`.
- [x] Tracked regions include `funnel_outlet_proxy`.
- [x] `apply_to_driver` is false.
- [x] `apply_to_mpm_particles` is false.
- [x] `apply_to_lbm_solid_phi` is false.
- [x] `apply_to_lbm_solid_vel` is false.
- [x] `apply_to_projection` is false.
- [x] `update_dynamic_solid` is false.
- [x] `recompute_boundary_links` is false.
- [x] `mutate_geometry_state` is false.
- [x] Geometry-motion interface report exists.
- [x] Geometry-motion interface `no_op_pass` is true.
- [x] Static driver regression runs two rows.
- [x] Diagnostic geometry-motion no-op smoke runs two rows.
- [x] All four driver rows are stable.
- [x] All rows complete at least five LBM steps.
- [x] All rows complete at least 25 MPM substeps.
- [x] Every driver row writes `geometry_quality_report.json`.
- [x] Every quality report passes.
- [x] Static-vs-diagnostic no-op comparison passes.
- [x] No geometry-state mutation guard passes.
- [x] Step 42 regression guard passes.
- [x] Default `boundary_motion_mode` remains `static`.
- [x] Default `wall_velocity_application_mode` remains `disabled`.
- [x] No default behavior changes.
- [x] No moving bounce-back formula changes.
- [x] No LBM collision formula changes.
- [x] No MPM constitutive formula changes.
- [x] No projection formula changes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No Step 43 `.vtr` outputs.
- [x] No Step 43 particle `.npy` outputs.
- [x] Artifact large-file count is zero.
- [x] Step 43 output total-size budget passes.
- [x] Repo artifact summary total size remains below budget.
- [x] Step 43 contract test passes.
- [x] Full pytest passes.
- [x] Git whitespace checks pass.
- [x] Pre-push hook passes.
- [x] Step 43 artifacts are pushed to `origin/main`.

## 16. Decision For Step 44

If Step 43 is accepted, Step 44 may consider a controlled diagnostic geometry-update smoke. Step 44 should remain opt-in and conservative, starting from a diagnostic runtime copy or projection-only smoke before any broader coupled-motion claim.
