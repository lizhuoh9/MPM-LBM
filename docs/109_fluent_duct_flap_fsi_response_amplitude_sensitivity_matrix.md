# Step109 Fluent Duct-Flap FSI Response Amplitude Sensitivity Matrix

Step109 runs a bounded response-amplitude sensitivity matrix for the existing
Step108 low-Mach duct-flap proxy. It keeps the Step108 public-speed mapping:
`target_u_lbm = [0.02, 0.0, 0.0]`, `lbm_substeps_per_fsi_step = 120`,
`lbm_dt_phys_override_s = 4.166666666666667e-6`, and 50 official FSI samples
covering `0.025 s`.

The purpose is diagnostic: identify which proxy parameters control the
solver's displacement amplitude relative to the Step107 public plot
digitization. It does not assert official monitor equivalence, dynamic-mesh
equivalence, structural-model equivalence, or Fluent parity. The public Ansys
tutorial page remains the source context for the duct/flap problem setup:
https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html

## Matrix

The response matrix is configured by
`configs/step109_response_matrix_policy.json` and the row configs
`configs/step109_response_matrix_*.json`.

Rows:

- `base`: Step108 low-Mach FSI settings.
- `cap_1e-4_scale_1`, `cap_1e-3_scale_1`, `cap_1e-2_scale_1`,
  `cap_1e-1_scale_1`: moving-boundary force-cap sweep.
- `cap_1e-2_scale_10`, `cap_1e-1_scale_10`: cap plus reaction-scale sweep.
- `E_1e5`, `E_1e4`: material-reference Young's modulus sweep using generated
  Step109 geometry configs under `outputs/step109_response_sensitivity_matrix/`.

All rows preserve the existing LBM collision, tau, moving bounce-back, reaction
transfer formula, MPM stress/update, and procedural duct-flap geometry identity.

## Final Results

Final response matrix artifact:
`outputs/step109_response_sensitivity_matrix/response_matrix_report.json`.

Summary:

- `response_matrix_pass = true`
- `response_matrix_row_count = 9`
- `successful_response_matrix_rows = 9`
- `step108_peak_solver_m = 1.2332112646618043e-6`
- `best_candidate_row_name = cap_1e-1_scale_10`
- `best_peak_solver_m = 0.0012614636216312647`
- `rows_above_step108_peak_count = 8`
- `rows_above_min_peak_count = 7`

Key amplitude pattern:

- `base`: peak ratio `0.0031223361808850867`
- `cap_1e-3_scale_1`: peak ratio `0.03128931168732056`
- `cap_1e-2_scale_1`: peak ratio `0.31252422582216655`
- `cap_1e-1_scale_10`: peak ratio `3.1935787889399108`
- `E_1e5`: peak ratio `0.647285030683196`
- `E_1e4`: peak ratio `0.8615464726580849`

The dominant proxy control in this matrix is the moving-boundary force-cap
envelope. Lower Young's modulus increases response amplitude, but in this
bounded matrix it does not exceed the `cap_1e-1` response.

## Monitor Sensitivity

Final monitor artifact:
`outputs/step109_monitor_sensitivity/monitor_sensitivity_report.json`.

The selected row is `cap_1e-1_scale_10`. Four monitor variants were exported
with 51 samples each:

- `free_tip_proxy_mean`: peak `0.0012614641845287954 m`
- `free_tip_proxy_max_total_displacement`: peak `0.0014932498700470317 m`
- `nearest_public_monitor_point`: peak `0.0013679608251050482 m`
- `top_5_nearest_public_monitor_mean`: peak `0.0013471473475727383 m`

The monitor spread is modest for this row:
`max_to_mean_peak_ratio = 1.1837433740576766`.

## Diagnostics And Guards

Final diagnostics:

- `outputs/step109_diagnostics/force_cap_diagnostics_report.json`
- `outputs/step109_diagnostics/structural_sensitivity_report.json`

Final guards:

- `outputs/step109_output_guard/output_guard_report.json`
- `outputs/step109_artifact_manifest/artifact_manifest.json`

Guard summary:

- `output_guard_pass = true`
- `artifact_manifest_pass = true`
- `step109_driver_run_dir_count = 9`
- `step109_file_count = 142`
- `step109_total_size_mb = 3.4777116775512695`

## Reproduction

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_response_sensitivity_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_monitor_sensitivity.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_force_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step109_response_sensitivity_matrix_contract.py tests\test_step109_monitor_sensitivity_contract.py tests\test_step109_output_guard_contract.py
```

The first full matrix run can be slow because Taichi compiles large D3Q19 matrix
kernels. The Step109 matrix runner can reuse completed row directories and
rerun only missing rows plus the final selected monitor-capture row.
