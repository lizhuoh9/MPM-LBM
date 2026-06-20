# Step 28 Goal: Controlled Real Geometry 64 Transfer Diagnostics

This file is the authoritative execution contract for Step 28 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 28 starts only when a goal explicitly references this file.

## 1. Status Before Step 28

Step 27 is accepted on GitHub at commit:

```text
eb4de4e32606c7ed57c97c6f5fcfb00ebd681a20
```

Step 27 established controlled real geometry 64^3 short driver feasibility. The accepted evidence includes:

- `STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md`;
- candidate fingerprint guard against the Step 25 manifest;
- six 64^3 short driver rows for the accepted mesh and voxel candidates;
- mesh 64^3 rows for penalty engineering, moving_boundary engineering, and moving_boundary link_area_experimental;
- voxel 64^3 rows for penalty engineering, moving_boundary engineering, and moving_boundary link_area_experimental;
- all six rows completed 5 LBM steps and 25 MPM substeps;
- all six rows were stable, finite, and strict quality-passing;
- all six rows wrote `geometry_quality_report.json`;
- driver/projection alignment passed for all six rows against Step 26 64^3 projection-only diagnostics;
- active-cell delta was 0 for every Step 27 alignment row;
- Step 27 summary had `driver_row_count = 6`, `stable_count = 6`, `quality_report_count = 6`, and `quality_pass_count = 6`;
- Step 27 quality aggregation had 6 strict reports, 6 pass, 0 warning, and 0 error;
- `logs/step27_pytest.log` showed the full test suite passed;
- Step 27 artifact summary had `large_file_count = 0`, no Step 27 `.vtr`, no Step 27 particle `.npy`, no raw candidate large files, no scan data, and no private absolute paths;
- no edits to `external/taichi_LBM3D`;
- no solver/coupler/LBM/MPM/projection formula changes.

Step 28 must preserve all Step 25, Step 26, and Step 27 boundaries and evidence.

## 2. Step 28 Objective

Correct description:

```text
Step 28 is controlled real geometry 64^3 transfer diagnostics.
```

Required scope sentence:

```text
Step 28 compares engineering and link_area_experimental transfer diagnostically.
```

Long-form objective:

```text
Step 28 compares 64^3 engineering and link_area_experimental moving-boundary transfer for the accepted controlled real-geometry smoke candidates, adds force/reaction diagnostics and area-scale envelope summaries, and remains a diagnostic feasibility step only.
```

Step 28 carries the accepted Step 25 real-geometry smoke candidates from Step 27 64^3 short-driver feasibility into a 64^3 paired moving-boundary transfer diagnostic. Step 28 is not real squid validation.

Step 28 must prove:

1. The accepted Step 25 candidate fingerprints still match the Step 25 manifest.
2. The Step 26 generated driver-ready `GeometryConfig` files remain valid and strict.
3. The selected 64^3 Step 28 paired moving-boundary driver configs are valid, strict, and output-budgeted.
4. The 64^3 moving_boundary engineering and link_area_experimental rows are directly comparable for each candidate.
5. The link_area_experimental rows remain inside the already validated stability envelope.
6. Area-scale diagnostics are finite and bounded for both link-area rows.
7. Reaction and force diagnostics are finite, reportable, and comparable for both engineering and link-area transfer.
8. Step 28 10-step rows preserve the Step 27 5-step prefix diagnostics within explicit tolerances.
9. Step 27 regression evidence remains intact.
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
changes to the moving bounce-back formula
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
engineering vs link_area comparison scripts
force/reaction diagnostic aggregation from existing diagnostics
area_scale envelope summaries
short-window 64^3 paired moving-boundary driver reruns
Step 27 prefix regression comparison
Step 27 regression guard
quality report aggregation
driver timing and artifact diagnostics
docs, report, contract test, logs, small outputs
artifact budget checks
commit and push of relevant Step 28 code, configs, docs, logs, outputs, tests, goal, and report
```

Any change that touches core solver formulas is out of scope and must be rejected.

## 4. Required Files

Create:

```text
STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_GOAL.md
STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md

docs/28_controlled_real_geometry_64_transfer_diagnostics.md

configs/step28_compare_real_candidate_smoke_mesh_64_moving_boundary.json
configs/step28_compare_real_candidate_smoke_mesh_64_link_area.json
configs/step28_compare_real_candidate_smoke_voxel_64_moving_boundary.json
configs/step28_compare_real_candidate_smoke_voxel_64_link_area.json

baseline_tests/step28_common.py
baseline_tests/run_step28_candidate_fingerprint_guard.py
baseline_tests/run_step28_64_transfer_pair_driver.py
baseline_tests/run_step28_engineering_vs_link_area_comparison.py
baseline_tests/run_step28_force_reaction_diagnostics.py
baseline_tests/run_step28_area_scale_envelope.py
baseline_tests/run_step28_step27_prefix_regression.py
baseline_tests/run_step28_quality_report_aggregation.py
baseline_tests/run_step28_step27_regression_guard.py
baseline_tests/run_step28_artifact_manifest.py

tests/test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py
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
```

Reuse but do not overwrite as Step 28 setup:

```text
configs/step25_candidate_smoke_mesh_descriptor.json
configs/step25_candidate_smoke_voxel_descriptor.json
configs/step26_real_candidate_smoke_mesh_geometry.json
configs/step26_real_candidate_smoke_voxel_geometry.json
outputs/step25_candidate_manifest/candidate_manifest.json
outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv
outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv
outputs/step27_64_driver_summary/driver_64_summary.json
outputs/step27_quality_report_aggregation/quality_report_summary.json
outputs/step27_artifact_manifest/artifact_summary.json
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Required Scope Language

These exact phrases must appear across docs and the Step 28 report:

```text
Step 28 is controlled real geometry 64^3 transfer diagnostics.
Step 28 compares engineering and link_area_experimental transfer diagnostically.
Step 28 is not real squid validation.
Step 28 does not implement squid actuation.
Step 28 does not implement squid swimming.
Step 28 does not implement new FSI physics.
Step 28 does not validate production sharp-interface FSI.
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

## 6. Step 28 Driver Matrix

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

Penalty rows are deliberately excluded from the required Step 28 matrix. Step 27 already validated penalty feasibility at 64^3. Step 28 should spend runtime on paired moving-boundary transfer diagnostics with meaningful force/reaction and area-scale envelopes.

Required config parameters:

```text
coupling_mode = moving_boundary
n_grid = 64
n_particles = 4096
n_lbm_steps = 10
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

Step 28 must not require or claim that link_area_experimental is better than engineering. The comparison is diagnostic and bounded only.

## 7. General Driver Acceptance

Every Step 28 driver row must satisfy:

```text
completed_lbm_steps >= 10
total_mpm_substeps >= 50
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
baseline_tests/run_step28_candidate_fingerprint_guard.py
```

Outputs:

```text
outputs/step28_candidate_fingerprint_guard/fingerprint_guard.csv
outputs/step28_candidate_fingerprint_guard/fingerprint_guard.json
logs/step28_candidate_fingerprint_guard.log
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
[OK] Step 28 candidate fingerprint guard finished
```

### 8.2 64 Transfer Pair Driver

Script:

```text
baseline_tests/run_step28_64_transfer_pair_driver.py
```

Outputs:

```text
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.npz
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json
outputs/step28_64_transfer_pair_driver/<case>/diagnostics_timeseries.csv
outputs/step28_64_transfer_pair_driver/<case>/diagnostics_timeseries.npz
outputs/step28_64_transfer_pair_driver/<case>/geometry_quality_report.json
outputs/step28_64_transfer_pair_driver/<case>/driver_timing.json
logs/step28_64_transfer_pair_driver.log
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
[OK] Step 28 64 transfer pair driver finished
```

### 8.3 Engineering Vs Link-Area Comparison

Script:

```text
baseline_tests/run_step28_engineering_vs_link_area_comparison.py
```

Inputs:

```text
outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv
```

Outputs:

```text
outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.csv
outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json
logs/step28_engineering_vs_link_area_comparison.log
```

Compare one engineering row with one link-area row per candidate.

Required fields:

```text
candidate_id
geometry_type
n_grid
engineering_rho_min
link_area_rho_min
rho_min_delta
engineering_rho_max
link_area_rho_max
rho_max_delta
engineering_lbm_max_v
link_area_lbm_max_v
lbm_max_v_delta
engineering_mpm_min_J
link_area_mpm_min_J
mpm_min_J_delta
engineering_projected_mass
link_area_projected_mass
projected_mass_delta
engineering_hydro_force_max_norm
link_area_hydro_force_max_norm
hydro_force_max_norm_delta
link_area_area_scale_final
comparison_pass
```

Checks:

```text
row_count == 2
pass_count == 2
comparison_pass == true for mesh
comparison_pass == true for voxel
abs(rho_min_delta) <= 5e-4
abs(rho_max_delta) <= 5e-4
abs(lbm_max_v_delta) <= 5e-4
abs(mpm_min_J_delta) <= 5e-4
abs(projected_mass_delta) <= 5e-5
link_area_area_scale_final finite
0.25 <= link_area_area_scale_final <= 2.0
```

Log marker:

```text
[OK] Step 28 engineering vs link-area comparison finished
```

### 8.4 Force And Reaction Diagnostics

Script:

```text
baseline_tests/run_step28_force_reaction_diagnostics.py
```

Inputs:

```text
outputs/step28_64_transfer_pair_driver/<case>/diagnostics_timeseries.csv
```

Outputs:

```text
outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.csv
outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.json
logs/step28_force_reaction_diagnostics.log
```

Required fields:

```text
candidate_id
geometry_type
reaction_transfer_mode
row_count
post_step_positive_rows
hydro_force_max_norm_min
hydro_force_max_norm_max
hydro_force_max_norm_final
max_grid_reaction_norm_min
max_grid_reaction_norm_max
max_grid_reaction_norm_final
active_reaction_particle_count_min
active_reaction_particle_count_max
bb_link_count_min
bb_link_count_max
bb_max_correction_max
finite_pass
diagnostic_pass
```

Checks:

```text
row_count >= 10
hydro_force_max_norm finite
hydro_force_max_norm > 0 for nonzero steps
max_grid_reaction_norm finite
active_reaction_particle_count_max > 0
bb_link_count_max > 0
bb_max_correction_max finite
finite_pass == true
diagnostic_pass == true
```

If step 0 has zero reaction count, the script must separate all-step and post-step statistics and must not fail solely because step 0 is zero.

Log marker:

```text
[OK] Step 28 force reaction diagnostics finished
```

### 8.5 Area-Scale Envelope

Script:

```text
baseline_tests/run_step28_area_scale_envelope.py
```

Inputs:

```text
outputs/step28_64_transfer_pair_driver/<link_area_case>/diagnostics_timeseries.csv
```

Outputs:

```text
outputs/step28_area_scale_envelope/area_scale_envelope.csv
outputs/step28_area_scale_envelope/area_scale_envelope.json
logs/step28_area_scale_envelope.log
```

Required fields:

```text
candidate_id
geometry_type
n_grid
area_scale_initial
area_scale_min_observed
area_scale_max_observed
area_scale_final
area_scale_config_min
area_scale_config_max
raw_area_scale_min
raw_area_scale_max
hit_lower_bound
hit_upper_bound
finite_pass
bounded_pass
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
[OK] Step 28 area-scale envelope finished
```

### 8.6 Step 27 Prefix Regression

Script:

```text
baseline_tests/run_step28_step27_prefix_regression.py
```

Purpose:

Step 28 runs 10 steps. Compare the Step 28 step-5 prefix diagnostics against the corresponding Step 27 final step-5 diagnostics.

Inputs:

```text
outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv
outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv
outputs/step28_64_transfer_pair_driver/<case>/diagnostics_timeseries.csv
```

Compare:

```text
mesh moving_boundary engineering
mesh moving_boundary link_area_experimental
voxel moving_boundary engineering
voxel moving_boundary link_area_experimental
```

Outputs:

```text
outputs/step28_step27_prefix_regression/step27_prefix_regression.csv
outputs/step28_step27_prefix_regression/step27_prefix_regression.json
logs/step28_step27_prefix_regression.log
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
[OK] Step 28 Step 27 prefix regression finished
```

### 8.7 Quality Report Aggregation

Script:

```text
baseline_tests/run_step28_quality_report_aggregation.py
```

Outputs:

```text
outputs/step28_quality_report_aggregation/quality_report_summary.csv
outputs/step28_quality_report_aggregation/quality_report_summary.json
logs/step28_quality_report_aggregation.log
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
[OK] Step 28 quality report aggregation finished
```

### 8.8 Step 27 Regression Guard

Script:

```text
baseline_tests/run_step28_step27_regression_guard.py
```

Inputs:

```text
STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md
outputs/step27_64_driver_summary/driver_64_summary.json
outputs/step27_quality_report_aggregation/quality_report_summary.json
outputs/step27_artifact_manifest/artifact_summary.json
```

Outputs:

```text
outputs/step28_step27_regression_guard/step27_regression_guard.csv
outputs/step28_step27_regression_guard/step27_regression_guard.json
logs/step28_step27_regression_guard.log
```

Checks:

```text
Step 27 report exists
Step 27 driver_row_count == 6
Step 27 stable_count == 6
Step 27 quality_report_count == 6
Step 27 quality pass_count == 6
Step 27 artifact large_file_count == 0
Step 27 raw_candidate_large_file_count == 0
Step 27 scan_data_file_count == 0
Step 27 private_absolute_path_count == 0
```

Log marker:

```text
[OK] Step 28 Step 27 regression guard finished
```

### 8.9 Artifact Manifest

Script:

```text
baseline_tests/run_step28_artifact_manifest.py
```

Outputs:

```text
outputs/step28_artifact_manifest/artifact_manifest.csv
outputs/step28_artifact_manifest/artifact_summary.csv
outputs/step28_artifact_manifest/artifact_summary.json
logs/step28_artifact_manifest.log
```

Budget:

```text
large_file_count == 0
raw_candidate_large_file_count == 0
scan_data_file_count == 0
private_absolute_path_count == 0
step28_total_size_mb < 15
repo total_size_mb < 165
step28_vtr_count == 0
step28_particle_npy_count == 0
step28_quality_report_count == 4
```

The artifact manifest script must avoid self-referential size instability by excluding its own `outputs/step28_artifact_manifest/` output directory from the scanned rows before summarizing.

Log marker:

```text
[OK] Step 28 artifact manifest finished
```

## 9. Contract Test Requirements

Create:

```text
tests/test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py
```

Required tests:

```text
test_step28_required_artifacts_exist
test_step28_driver_configs_are_valid
test_step28_candidate_fingerprint_guard_is_valid
test_step28_transfer_pair_driver_outputs_are_valid
test_step28_engineering_vs_link_area_comparison_is_valid
test_step28_force_reaction_diagnostics_are_valid
test_step28_area_scale_envelope_is_valid
test_step28_step27_prefix_regression_is_valid
test_step28_quality_report_aggregation_is_valid
test_step28_step27_regression_guard_is_valid
test_step28_default_modes_remain_unchanged
test_step28_docs_scope_and_forbidden_claims_are_valid
test_step28_artifact_budget_is_valid
test_step28_report_acceptance_complete
```

The contract test must verify:

- every required Step 28 source/config/doc/baseline file exists;
- every required Step 28 output exists after baselines run;
- generated Step 28 driver configs use 64^3, 10 LBM steps, 5 MPM substeps per LBM step, strict quality gates, no VTK, and no particle output;
- Step 28 configs are all moving_boundary rows;
- candidate fingerprint guard matches Step 25 accepted manifest;
- Step 26 geometry configs remain valid through `GeometryConfig`;
- all four paired transfer driver rows pass;
- all paired transfer rows are stable;
- all paired transfer rows write strict quality reports;
- engineering-vs-link-area comparison passes for mesh and voxel;
- force/reaction diagnostics are finite and positive where required;
- area-scale envelope passes for both link-area rows;
- Step 27 prefix regression passes at step 5;
- Step 27 regression guard passes;
- defaults remain disabled in `src/geometry_config.py` and `src/fsi_config.py`;
- docs and report include required scope language;
- docs and report do not include forbidden claims;
- artifact budget passes;
- `logs/step28_pytest.log` exists;
- all expected Step 28 logs contain success markers;
- `external/taichi_LBM3D` is unchanged.

Make the test compatible with both the Taichi env and the ECC pre-push hook environment. Avoid importing `src` package-level `__init__` in the contract test if that would require optional packages missing in the hook environment.

## 10. Required Report

Create:

```text
STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md
```

Required sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. Candidate Fingerprint Guard
## 5. 64^3 Transfer Pair Driver
## 6. Engineering Vs Link-Area Comparison
## 7. Force And Reaction Diagnostics
## 8. Area-Scale Envelope
## 9. Step 27 Prefix Regression
## 10. Quality Report Aggregation
## 11. Step 27 Regression Guard
## 12. Artifact Manifest Summary
## 13. Verification Commands
## 14. GitHub Sync Information
## 15. Acceptance Checklist
## 16. Decision For Step 29
```

The report must include:

- exact commands;
- exact artifact paths;
- exact row counts;
- exact summary values;
- engineering-vs-link-area comparison deltas;
- force/reaction diagnostic envelope values;
- area-scale envelope values;
- Step 27 prefix regression deltas;
- artifact budget numbers;
- target remote branch;
- final commit hash in the completion message after push.

## 11. Verification Command Order

Run in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step28_common.py baseline_tests\run_step28_candidate_fingerprint_guard.py baseline_tests\run_step28_64_transfer_pair_driver.py baseline_tests\run_step28_engineering_vs_link_area_comparison.py baseline_tests\run_step28_force_reaction_diagnostics.py baseline_tests\run_step28_area_scale_envelope.py baseline_tests\run_step28_step27_prefix_regression.py baseline_tests\run_step28_quality_report_aggregation.py baseline_tests\run_step28_step27_regression_guard.py baseline_tests\run_step28_artifact_manifest.py tests\test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_64_transfer_pair_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_engineering_vs_link_area_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_force_reaction_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_area_scale_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_step27_prefix_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_step27_regression_guard.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py -q

pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Also write full pytest output to:

```text
logs/step28_pytest.log
```

If any baseline fails, stop and diagnose the failed artifact. Do not weaken thresholds, remove no-claim checks, widen tolerances without artifact evidence, or add solver shortcuts to force a pass.

## 12. Commit And Push Requirements

After Step 28 implementation is accepted locally:

1. Review `git diff`.
2. Confirm `external/taichi_LBM3D` is unchanged.
3. Confirm raw large candidate geometry and scan data are not staged.
4. Commit all relevant Step 28 code, configs, docs, logs, outputs, tests, goal, and report.
5. Use this conventional commit message:

```text
test: add step28 controlled real geometry 64 transfer diagnostics
```

6. Push to `origin/main` unless the user explicitly says not to push.
7. Report the final commit hash and remote branch in the completion message.

Do not add local raw real geometry, scan data, private absolute-path manifests, `.vtr`, or particle `.npy` outputs.

## 13. Acceptance Checklist

The final Step 28 report must include this checklist with every accepted item checked:

```text
- [ ] candidate fingerprint guard passes
- [ ] Step 25 manifest fingerprints match current candidate files
- [ ] Step 26 generated GeometryConfig files remain valid
- [ ] mesh 64^3 moving_boundary engineering 10-step row passes
- [ ] mesh 64^3 moving_boundary link_area 10-step row passes
- [ ] voxel 64^3 moving_boundary engineering 10-step row passes
- [ ] voxel 64^3 moving_boundary link_area 10-step row passes
- [ ] every Step 28 driver row writes geometry_quality_report.json
- [ ] every Step 28 quality gate is strict
- [ ] every Step 28 quality report passes
- [ ] quality warning count == 0
- [ ] quality error count == 0
- [ ] all driver rows have completed_lbm_steps >= 10
- [ ] all driver rows have total_mpm_substeps >= 50
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
- [ ] engineering vs link_area comparison passes for mesh
- [ ] engineering vs link_area comparison passes for voxel
- [ ] link_area rows have finite bounded area_scale
- [ ] area_scale envelope summary passes
- [ ] Step 27 prefix regression passes at step=5
- [ ] Step 27 regression guard passes
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
- [ ] no Step 28 .vtr outputs
- [ ] no Step 28 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 28 output total size budget passes
- [ ] repo artifact_summary total_size_mb < 165
- [ ] logs/step28_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 28 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 28 artifacts are pushed to origin/main
```

## 14. Decision For Step 29

If Step 28 passes, Step 29 should still not jump directly to swimming. A conservative Step 29 direction is:

```text
Step 29 Controlled Real Geometry 64^3 Short-Window Stability Envelope
```

Step 29 should use Step 28 diagnostics to extend the 64^3 moving_boundary engineering and link_area_experimental windows modestly, for example to 20 or 30 LBM steps, and continue to summarize stability envelope, force envelope, and area-scale envelope only. Step 29 must avoid actuation, swimming, production sharp-interface FSI claims, final readiness claims, production mesh repair, automatic remeshing, and solver formula changes.
