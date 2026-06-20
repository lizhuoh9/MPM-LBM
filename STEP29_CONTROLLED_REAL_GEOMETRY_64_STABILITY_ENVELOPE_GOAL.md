# Step 29 Goal: Controlled Real Geometry 64 Short-Window Stability Envelope

This file is the authoritative execution contract for Step 29 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 29 starts only when a Codex goal explicitly references this file.

## 1. Status Before Step 29

Step 28 is accepted on GitHub at commit:

```text
c679c460861e37e7b15e92999d0b9bd9844b575e
```

Step 28 established controlled real geometry 64^3 transfer diagnostics. The accepted evidence includes:

- `STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md`;
- candidate fingerprint guard against the Step 25 manifest;
- four 64^3 moving_boundary transfer diagnostic rows for the accepted mesh and voxel smoke candidates;
- mesh 64^3 rows for moving_boundary engineering and moving_boundary link_area_experimental;
- voxel 64^3 rows for moving_boundary engineering and moving_boundary link_area_experimental;
- all four rows completed 10 LBM steps and 50 MPM substeps;
- all four rows were stable, finite, and strict quality-passing;
- all four rows wrote `geometry_quality_report.json`;
- engineering-vs-link_area comparison had two passing rows;
- force/reaction diagnostics had four passing rows, 11 time-series rows per case, and 10 post-step positive diagnostic rows per case;
- area-scale envelope had two passing link-area rows with finite bounded final scale values;
- Step 27 prefix regression passed at Step 28 `step = 5` for all four transfer rows;
- Step 28 quality aggregation had 4 strict reports, 4 pass, 0 warning, and 0 error;
- Step 28 artifact summary had `large_file_count = 0`, no Step 28 `.vtr`, no Step 28 particle `.npy`, no raw candidate large files, no scan data, and no private absolute paths;
- `logs/step28_pytest.log` showed `238 passed`;
- no edits to `external/taichi_LBM3D`;
- no solver/coupler/LBM/MPM/projection formula changes.

Step 29 must preserve all Step 25, Step 26, Step 27, and Step 28 boundaries and evidence.

## 2. Step 29 Objective

Correct description:

```text
Step 29 is controlled real geometry 64^3 short-window stability envelope.
```

Required scope sentence:

```text
Step 29 extends Step 28 transfer diagnostics conservatively.
```

Long-form objective:

```text
Step 29 expands the accepted Step 28 64^3 transfer diagnostics from a 10-step diagnostic window to a 20-step short-window stability envelope for the same controlled real-geometry smoke candidates. Step 29 remains diagnostic only and is not real squid validation.
```

Step 29 must prove:

1. The accepted Step 25 candidate fingerprints still match the Step 25 manifest.
2. The Step 26 generated driver-ready `GeometryConfig` files remain valid and strict.
3. The selected 64^3 Step 29 moving_boundary stability configs are valid, strict, and output-budgeted.
4. The same four Step 28 transfer rows can run a 20-step 64^3 diagnostic window without NaN, Inf, density instability, excessive velocity, invalid MPM deformation, or lost projection.
5. The engineering and link_area_experimental envelopes remain directly comparable for each candidate.
6. Force/reaction envelopes remain finite and positive after nonzero steps.
7. Area-scale diagnostics remain finite and bounded for both link-area rows.
8. Step 29 20-step rows preserve the Step 28 10-step prefix/final diagnostics within explicit tolerances.
9. Step 28 regression evidence remains intact.
10. Solver, coupler, LBM, MPM, moving-boundary, and projection formulas remain unchanged.
11. Artifact budgets remain controlled.
12. Raw large real geometry files and scan data are not committed.

## 3. Hard Boundaries

Do not implement:

```text
squid actuation
squid swimming
real squid validation claim
production sharp-interface FSI claim
final solver readiness claim
new FSI physics
new coupling formula
changes to PenaltyFSICoupler3D
changes to MovingBoundaryFSICoupler3D
changes to LinkAreaMovingBoundaryCoupler3D
changes to moving bounce-back formula
changes to LBM step formulas
changes to MPM constitutive formulas
changes to projection formulas
production mesh repair
automatic remeshing
mesh cleanup or mesh fixing
scan-data processing pipeline
two-phase flow
contact angle physics
sparse storage
ReducedSquidFSI
edits to external/taichi_LBM3D
committing large raw real geometry
committing scan data
committing private absolute local geometry paths
```

Allowed work:

```text
20-step short-window 64^3 moving_boundary driver rows
engineering vs link_area stability envelope summaries
force/reaction envelope summaries
area-scale envelope summaries
Step 28 prefix/final regression comparison
Step 28 regression guard
quality report aggregation
driver timing and artifact diagnostics
docs, report, contract test, logs, small outputs
artifact budget checks
commit and push of relevant Step 29 code, configs, docs, logs, outputs, tests, goal, and report
```

Any change that touches core solver formulas is out of scope and must be rejected.

## 4. Required Files

Create:

```text
STEP29_CONTROLLED_REAL_GEOMETRY_64_STABILITY_ENVELOPE_GOAL.md
STEP29_CONTROLLED_REAL_GEOMETRY_64_STABILITY_ENVELOPE_REPORT.md

docs/29_controlled_real_geometry_64_stability_envelope.md

configs/step29_stability_real_candidate_smoke_mesh_64_moving_boundary.json
configs/step29_stability_real_candidate_smoke_mesh_64_link_area.json
configs/step29_stability_real_candidate_smoke_voxel_64_moving_boundary.json
configs/step29_stability_real_candidate_smoke_voxel_64_link_area.json

baseline_tests/step29_common.py
baseline_tests/run_step29_candidate_fingerprint_guard.py
baseline_tests/run_step29_64_stability_driver.py
baseline_tests/run_step29_stability_envelope_summary.py
baseline_tests/run_step29_engineering_vs_link_area_envelope.py
baseline_tests/run_step29_force_reaction_envelope.py
baseline_tests/run_step29_area_scale_envelope.py
baseline_tests/run_step29_step28_prefix_regression.py
baseline_tests/run_step29_quality_report_aggregation.py
baseline_tests/run_step29_step28_regression_guard.py
baseline_tests/run_step29_artifact_manifest.py

tests/test_step29_controlled_real_geometry_64_stability_envelope_contract.py
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/11_artifact_policy.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
docs/24_controlled_real_geometry_intake.md
docs/25_real_geometry_candidate_policy.md
docs/26_controlled_real_geometry_short_feasibility.md
docs/27_controlled_real_geometry_64_short_driver.md
docs/28_controlled_real_geometry_64_transfer_diagnostics.md
```

Reuse but do not overwrite as Step 29 setup:

```text
configs/step25_candidate_smoke_mesh_descriptor.json
configs/step25_candidate_smoke_voxel_descriptor.json
configs/step26_real_candidate_smoke_mesh_geometry.json
configs/step26_real_candidate_smoke_voxel_geometry.json
outputs/step25_candidate_manifest/candidate_manifest.json
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json
outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json
outputs/step28_quality_report_aggregation/quality_report_summary.json
outputs/step28_artifact_manifest/artifact_summary.json
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Required Scope Language

These exact phrases must appear across docs and the Step 29 report:

```text
Step 29 is controlled real geometry 64^3 short-window stability envelope.
Step 29 extends Step 28 transfer diagnostics conservatively.
Step 29 is not real squid validation.
Step 29 does not implement squid actuation.
Step 29 does not implement squid swimming.
Step 29 does not implement new FSI physics.
Step 29 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
```

Forbidden claims:

```text
real squid simulation is validated
validated squid swimming
squid actuation is implemented
production-ready sharp-interface FSI
final solver readiness
production mesh repair is complete
automatic remeshing is implemented
strict momentum-conserving FSI is complete
link_area_experimental is physically superior
engineering transfer is physically validated
implements two_phase
implements contact_angle
```

The contract test should scan docs and the report for forbidden claims, but it should not scan this goal file because the goal intentionally records the forbidden-claims list.

## 6. Step 29 Driver Matrix

Required 64^3 paired moving-boundary rows:

```text
real_candidate_smoke_mesh 64 moving_boundary engineering
real_candidate_smoke_mesh 64 moving_boundary link_area_experimental

real_candidate_smoke_voxel 64 moving_boundary engineering
real_candidate_smoke_voxel 64 moving_boundary link_area_experimental
```

Rows:

```text
2 candidates x 2 transfer rows = 4 driver rows
```

Penalty and none rows are deliberately excluded from Step 29. Step 29 should spend runtime only on the conservative 20-step stability envelope for the Step 28 transfer matrix.

Required config parameters:

```text
coupling_mode = moving_boundary
n_grid = 64
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 5
output_interval = 1
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
```

Mode/transfer requirements:

```text
engineering row: reaction_transfer_mode = engineering
link-area row: reaction_transfer_mode = link_area_experimental
```

For link-area rows:

```text
link_area_policy = inverse_length
link_area_scale_min = 0.25
link_area_scale_max = 2.0
```

Step 29 must not require or claim that link_area_experimental is better than engineering. The comparison remains diagnostic and bounded only.

## 7. General Driver Acceptance

Every Step 29 driver row must satisfy:

```text
completed_lbm_steps >= 20
total_mpm_substeps >= 100
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
projected_mass > 0
active_cell_count > 0
cell_force_max_norm == 0
bb_link_count_min > 0
bb_link_count_max > 0
active_reaction_particle_count_max > 0
hydro_force_max_norm > 0
has_nan == false
has_inf == false
stable == true
quality_check_enabled == true
quality_check_strict == true
quality_gate_strict == true
quality_pass == true
quality_severity == ok
quality_warnings_count == 0
quality_reasons_count == 0
```

Link-area rows must also satisfy:

```text
area_scale_final finite
raw_area_scale_final finite
0.25 <= area_scale_final <= 2.0
0.25 <= area_scale_min <= area_scale_max <= 2.0
```

Quality-report acceptance:

```text
mesh rows:
  vertices_count > 0
  faces_count > 0
  boundary_edge_count == 0
  degenerate_face_count == 0
  nonmanifold_edge_count == 0

voxel rows:
  occupied_count > 0
  connected_component_count == 1
  largest_component_fraction == 1.0
```

## 8. Runner Contracts

### 8.1 Candidate Fingerprint Guard

Script:

```text
baseline_tests/run_step29_candidate_fingerprint_guard.py
```

Outputs:

```text
outputs/step29_candidate_fingerprint_guard/fingerprint_guard.csv
outputs/step29_candidate_fingerprint_guard/fingerprint_guard.json
logs/step29_candidate_fingerprint_guard.log
```

Checks:

```text
row_count == 2
pass_count == 2
candidate_id matches Step 25 manifest
geometry_type matches Step 25 manifest
sha256 matches Step 25 manifest
size_bytes matches Step 25 manifest
Step 26 geometry_config geometry_file matches descriptor source_file
quality_check_enabled == true in generated GeometryConfig
quality_check_strict == true in generated GeometryConfig
no private absolute path
```

Log marker:

```text
[OK] Step 29 candidate fingerprint guard finished
```

### 8.2 64 Stability Driver

Script:

```text
baseline_tests/run_step29_64_stability_driver.py
```

Outputs:

```text
outputs/step29_64_stability_driver/stability_driver_results.csv
outputs/step29_64_stability_driver/stability_driver_results.npz
outputs/step29_64_stability_driver/stability_driver_results.json
outputs/step29_64_stability_driver/<case>/diagnostics_timeseries.csv
outputs/step29_64_stability_driver/<case>/diagnostics_timeseries.npz
outputs/step29_64_stability_driver/<case>/geometry_quality_report.json
outputs/step29_64_stability_driver/<case>/driver_timing.json
logs/step29_64_stability_driver.log
```

Checks:

```text
row_count == 4
stable_count == 4
quality_report_count == 4
quality_pass_count == 4
strict_count == 4
mesh_row_count == 2
voxel_row_count == 2
engineering_row_count == 2
link_area_row_count == 2
all general driver acceptance checks pass
all link-area-specific checks pass
```

Log marker:

```text
[OK] Step 29 64 stability driver finished
```

### 8.3 Stability Envelope Summary

Script:

```text
baseline_tests/run_step29_stability_envelope_summary.py
```

Inputs:

```text
outputs/step29_64_stability_driver/<case>/diagnostics_timeseries.csv
```

Outputs:

```text
outputs/step29_stability_envelope_summary/stability_envelope.csv
outputs/step29_stability_envelope_summary/stability_envelope.json
logs/step29_stability_envelope_summary.log
```

Required fields:

```text
candidate_id
geometry_type
reaction_transfer_mode
diagnostic_row_count
step_min
step_max
rho_min_observed
rho_max_observed
lbm_max_v_observed
mpm_min_J_observed
mpm_max_speed_observed
projected_mass_min
projected_mass_max
active_cell_count_min
active_cell_count_max
hydro_force_max_norm_max
bb_link_count_min
bb_link_count_max
stable_envelope_pass
```

Checks:

```text
row_count == 4
pass_count == 4
diagnostic_row_count >= 21
step_min == 0
step_max == 20
rho_min_observed > 0.95
rho_max_observed < 1.05
lbm_max_v_observed < 0.1
mpm_min_J_observed > 0
mpm_max_speed_observed < 10
projected_mass_min > 0
active_cell_count_min > 0
stable_envelope_pass == true
```

Log marker:

```text
[OK] Step 29 stability envelope summary finished
```

### 8.4 Engineering Vs Link-Area Envelope

Script:

```text
baseline_tests/run_step29_engineering_vs_link_area_envelope.py
```

Inputs:

```text
outputs/step29_stability_envelope_summary/stability_envelope.csv
outputs/step29_64_stability_driver/stability_driver_results.csv
```

Outputs:

```text
outputs/step29_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.csv
outputs/step29_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.json
logs/step29_engineering_vs_link_area_envelope.log
```

Required fields:

```text
candidate_id
geometry_type
rho_min_delta
rho_max_delta
lbm_max_v_delta
mpm_min_J_delta
projected_mass_delta
hydro_force_max_norm_delta
active_cell_count_delta
bb_link_count_delta
link_area_area_scale_final
comparison_pass
```

Checks:

```text
row_count == 2
pass_count == 2
comparison_pass == true
abs(rho_min_delta) <= 1e-3
abs(rho_max_delta) <= 1e-3
abs(lbm_max_v_delta) <= 1e-3
abs(mpm_min_J_delta) <= 1e-3
abs(projected_mass_delta) <= 1e-4
active_cell_count_delta == 0
abs(bb_link_count_delta) <= 512
0.25 <= link_area_area_scale_final <= 2.0
```

Log marker:

```text
[OK] Step 29 engineering vs link-area envelope finished
```

### 8.5 Force And Reaction Envelope

Script:

```text
baseline_tests/run_step29_force_reaction_envelope.py
```

Outputs:

```text
outputs/step29_force_reaction_envelope/force_reaction_envelope.csv
outputs/step29_force_reaction_envelope/force_reaction_envelope.json
logs/step29_force_reaction_envelope.log
```

Required fields:

```text
candidate_id
geometry_type
reaction_transfer_mode
post_step_row_count
hydro_force_min
hydro_force_max
hydro_force_final
max_grid_reaction_norm_min
max_grid_reaction_norm_max
max_grid_reaction_norm_final
active_reaction_particle_count_min
active_reaction_particle_count_max
bb_link_count_min
bb_link_count_max
bb_max_correction_max
finite_pass
positive_post_step_pass
```

Checks:

```text
row_count == 4
pass_count == 4
post_step_row_count >= 20
finite_pass == true
positive_post_step_pass == true
hydro_force_max > 0
max_grid_reaction_norm_max > 0
active_reaction_particle_count_max > 0
bb_link_count_min > 0 after step 0
```

Log marker:

```text
[OK] Step 29 force reaction envelope finished
```

### 8.6 Area-Scale Envelope

Script:

```text
baseline_tests/run_step29_area_scale_envelope.py
```

Outputs:

```text
outputs/step29_area_scale_envelope/area_scale_envelope.csv
outputs/step29_area_scale_envelope/area_scale_envelope.json
logs/step29_area_scale_envelope.log
```

Checks:

```text
row_count == 2
pass_count == 2
finite_pass == true
bounded_pass == true
0.25 <= area_scale_min_observed <= area_scale_max_observed <= 2.0
area_scale_final finite
raw_area_scale finite
```

Hitting a bound is a diagnostic finding, not an automatic failure, unless a row is non-finite or outside configured bounds.

Log marker:

```text
[OK] Step 29 area-scale envelope finished
```

### 8.7 Step 28 Prefix Regression

Script:

```text
baseline_tests/run_step29_step28_prefix_regression.py
```

Purpose:

Step 29 runs 20 steps. Compare the Step 29 step-10 prefix diagnostics against the corresponding Step 28 final step-10 diagnostics.

Inputs:

```text
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv
outputs/step29_64_stability_driver/<case>/diagnostics_timeseries.csv
```

Outputs:

```text
outputs/step29_step28_prefix_regression/step28_prefix_regression.csv
outputs/step29_step28_prefix_regression/step28_prefix_regression.json
logs/step29_step28_prefix_regression.log
```

Checks:

```text
row_count == 4
pass_count == 4
abs(rho_min_delta) <= 1e-5
abs(rho_max_delta) <= 1e-5
abs(lbm_max_v_delta) <= 1e-5
abs(mpm_min_J_delta) <= 1e-5
abs(projected_mass_delta) <= 5e-5
active_cell_count_delta == 0
bb_link_count_delta == 0
```

If an exact field name differs between final summary rows and time-series rows, use the semantically matching field and record it in the report. Do not widen tolerances unless a failed artifact proves a legitimate deterministic difference and the report records the reason.

Log marker:

```text
[OK] Step 29 Step 28 prefix regression finished
```

### 8.8 Quality Report Aggregation

Script:

```text
baseline_tests/run_step29_quality_report_aggregation.py
```

Outputs:

```text
outputs/step29_quality_report_aggregation/quality_report_summary.csv
outputs/step29_quality_report_aggregation/quality_report_summary.json
logs/step29_quality_report_aggregation.log
```

Checks:

```text
quality_report_count == 4
strict_count == 4
pass_count == 4
error_count == 0
warning_count == 0
mesh_row_count == 2
voxel_row_count == 2
quality_report_total_size_bytes > 0
quality_report_max_size_bytes < 100000
```

Log marker:

```text
[OK] Step 29 quality report aggregation finished
```

### 8.9 Step 28 Regression Guard

Script:

```text
baseline_tests/run_step29_step28_regression_guard.py
```

Inputs:

```text
STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json
outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json
outputs/step28_quality_report_aggregation/quality_report_summary.json
outputs/step28_artifact_manifest/artifact_summary.json
```

Outputs:

```text
outputs/step29_step28_regression_guard/step28_regression_guard.csv
outputs/step29_step28_regression_guard/step28_regression_guard.json
logs/step29_step28_regression_guard.log
```

Checks:

```text
Step 28 report exists
Step 28 driver_row_count == 4
Step 28 stable_count == 4
Step 28 quality_report_count == 4
Step 28 quality pass_count == 4
Step 28 engineering-vs-link-area pass_count == 2
Step 28 artifact large_file_count == 0
Step 28 artifact raw_candidate_large_file_count == 0
Step 28 artifact scan_data_file_count == 0
Step 28 artifact private_absolute_path_count == 0
```

Log marker:

```text
[OK] Step 29 Step 28 regression guard finished
```

### 8.10 Artifact Manifest

Script:

```text
baseline_tests/run_step29_artifact_manifest.py
```

Outputs:

```text
outputs/step29_artifact_manifest/artifact_manifest.csv
outputs/step29_artifact_manifest/artifact_summary.csv
outputs/step29_artifact_manifest/artifact_summary.json
logs/step29_artifact_manifest.log
```

Budget:

```text
large_file_count == 0
raw_candidate_large_file_count == 0
scan_data_file_count == 0
private_absolute_path_count == 0
step29_total_size_mb < 20
repo total_size_mb < 175
step29_vtr_count == 0
step29_particle_npy_count == 0
step29_quality_report_count == 4
```

The artifact manifest script must avoid self-referential size instability by excluding its own `outputs/step29_artifact_manifest/` output directory from the scanned rows before summarizing.

Log marker:

```text
[OK] Step 29 artifact manifest finished
```

## 9. Contract Test Requirements

Create:

```text
tests/test_step29_controlled_real_geometry_64_stability_envelope_contract.py
```

Required tests:

```text
test_step29_required_artifacts_exist
test_step29_driver_configs_are_valid
test_step29_candidate_fingerprint_guard_is_valid
test_step29_stability_driver_outputs_are_valid
test_step29_stability_envelope_summary_is_valid
test_step29_engineering_vs_link_area_envelope_is_valid
test_step29_force_reaction_envelope_is_valid
test_step29_area_scale_envelope_is_valid
test_step29_step28_prefix_regression_is_valid
test_step29_quality_report_aggregation_is_valid
test_step29_step28_regression_guard_is_valid
test_step29_default_modes_remain_unchanged
test_step29_docs_scope_and_forbidden_claims_are_valid
test_step29_artifact_budget_is_valid
test_step29_report_acceptance_complete
```

The contract test must verify:

- every required Step 29 source/config/doc/baseline file exists;
- every required Step 29 output exists after baselines run;
- generated Step 29 driver configs use 64^3, 20 LBM steps, 5 MPM substeps per LBM step, strict quality gates, no VTK, and no particle output;
- Step 29 configs are all moving_boundary rows;
- candidate fingerprint guard matches Step 25 accepted manifest;
- Step 26 geometry configs remain valid through `GeometryConfig`;
- all four stability driver rows pass;
- all stability driver rows are stable;
- all stability driver rows write strict quality reports;
- stability envelope summary passes for every row;
- engineering-vs-link-area envelope passes for mesh and voxel;
- force/reaction envelopes are finite and positive where required;
- area-scale envelope passes for both link-area rows;
- Step 28 prefix regression passes at step 10;
- Step 28 regression guard passes;
- defaults remain disabled in `src/geometry_config.py` and `src/fsi_config.py`;
- docs and report include required scope language;
- docs and report do not include forbidden claims;
- artifact budget passes;
- `logs/step29_pytest.log` exists;
- all expected Step 29 logs contain success markers;
- `external/taichi_LBM3D` is unchanged.

Make the test compatible with both the Taichi env and the ECC pre-push hook environment. Avoid importing `src` package-level `__init__` in the contract test if that would require optional packages missing in the hook environment.

## 10. Required Report

Create:

```text
STEP29_CONTROLLED_REAL_GEOMETRY_64_STABILITY_ENVELOPE_REPORT.md
```

Required sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. Candidate Fingerprint Guard
## 5. 64^3 Stability Driver
## 6. Stability Envelope Summary
## 7. Engineering Vs Link-Area Envelope
## 8. Force And Reaction Envelope
## 9. Area-Scale Envelope
## 10. Step 28 Prefix Regression
## 11. Quality Report Aggregation
## 12. Step 28 Regression Guard
## 13. Artifact Manifest Summary
## 14. Verification Commands
## 15. GitHub Sync Information
## 16. Acceptance Checklist
## 17. Decision For Step 30
```

The report must include:

- exact commands;
- exact artifact paths;
- exact row counts;
- exact summary values;
- stability envelope values;
- engineering-vs-link-area envelope deltas;
- force/reaction diagnostic envelope values;
- area-scale envelope values;
- Step 28 prefix regression deltas;
- artifact budget numbers;
- target remote branch;
- final commit hash in the completion message after push.

## 11. Verification Command Order

Run in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step29_common.py baseline_tests\run_step29_candidate_fingerprint_guard.py baseline_tests\run_step29_64_stability_driver.py baseline_tests\run_step29_stability_envelope_summary.py baseline_tests\run_step29_engineering_vs_link_area_envelope.py baseline_tests\run_step29_force_reaction_envelope.py baseline_tests\run_step29_area_scale_envelope.py baseline_tests\run_step29_step28_prefix_regression.py baseline_tests\run_step29_quality_report_aggregation.py baseline_tests\run_step29_step28_regression_guard.py baseline_tests\run_step29_artifact_manifest.py tests\test_step29_controlled_real_geometry_64_stability_envelope_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_64_stability_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_stability_envelope_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_engineering_vs_link_area_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_force_reaction_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_area_scale_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_step28_prefix_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_step28_regression_guard.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step29_controlled_real_geometry_64_stability_envelope_contract.py -q

pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Also write full pytest output to:

```text
logs/step29_pytest.log
```

If any baseline fails, stop and diagnose the failed artifact. Do not weaken thresholds, remove no-claim checks, widen tolerances without artifact evidence, or add solver shortcuts to force a pass.

## 12. Commit And Push Requirements

After Step 29 implementation is accepted locally:

1. Review `git diff`.
2. Confirm `external/taichi_LBM3D` is unchanged.
3. Confirm raw large candidate geometry and scan data are not staged.
4. Commit all relevant Step 29 code, configs, docs, logs, outputs, tests, goal, and report.
5. Use this conventional commit message:

```text
test: add step29 controlled real geometry 64 stability envelope
```

6. Push to `origin/main`. The user has already approved push in the Step 29 request.
7. Report the final commit hash and remote branch in the completion message.

Do not add local raw real geometry, scan data, private absolute-path manifests, `.vtr`, or particle `.npy` outputs.

## 13. Acceptance Checklist

The final Step 29 report must include this checklist with every accepted item checked:

```text
- [ ] candidate fingerprint guard passes
- [ ] Step 25 manifest fingerprints match current candidate files
- [ ] Step 26 generated GeometryConfig files remain valid
- [ ] mesh 64^3 moving_boundary engineering 20-step row passes
- [ ] mesh 64^3 moving_boundary link_area 20-step row passes
- [ ] voxel 64^3 moving_boundary engineering 20-step row passes
- [ ] voxel 64^3 moving_boundary link_area 20-step row passes
- [ ] every Step 29 driver row writes geometry_quality_report.json
- [ ] every Step 29 quality gate is strict
- [ ] every Step 29 quality report passes
- [ ] quality warning count == 0
- [ ] quality error count == 0
- [ ] all driver rows have completed_lbm_steps >= 20
- [ ] all driver rows have total_mpm_substeps >= 100
- [ ] rho_min > 0.95
- [ ] rho_max < 1.05
- [ ] lbm_max_v < 0.1
- [ ] mpm_min_J > 0
- [ ] mpm_max_speed < 10
- [ ] projected_mass > 0
- [ ] active_cell_count > 0
- [ ] no NaN
- [ ] no Inf
- [ ] moving_boundary rows keep cell_force_max_norm == 0
- [ ] moving_boundary rows have bb_link_count > 0
- [ ] moving_boundary rows have active_reaction_particle_count_max > 0
- [ ] hydro_force_max_norm is finite and positive after nonzero steps
- [ ] max_grid_reaction_norm is finite
- [ ] stability envelope summary passes
- [ ] engineering vs link_area envelope passes for mesh
- [ ] engineering vs link_area envelope passes for voxel
- [ ] force/reaction envelope passes
- [ ] link_area rows have finite bounded area_scale
- [ ] area_scale envelope summary passes
- [ ] Step 28 prefix regression passes at step=10
- [ ] Step 28 regression guard passes
- [ ] default quality_check_enabled remains false
- [ ] default quality_check_strict remains false
- [ ] default reaction_transfer_mode remains engineering
- [ ] no FSI formula changes
- [ ] no moving bounce-back formula changes
- [ ] no LBM formula changes
- [ ] no MPM constitutive formula changes
- [ ] no projection formula changes
- [ ] no production mesh repair claims
- [ ] no automatic remeshing claims
- [ ] no real squid validation claims
- [ ] no squid swimming claims
- [ ] no squid actuation claims
- [ ] no production sharp-interface FSI claims
- [ ] no final readiness claims
- [ ] no external/taichi_LBM3D edits
- [ ] no committed large raw real geometry
- [ ] no committed scan data
- [ ] no private absolute paths in committed outputs
- [ ] no Step 29 .vtr outputs
- [ ] no Step 29 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 29 output total size budget passes
- [ ] repo artifact_summary total_size_mb < 175
- [ ] logs/step29_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 29 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 29 artifacts are pushed to origin/main
```

## 14. Decision For Step 30

If Step 29 passes, Step 30 should not jump directly to actuation. A conservative Step 30 direction is:

```text
Step 30 Controlled Squid Proxy Region Geometry Contract
```

Step 30 should define region semantics for a squid-like proxy without actuation:

```text
mantle outer region
mantle cavity proxy
funnel or siphon outlet proxy
head and arms coarse proxy
optional fin region
body axis
reference length
region IDs
```

Only after the squid proxy region geometry and projection/driver smoke evidence are stable should a later step consider prescribed mantle/funnel kinematics. Step 29 must remain only a 64^3 short-window stability envelope.
