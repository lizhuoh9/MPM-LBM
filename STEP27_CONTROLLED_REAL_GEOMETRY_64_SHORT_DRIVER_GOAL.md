# Step 27 Goal: Controlled Real Geometry 64^3 Short Driver Feasibility

This file is the authoritative execution contract for Step 27 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 27 starts only when a goal explicitly references this file.

## 1. Status Before Step 27

Step 26 is accepted on GitHub at commit:

```text
2524b75
```

Step 26 established controlled real geometry projection-only and short driver feasibility. The accepted evidence includes:

- `STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md`;
- candidate fingerprint guard against the Step 25 manifest;
- driver-ready geometry configs for `real_candidate_smoke_mesh` and `real_candidate_smoke_voxel`;
- projection-only scale diagnostics for both candidates at `32^3`, `48^3`, and `64^3`;
- Step 25 projection regression for the `32^3` rows;
- `48^3` very short driver rows for both candidates across `none`, `penalty`, `moving_boundary` engineering, and `moving_boundary` link-area transfer;
- 8 strict `geometry_quality_report.json` artifacts;
- short driver summary with `driver_row_count = 8`, `stable_count = 8`, `quality_report_count = 8`, and `quality_pass_count = 8`;
- `large_file_count = 0`, no Step 26 `.vtr`, no Step 26 particle `.npy`, no raw candidate large files, no scan data, and no private absolute paths;
- `logs/step26_pytest.log` showing `211 passed`;
- no edits to `external/taichi_LBM3D`;
- no solver/coupler/LBM/MPM/projection formula changes.

Step 27 must preserve all Step 25 and Step 26 boundaries and evidence.

## 2. Step 27 Objective

Correct description:

```text
Step 27 is controlled real geometry 64^3 short driver feasibility.
```

Step 27 carries the accepted Step 25 real-geometry smoke candidates from Step 26 projection-only and `48^3` short-driver feasibility into a small `64^3` short-driver subset. Step 27 is not real squid validation.

Step 27 must prove:

1. The accepted Step 25 candidate fingerprints still match the Step 25 manifest.
2. The Step 26 generated driver-ready `GeometryConfig` files remain valid and strict.
3. The selected `64^3` driver configs are valid, strict, and output-budgeted.
4. A conservative `64^3` short-driver subset passes for both candidates.
5. Every Step 27 driver row writes and passes a strict `geometry_quality_report.json`.
6. Every Step 27 driver row completes at least 5 LBM steps and 25 MPM substeps.
7. Every Step 27 driver row is finite, stable, and free of NaN/Inf diagnostics.
8. Step 27 driver projected mass and active cells align with Step 26 `64^3` projection-only diagnostics within explicit tolerances.
9. Step 26 regression evidence remains intact.
10. Solver, coupler, LBM, MPM, moving-boundary, and projection formulas remain unchanged.
11. Artifact budgets remain controlled.
12. Raw large real geometry files and scan data are not committed.

## 3. Hard Boundaries

Do not implement:

- squid actuation;
- squid swimming;
- real squid validation claim;
- production sharp-interface FSI claim;
- final solver readiness claim;
- new FSI physics;
- new coupling formula;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to the moving bounce-back formula;
- changes to LBM step formulas;
- changes to MPM constitutive formulas;
- changes to projection formulas;
- production mesh repair;
- automatic remeshing;
- mesh cleanup or mesh fixing;
- scan-data processing pipeline;
- two-phase flow;
- contact angle physics;
- sparse storage;
- `ReducedSquidFSI`;
- edits to `external/taichi_LBM3D`;
- committing large raw real geometry;
- committing scan data;
- committing private absolute local geometry paths.

Allowed work:

- `64^3` short driver configs;
- `64^3` strict quality-gated driver reports;
- `64^3` driver/projection alignment comparison;
- Step 26 regression guard;
- quality report aggregation;
- driver timing and artifact diagnostics;
- docs, report, contract test, logs, small outputs;
- artifact budget checks;
- commit and push of relevant Step 27 code, docs, logs, configs, tests, and generated artifacts.

Any change that touches core solver formulas is out of scope and must be rejected.

## 4. Required Files

Create:

```text
STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_GOAL.md
STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md

docs/27_controlled_real_geometry_64_short_driver.md

configs/step27_driver_real_candidate_smoke_mesh_64_penalty.json
configs/step27_driver_real_candidate_smoke_mesh_64_moving_boundary.json
configs/step27_driver_real_candidate_smoke_mesh_64_link_area.json
configs/step27_driver_real_candidate_smoke_voxel_64_penalty.json
configs/step27_driver_real_candidate_smoke_voxel_64_moving_boundary.json
configs/step27_driver_real_candidate_smoke_voxel_64_link_area.json

baseline_tests/step27_common.py
baseline_tests/run_step27_candidate_fingerprint_guard.py
baseline_tests/run_step27_64_driver_mesh_feasibility.py
baseline_tests/run_step27_64_driver_voxel_feasibility.py
baseline_tests/run_step27_driver_projection_alignment.py
baseline_tests/run_step27_64_driver_summary.py
baseline_tests/run_step27_quality_report_aggregation.py
baseline_tests/run_step27_step26_regression_guard.py
baseline_tests/run_step27_artifact_manifest.py

tests/test_step27_controlled_real_geometry_64_short_driver_contract.py
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
```

Reuse but do not overwrite as part of Step 27:

```text
configs/step26_real_candidate_smoke_mesh_geometry.json
configs/step26_real_candidate_smoke_voxel_geometry.json
outputs/step26_projection_scale_diagnostics/projection_scale_results.json
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Required Scope Language

These exact phrases must appear across docs and the Step 27 report:

```text
Step 27 is controlled real geometry 64^3 short driver feasibility.
Step 27 is not real squid validation.
Step 27 does not implement squid actuation.
Step 27 does not implement squid swimming.
Step 27 does not implement new FSI physics.
Step 27 does not validate production sharp-interface FSI.
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
implements two_phase
implements contact_angle
```

The contract test should scan docs and the report for forbidden claims, but it should not scan this goal file because the goal intentionally records the forbidden-claims list.

## 6. Step 27 Driver Matrix

Required `64^3` short driver subset:

```text
real_candidate_smoke_mesh 64 penalty engineering
real_candidate_smoke_mesh 64 moving_boundary engineering
real_candidate_smoke_mesh 64 moving_boundary link_area_experimental

real_candidate_smoke_voxel 64 penalty engineering
real_candidate_smoke_voxel 64 moving_boundary engineering
real_candidate_smoke_voxel 64 moving_boundary link_area_experimental
```

Rows:

```text
2 candidates x 3 coupling rows = 6 driver rows
```

The `none` row is deliberately excluded from the required Step 27 matrix. Step 26 already validated `none` at `48^3`, and Step 26 already validated `64^3` projection-only diagnostics. Step 27 should spend runtime on the `64^3` coupling paths with meaningful force/reaction diagnostics.

Required config parameters:

```text
n_grid = 64
n_particles = 4096
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
output_interval = 5
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
```

Mode/transfer requirements:

```text
penalty: reaction_transfer_mode = engineering
moving_boundary engineering: reaction_transfer_mode = engineering
moving_boundary link-area: reaction_transfer_mode = link_area_experimental
```

For link-area rows:

```text
link_area_policy = inverse_length
link_area_scale_min = 0.25
link_area_scale_max = 2.0
```

## 7. General Driver Acceptance

Every driver row must satisfy:

```text
completed_lbm_steps >= 5
total_mpm_substeps >= 25
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
projected_mass > 0
active_cell_count > 0
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

Mode-specific acceptance:

```text
penalty:
  cell_force_max_norm > 0
  hydro_force_max_norm > 0
  bb_link_count_max == 0

moving_boundary engineering:
  cell_force_max_norm == 0
  hydro_force_max_norm > 0
  bb_link_count_max > 0
  active_reaction_particle_count_max > 0

moving_boundary link_area_experimental:
  cell_force_max_norm == 0
  hydro_force_max_norm > 0
  bb_link_count_max > 0
  active_reaction_particle_count_max > 0
  area_scale_final finite
  raw_area_scale_final finite
  0.25 <= area_scale_final <= 2.0
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

## 8. Driver/Projection Alignment

Compare Step 27 `64^3` driver projection diagnostics against Step 26 `64^3` projection-only diagnostics:

Step 26 reference inputs:

```text
outputs/step26_projection_scale_diagnostics/projection_scale_results.json
```

Known Step 26 `64^3` signatures:

```text
real_candidate_smoke_mesh:
  projected_mass ~= 0.6058260798454285
  active_cell_count = 110592

real_candidate_smoke_voxel:
  projected_mass ~= 0.09944107383489609
  active_cell_count = 31116
```

Acceptance:

```text
row_count == 6
candidate_id matches
n_grid == 64
abs(projected_mass_delta) <= 5e-5
abs(active_cell_count_delta) <= 32
alignment_pass == true
```

The active-cell tolerance is deliberately small but nonzero because driver initialization may include a short projection refresh path and the `64^3` coupling rows may use slightly different timing around diagnostics. Do not widen this tolerance unless a failed artifact proves a legitimate deterministic difference and the report records the reason.

## 9. Baseline Runner Contracts

### 9.1 Candidate Fingerprint Guard

Script:

```text
baseline_tests/run_step27_candidate_fingerprint_guard.py
```

Outputs:

```text
outputs/step27_candidate_fingerprint_guard/fingerprint_guard.csv
outputs/step27_candidate_fingerprint_guard/fingerprint_guard.json
logs/step27_candidate_fingerprint_guard.log
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
[OK] Step 27 candidate fingerprint guard finished
```

### 9.2 Mesh 64 Driver Feasibility

Script:

```text
baseline_tests/run_step27_64_driver_mesh_feasibility.py
```

Outputs:

```text
outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv
outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.npz
outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.json
outputs/step27_64_driver_mesh_feasibility/<case>/geometry_quality_report.json
outputs/step27_64_driver_mesh_feasibility/<case>/driver_timing.json
logs/step27_64_driver_mesh_feasibility.log
```

Checks:

```text
row_count == 3
stable_count == 3
quality_pass_count == 3
strict_count == 3
all general driver acceptance checks pass
all mode-specific checks pass
```

Log marker:

```text
[OK] Step 27 mesh 64 short driver feasibility finished
```

### 9.3 Voxel 64 Driver Feasibility

Script:

```text
baseline_tests/run_step27_64_driver_voxel_feasibility.py
```

Outputs:

```text
outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv
outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.npz
outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.json
outputs/step27_64_driver_voxel_feasibility/<case>/geometry_quality_report.json
outputs/step27_64_driver_voxel_feasibility/<case>/driver_timing.json
logs/step27_64_driver_voxel_feasibility.log
```

Checks:

```text
row_count == 3
stable_count == 3
quality_pass_count == 3
strict_count == 3
all general driver acceptance checks pass
all mode-specific checks pass
```

Log marker:

```text
[OK] Step 27 voxel 64 short driver feasibility finished
```

### 9.4 Driver Projection Alignment

Script:

```text
baseline_tests/run_step27_driver_projection_alignment.py
```

Outputs:

```text
outputs/step27_driver_projection_alignment/driver_projection_alignment.csv
outputs/step27_driver_projection_alignment/driver_projection_alignment.json
logs/step27_driver_projection_alignment.log
```

Checks:

```text
row_count == 6
pass_count == 6
abs(projected_mass_delta) <= 5e-5
abs(active_cell_count_delta) <= 32
alignment_pass == true
```

Log marker:

```text
[OK] Step 27 driver projection alignment finished
```

### 9.5 Driver 64 Summary

Script:

```text
baseline_tests/run_step27_64_driver_summary.py
```

Outputs:

```text
outputs/step27_64_driver_summary/driver_64_summary.csv
outputs/step27_64_driver_summary/driver_64_summary.json
logs/step27_64_driver_summary.log
```

Checks:

```text
driver_row_count == 6
stable_count == 6
mesh_row_count == 3
voxel_row_count == 3
penalty_row_count == 2
moving_boundary_row_count == 4
link_area_row_count == 2
quality_report_count == 6
quality_pass_count == 6
min_rho_min_global > 0.95
max_rho_max_global < 1.05
max_lbm_max_v_global < 0.1
min_mpm_min_J_global > 0
max_mpm_max_speed_global < 10
min_projected_mass > 0
min_active_cell_count > 0
max_driver_total_time finite
```

Log marker:

```text
[OK] Step 27 64 driver summary finished
```

### 9.6 Quality Report Aggregation

Script:

```text
baseline_tests/run_step27_quality_report_aggregation.py
```

Outputs:

```text
outputs/step27_quality_report_aggregation/quality_report_summary.csv
outputs/step27_quality_report_aggregation/quality_report_summary.json
logs/step27_quality_report_aggregation.log
```

Checks:

```text
quality_report_count == 6
strict_count == 6
pass_count == 6
error_count == 0
warning_count == 0
mesh_row_count == 3
voxel_row_count == 3
quality_report_total_size_bytes > 0
quality_report_max_size_bytes < 100000
```

Log marker:

```text
[OK] Step 27 quality report aggregation finished
```

### 9.7 Step 26 Regression Guard

Script:

```text
baseline_tests/run_step27_step26_regression_guard.py
```

Outputs:

```text
outputs/step27_step26_regression_guard/step26_regression_guard.csv
outputs/step27_step26_regression_guard/step26_regression_guard.json
logs/step27_step26_regression_guard.log
```

Checks:

```text
STEP26 report exists
Step 26 projection row_count == 6
Step 26 projection pass_count == 6
Step 26 short driver row_count == 8
Step 26 stable_count == 8
Step 26 quality_report_count == 8
Step 26 quality pass_count == 8
Step 26 artifact large_file_count == 0
Step 26 raw_candidate_large_file_count == 0
Step 26 scan_data_file_count == 0
Step 26 private_absolute_path_count == 0
```

Log marker:

```text
[OK] Step 27 Step 26 regression guard finished
```

### 9.8 Artifact Manifest

Script:

```text
baseline_tests/run_step27_artifact_manifest.py
```

Outputs:

```text
outputs/step27_artifact_manifest/artifact_manifest.csv
outputs/step27_artifact_manifest/artifact_summary.csv
outputs/step27_artifact_manifest/artifact_summary.json
logs/step27_artifact_manifest.log
```

Budget:

```text
large_file_count == 0
raw_candidate_large_file_count == 0
scan_data_file_count == 0
private_absolute_path_count == 0
step27_total_size_mb < 15
repo total_size_mb < 155
step27_vtr_count == 0
step27_particle_npy_count == 0
step27_quality_report_count == 6
```

Log marker:

```text
[OK] Step 27 artifact manifest finished
```

## 10. Contract Test Requirements

Create:

```text
tests/test_step27_controlled_real_geometry_64_short_driver_contract.py
```

Required tests:

```text
test_step27_required_artifacts_exist
test_step27_driver_configs_are_valid
test_step27_candidate_fingerprint_guard_is_valid
test_step27_mesh_64_driver_outputs_are_valid
test_step27_voxel_64_driver_outputs_are_valid
test_step27_driver_projection_alignment_is_valid
test_step27_64_driver_summary_is_valid
test_step27_quality_report_aggregation_is_valid
test_step27_step26_regression_guard_is_valid
test_step27_default_modes_remain_unchanged
test_step27_docs_scope_and_forbidden_claims_are_valid
test_step27_artifact_budget_is_valid
test_step27_report_acceptance_complete
```

The contract test must verify:

- every required Step 27 source/config/doc/baseline file exists;
- every required Step 27 output exists after baselines run;
- generated Step 27 driver configs use `64^3`, strict quality gates, no VTK, and no particle output;
- candidate fingerprint guard matches Step 25 accepted manifest;
- Step 26 geometry configs remain valid through `GeometryConfig`;
- mesh and voxel `64^3` short driver rows pass;
- all short driver rows are stable;
- all driver rows write strict quality reports;
- driver/projection alignment passes against Step 26 `64^3` projection-only rows;
- Step 26 regression guard passes;
- defaults remain disabled in `src/geometry_config.py` and `src/fsi_config.py`;
- docs and report include required scope language;
- docs and report do not include forbidden claims;
- artifact budget passes;
- `logs/step27_pytest.log` exists;
- all expected Step 27 logs contain success markers;
- `external/taichi_LBM3D` is unchanged.

Make the test compatible with both the Taichi env and the ECC pre-push hook environment. Avoid importing `src` package-level `__init__` in the contract test if that would require optional packages missing in the hook environment.

## 11. Required Report

Create:

```text
STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md
```

Required sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. Candidate Fingerprint Guard
## 5. 64^3 Mesh Short Driver Feasibility
## 6. 64^3 Voxel Short Driver Feasibility
## 7. Driver Projection Alignment
## 8. 64^3 Driver Summary
## 9. Quality Report Aggregation
## 10. Step 26 Regression Guard
## 11. Artifact Manifest Summary
## 12. Verification Commands
## 13. GitHub Sync Information
## 14. Acceptance Checklist
## 15. Decision For Step 28
```

The report must include:

- exact commands;
- exact artifact paths;
- exact row counts;
- exact summary values;
- artifact budget numbers;
- target remote branch;
- final commit hash in the completion message after push.

## 12. Verification Command Order

Run in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step27_common.py baseline_tests\run_step27_candidate_fingerprint_guard.py baseline_tests\run_step27_64_driver_mesh_feasibility.py baseline_tests\run_step27_64_driver_voxel_feasibility.py baseline_tests\run_step27_driver_projection_alignment.py baseline_tests\run_step27_64_driver_summary.py baseline_tests\run_step27_quality_report_aggregation.py baseline_tests\run_step27_step26_regression_guard.py baseline_tests\run_step27_artifact_manifest.py tests\test_step27_controlled_real_geometry_64_short_driver_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_mesh_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_voxel_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_driver_projection_alignment.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_step26_regression_guard.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step27_controlled_real_geometry_64_short_driver_contract.py -q

pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Also write full pytest output to:

```text
logs/step27_pytest.log
```

If any baseline fails, stop and diagnose the failed artifact. Do not weaken thresholds, remove no-claim checks, or add solver shortcuts to force a pass.

## 13. Commit And Push Requirements

After Step 27 implementation is accepted locally:

1. Review `git diff`.
2. Confirm `external/taichi_LBM3D` is unchanged.
3. Confirm raw large candidate geometry and scan data are not staged.
4. Commit all relevant Step 27 code, configs, docs, logs, outputs, tests, goal, and report.
5. Use this conventional commit message:

```text
test: add step27 controlled real geometry 64 short driver feasibility
```

6. Push to `origin/main` unless the user explicitly says not to push.
7. Report the final commit hash and remote branch in the completion message.

Do not add local raw real geometry, scan data, private absolute-path manifests, `.vtr`, or particle `.npy` outputs.

## 14. Acceptance Checklist

The final Step 27 report must include this checklist with every accepted item checked:

```text
- [ ] candidate fingerprint guard passes
- [ ] Step 25 manifest fingerprints match current candidate files
- [ ] Step 26 generated GeometryConfig files remain valid
- [ ] mesh 64^3 penalty short driver passes
- [ ] mesh 64^3 moving_boundary engineering short driver passes
- [ ] mesh 64^3 moving_boundary link_area short driver passes
- [ ] voxel 64^3 penalty short driver passes
- [ ] voxel 64^3 moving_boundary engineering short driver passes
- [ ] voxel 64^3 moving_boundary link_area short driver passes
- [ ] every Step 27 driver row writes geometry_quality_report.json
- [ ] every Step 27 quality gate is strict
- [ ] every Step 27 quality report passes
- [ ] quality warning count == 0
- [ ] quality error count == 0
- [ ] all driver rows have completed_lbm_steps >= 5
- [ ] all driver rows have total_mpm_substeps >= 25
- [ ] rho_min > 0.95
- [ ] rho_max < 1.05
- [ ] lbm_max_v < 0.1
- [ ] mpm_min_J > 0
- [ ] mpm_max_speed < 10
- [ ] projected_mass > 0
- [ ] active_cell_count > 0
- [ ] no NaN
- [ ] no Inf
- [ ] penalty rows have positive cell_force_max_norm
- [ ] moving_boundary rows keep cell_force_max_norm == 0
- [ ] moving_boundary rows have bb_link_count > 0
- [ ] moving_boundary rows have active_reaction_particle_count_max > 0
- [ ] link_area rows have finite bounded area_scale
- [ ] driver/projection alignment passes against Step 26 64^3 projection-only rows
- [ ] Step 26 regression guard passes
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
- [ ] no Step 27 .vtr outputs
- [ ] no Step 27 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 27 output total size budget passes
- [ ] repo artifact_summary total_size_mb < 155
- [ ] logs/step27_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 27 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 27 artifacts are pushed to origin/main
```

## 15. Decision For Step 28

If Step 27 passes, Step 28 should not jump directly to swimming. A conservative Step 28 direction is:

```text
Step 28 Controlled Real Geometry 64^3 Engineering Vs Link-Area Comparison And Stability Envelope
```

Step 28 should compare engineering and link-area transfer at `64^3`, add force/reaction diagnostics, summarize the area-scale envelope, and continue to avoid actuation, swimming, production sharp-interface FSI claims, final readiness claims, production mesh repair, automatic remeshing, and solver formula changes.
