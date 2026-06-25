# Step108 Fluent Official-Speed Low-Mach Subcycling Report

Step108 passed as an official-speed low-Mach subcycling smoke. It maps the public tutorial `10 m/s` inlet to `u_lbm = 0.02` by using `120` LBM substeps inside each `0.0005 s` official FSI step, then compares the resulting `0.025 s` proxy displacement curve against the Step107 public-plot reference.

Allowed claim:

```text
The official 10 m/s inlet speed was mapped to a low-Mach LBM target through subcycling, and a 0.025 s proxy transient produced a solver curve that was compared against the Step107 public Fluent plot reference.
```

Step108 is not Fluent validation. It does not reproduce the official mesh, official case, official steady preflow, or exact structural-point monitor.

## Mapping

`outputs/step108_dimensional_mapping/low_mach_subcycling_mapping_report.json` passed:

```text
duct_length_m = 0.1
n_grid = 48
dx_phys_m = 0.0020833333333333333
target_inlet_velocity_mps = 10.0
target_u_lbm = 0.02
lbm_dt_phys_s = 4.166666666666667e-6
official_fsi_dt_s = 0.0005
lbm_substeps_per_fsi_step = 120
mapped_inlet_velocity_mps = 10.0
mapped_velocity_error_mps = 0.0
```

## Duct-Only Precheck

`outputs/step108_duct_only_low_mach_subcycling/flow_plane_report.json` passed with `50` official steps and `6000` LBM substeps:

```text
inlet_plane_mean_ux_final = 0.02000000700354576
mid_duct_plane_mean_ux_final = 0.012313909828662872
outlet_plane_mean_ux_final = 0.012407145462930202
rho_min_final = 0.9999998807907104
rho_max_final = 1.0198925733566284
has_nan = false
has_inf = false
```

## FSI Candidate

`outputs/step108_low_mach_fsi_candidate/low_mach_fsi_report.json` passed:

```text
completed_official_fsi_steps = 50
completed_lbm_substeps = 6000
flap_tip_timeseries_row_count = 51
solver_curve_time_start_s = 0.0
solver_curve_time_end_s = 0.025
fixed_base_max_displacement_norm = 0.0
fixed_base_max_velocity_norm = 0.0
step36_squid_wall_velocity_config_used = false
has_nan = false
has_inf = false
```

## Error Comparison

`outputs/step108_error_comparison/error_report.json` passed the hard comparison gates:

```text
sample_count = 51
solver_curve_time_end_s = 0.025
peak_reference_m = 0.000395
peak_solver_m = 1.2332112646618043e-6
normalized_rms_error = 0.616126763475836
shape_correlation = 0.07866350821657236
all_metrics_finite = true
monitor_equivalence = false
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
```

Soft-goal comparison against Step107:

```text
Step107 peak_solver_m = 3.766233760416071e-7
Step108 peak_solver_m = 1.2332112646618043e-6
peak_solver_improved = true

Step107 normalized_rms_error = 0.6166683693114237
Step108 normalized_rms_error = 0.616126763475836
normalized_rms_improved = true

Step107 shape_correlation = 0.07747139097796335
Step108 shape_correlation = 0.07866350821657236
shape_correlation_improved = true
```

The improvements are small. The remaining dominant gaps are still structural response, monitor equivalence, force transfer, and official steady preflow.

## Guards

`outputs/step108_output_guard/output_guard_report.json` passed:

```text
official_case_file_count = 0
official_mesh_file_count = 0
official_journal_file_count = 0
official_case_data_h5_count = 0
official_png_committed_count = 0
private_fluent_csv_committed_count = 0
validation_claim_count = 0
direct_equivalence_claim_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

`outputs/step108_artifact_manifest/artifact_manifest.json` passed with `step108_file_count = 64` and `step108_total_size_mb` approximately `0.829`.

## Verification

Completed:

```text
D:\working\taichi\env\python.exe -m py_compile ... Step108 files: passed
D:\working\taichi\env\python.exe baseline_tests\run_step108_dimensional_mapping.py: passed
D:\working\taichi\env\python.exe baseline_tests\run_step108_duct_only_low_mach_subcycling.py: passed
D:\working\taichi\env\python.exe baseline_tests\run_step108_low_mach_fsi_candidate.py: passed
D:\working\taichi\env\python.exe baseline_tests\run_step108_error_comparison.py: passed
D:\working\taichi\env\python.exe baseline_tests\run_step108_output_guard.py: passed
D:\working\taichi\env\python.exe baseline_tests\run_step108_artifact_manifest.py: passed
D:\working\taichi\env\python.exe -m pytest -q tests\test_step108_low_mach_subcycling_contract.py tests\test_step108_error_comparison_contract.py tests\test_step108_output_guard_contract.py: 8 passed
D:\working\taichi\env\python.exe baseline_tests\run_step71_config_schema_delta_audit.py: passed after registering the Step108 UnifiedSimConfig schema delta
D:\working\taichi\env\python.exe -m pytest -q tests\test_step71_config_schema_delta_contract.py tests\test_step108_low_mach_subcycling_contract.py tests\test_step108_error_comparison_contract.py tests\test_step108_output_guard_contract.py: 10 passed
D:\working\taichi\env\python.exe -m pytest -q: 1180 passed
D:\TOOL\Anaconda\python.exe -m pytest -q: 1180 passed, 1 deprecation warning from Taichi locale handling
pytest -q: 1180 passed, 1 deprecation warning from Taichi locale handling
git diff --check: passed with CRLF normalization warnings only
```

The pushed commit hash is reported in the final response.
