# Step109 Fluent Duct-Flap FSI Response Amplitude Sensitivity Matrix Report

Step109 is complete. It runs a bounded 9-row response-amplitude sensitivity
matrix for the Step108 low-Mach duct-flap proxy and compares each solver curve
against the Step107 public plot digitization.

This is a sensitivity and bottleneck report only. It does not claim official
Fluent parity, exact structural-point monitor equivalence, official mesh/case
reproduction, official dynamic-mesh reproduction, or readiness beyond the
recorded proxy evidence.

## Result

- Response matrix: pass
- Stable rows: 9 of 9
- Best row: `cap_1e-1_scale_10`
- Step108 peak solver displacement: `1.2332112646618043e-6 m`
- Best Step109 peak solver displacement: `0.0012614636216312647 m`
- Rows above Step108 peak: 8
- Rows above `1.0e-5 m`: 7
- Best peak ratio versus public reference peak: `3.1935787889399108`

The dominant proxy parameter in this matrix is the moving-boundary force-cap
envelope. The `cap_1e-1` rows raise the response by roughly three orders of
magnitude relative to Step108. The material sweep also increases amplitude:
`E_1e5` reaches peak ratio `0.647285030683196`, and `E_1e4` reaches
`0.8615464726580849`, but neither exceeds the `cap_1e-1` rows in this bounded
matrix.

## Artifacts

- Goal: `STEP109_FLUENT_DUCT_FLAP_FSI_RESPONSE_AMPLITUDE_SENSITIVITY_MATRIX_GOAL.md`
- Response matrix: `outputs/step109_response_sensitivity_matrix/response_matrix_report.json`
- Best candidate curve: `outputs/step109_response_sensitivity_matrix/best_candidate_flap_tip_displacement_timeseries.csv`
- Monitor sensitivity: `outputs/step109_monitor_sensitivity/monitor_sensitivity_report.json`
- Force-cap diagnostics: `outputs/step109_diagnostics/force_cap_diagnostics_report.json`
- Structural sensitivity: `outputs/step109_diagnostics/structural_sensitivity_report.json`
- Output guard: `outputs/step109_output_guard/output_guard_report.json`
- Artifact manifest: `outputs/step109_artifact_manifest/artifact_manifest.json`
- Documentation: `docs/109_fluent_duct_flap_fsi_response_amplitude_sensitivity_matrix.md`

## Monitor Sensitivity

The final selected row is `cap_1e-1_scale_10`. Four monitor variants were
recorded with 51 samples through `0.025 s`:

- `free_tip_proxy_mean`: peak `0.0012614641845287954 m`
- `free_tip_proxy_max_total_displacement`: peak `0.0014932498700470317 m`
- `nearest_public_monitor_point`: peak `0.0013679608251050482 m`
- `top_5_nearest_public_monitor_mean`: peak `0.0013471473475727383 m`

The max-to-mean monitor peak ratio is `1.1837433740576766`.

## Guard Status

- Output guard: pass
- Artifact manifest: pass
- Official case files: 0
- Official mesh files: 0
- Official journal files: 0
- Official case/data h5 files: 0
- Step109 driver run directories: 9
- Step109 artifact size: `3.4777116775512695 MB`

## Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_response_sensitivity_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_monitor_sensitivity.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_force_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step109_response_sensitivity_matrix_contract.py tests\test_step109_monitor_sensitivity_contract.py tests\test_step109_output_guard_contract.py
```

Full pytest and secondary interpreter verification were run after these Step109
artifacts were generated.
