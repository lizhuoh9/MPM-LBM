# Step 26 Goal: Controlled Real Geometry Projection-Only And Short Driver Feasibility

This file is the authoritative execution contract for Step 26 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 26 starts only when a goal explicitly references this file.

## 1. Status Before Step 26

Step 25 is accepted on GitHub at commit:

```text
2849548afb7dca1c236c64446b3dc50a2202164f
```

Step 25 established controlled real geometry candidate intake, not real squid validation. The accepted evidence includes:

- `STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md`;
- two candidate descriptors: `real_candidate_smoke_mesh` and `real_candidate_smoke_voxel`;
- candidate manifest row count 2;
- strict candidate descriptors with `validation_scope = intake_qa_normalization_sampling_projection_only`;
- mesh QA: 8 vertices, 12 faces, 0 degenerate faces, 0 boundary edges, 0 nonmanifold edges;
- voxel QA: 3016 occupied voxels, 1 connected component, largest component fraction 1.0;
- report-only normalization with source files unchanged;
- deterministic sampling reproducibility with repeatable position, `vol0`, and mass hashes;
- projection-only smoke with positive projected mass, positive active cells, no NaN, and no Inf;
- `pytest -q`: 197 passed;
- artifact summary with `large_file_count = 0`, `raw_candidate_large_file_count = 0`, `scan_data_file_count = 0`, Step 25 total size under budget, no Step 25 `.vtr`, and no Step 25 particle `.npy`;
- `external/taichi_LBM3D` unchanged.

Step 25 explicitly did not implement squid swimming, squid actuation, new FSI physics, production sharp-interface FSI validation, production mesh repair, automatic remeshing, two-phase flow, contact angle physics, sparse storage, or solver readiness claims.

Step 26 must preserve all Step 25 boundaries and evidence.

## 2. Step 26 Objective

Build controlled real geometry projection-only scale diagnostics and very short driver feasibility checks starting from Step 25 candidate intake artifacts.

Correct description:

```text
Step 26 is controlled real geometry projection-only and short driver feasibility.
```

Step 26 moves the project from:

```text
candidate intake, strict QA, normalization, sampling reproducibility, and 32^3 projection-only smoke
```

to:

```text
candidate fingerprint-guarded driver-ready geometry configs, 32^3/48^3/64^3 projection-only scale diagnostics, Step 25 projection regression, and 48^3 very short driver feasibility rows
```

Step 26 must prove:

1. Step 25 candidate descriptor fingerprints still match the accepted Step 25 manifest.
2. Step 25 candidate descriptors can be converted into driver-ready `GeometryConfig` JSON.
3. Candidate projection-only diagnostics pass at 32^3, 48^3, and 64^3.
4. Step 26 32^3 projection-only diagnostics regress cleanly against Step 25 projection smoke.
5. 48^3 very short `FSIDriver3D` feasibility passes for both smoke candidates across `none`, `penalty`, `moving_boundary` engineering, and `moving_boundary` link-area transfer rows.
6. Every Step 26 driver row enables strict quality checks and writes `geometry_quality_report.json`.
7. Driver rows are feasibility checks only and are not real squid validation.
8. Solver, coupler, LBM, MPM, moving-boundary, and projection formulas remain unchanged.
9. Artifact budgets remain controlled.
10. Raw large real geometry files and scan data are not committed.

## 3. Hard Boundaries

Do not implement:

- squid actuation;
- squid swimming;
- real squid validation claim;
- production sharp-interface FSI claim;
- final readiness claim;
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

- descriptor-to-driver `GeometryConfig` conversion;
- candidate fingerprint guard against Step 25 manifest;
- projection-only scale diagnostics;
- very short `FSIDriver3D` feasibility rows;
- strict quality-gated driver reports;
- Step 25 projection regression comparison;
- Step 24/25 regression guards;
- docs, report, contract test, logs, small outputs;
- artifact budget checks;
- commit and push of relevant Step 26 code, docs, logs, and output artifacts.

Any change that touches core solver formulas is out of scope and must be rejected.

## 4. Required Files

Create:

```text
STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_GOAL.md
STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md

src/geometry_driver_config.py
src/real_geometry_feasibility.py

configs/step26_real_candidate_smoke_mesh_geometry.json
configs/step26_real_candidate_smoke_voxel_geometry.json

configs/step26_projection_real_candidate_smoke_mesh_32.json
configs/step26_projection_real_candidate_smoke_mesh_48.json
configs/step26_projection_real_candidate_smoke_mesh_64.json
configs/step26_projection_real_candidate_smoke_voxel_32.json
configs/step26_projection_real_candidate_smoke_voxel_48.json
configs/step26_projection_real_candidate_smoke_voxel_64.json

configs/step26_driver_real_candidate_smoke_mesh_48_none.json
configs/step26_driver_real_candidate_smoke_mesh_48_penalty.json
configs/step26_driver_real_candidate_smoke_mesh_48_moving_boundary.json
configs/step26_driver_real_candidate_smoke_mesh_48_link_area.json
configs/step26_driver_real_candidate_smoke_voxel_48_none.json
configs/step26_driver_real_candidate_smoke_voxel_48_penalty.json
configs/step26_driver_real_candidate_smoke_voxel_48_moving_boundary.json
configs/step26_driver_real_candidate_smoke_voxel_48_link_area.json

baseline_tests/step26_common.py
baseline_tests/run_step26_candidate_fingerprint_guard.py
baseline_tests/run_step26_generate_driver_geometry_configs.py
baseline_tests/run_step26_projection_scale_diagnostics.py
baseline_tests/run_step26_step25_projection_regression.py
baseline_tests/run_step26_short_driver_mesh_48_modes.py
baseline_tests/run_step26_short_driver_voxel_48_modes.py
baseline_tests/run_step26_short_driver_summary.py
baseline_tests/run_step26_quality_report_aggregation.py
baseline_tests/run_step26_step25_regression_guard.py
baseline_tests/run_step26_artifact_manifest.py

docs/26_controlled_real_geometry_short_feasibility.md
tests/test_step26_controlled_real_geometry_short_feasibility_contract.py
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
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Required Scope Language

These exact phrases must appear across docs and the Step 26 report:

```text
Step 26 is controlled real geometry projection-only and short driver feasibility.
Step 26 is not real squid validation.
Step 26 does not implement squid actuation.
Step 26 does not implement squid swimming.
Step 26 does not implement new FSI physics.
Step 26 does not validate production sharp-interface FSI.
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

## 6. Source Module Contracts

### `src/geometry_driver_config.py`

Implement:

```python
def geometry_config_payload_from_candidate_descriptor(descriptor: dict) -> dict:
    ...

def write_geometry_config_from_descriptor(descriptor_path: str, out_config_path: str) -> dict:
    ...

def driver_config_payload_for_candidate(
    geometry_config_path: str,
    coupling_mode: str,
    reaction_transfer_mode: str,
    n_grid: int,
    n_lbm_steps: int,
    mpm_substeps_per_lbm_step: int,
) -> dict:
    ...
```

Requirements:

- Validate Step 25 descriptor using existing descriptor validation.
- Enforce `validation_scope = intake_qa_normalization_sampling_projection_only`.
- Enforce `quality_check_enabled = true`.
- Enforce `quality_check_strict = true`.
- Enforce `artifact_policy = no_vtk_no_particles_no_large_raw_geometry`.
- Generated geometry configs must be loadable by `GeometryConfig.from_json`.
- Generated driver configs must disable VTK and particle outputs.
- Generated driver configs must keep `quality_check_enabled = true` and `quality_check_strict = true`.

### `src/real_geometry_feasibility.py`

Implement:

```python
def run_projection_only_scale_case(geometry_config_path, n_grid, out_dir) -> dict:
    ...

def run_short_driver_case(driver_config_path, out_dir) -> dict:
    ...

def summarize_short_driver_diagnostics(config, diagnostics, driver, quality_report_path) -> dict:
    ...

def compare_step25_projection_smoke(step25_csv, step26_csv) -> dict:
    ...
```

Requirements:

- Projection-only scale diagnostics must not run the FSI driver.
- Driver feasibility rows must be very short (`n_lbm_steps = 5`, `mpm_substeps_per_lbm_step = 5`).
- Driver rows must write and validate strict `geometry_quality_report.json`.
- Summaries must record stability and mode-specific checks.
- Do not weaken thresholds or add solver shortcuts to pass.

## 7. Projection-Only Scale Diagnostics

Candidates:

```text
real_candidate_smoke_mesh
real_candidate_smoke_voxel
```

Grids:

```text
32^3
48^3
64^3
```

Rows:

```text
2 candidates × 3 grids = 6 rows
```

Acceptance:

```text
row_count == 6
projected_mass > 0
active_cell_count > 0
solid_phi_min >= 0
solid_phi_max <= 1
projected_volume_raw finite
projected_volume_clamped finite
max_phi_raw finite
has_nan == false
has_inf == false
projection_pass == true
```

32^3 rows must regress against Step 25 projection smoke:

```text
compared_row_count == 2
abs(projected_mass_delta) <= 1e-6
active_cell_count_delta == 0
solid_phi_min_delta == 0
solid_phi_max_delta == 0
projection_pass_both == true
```

48^3 and 64^3 rows are new scale diagnostics and do not need Step 25 overlap.

## 8. 48^3 Short Driver Feasibility Matrix

Candidates:

```text
real_candidate_smoke_mesh
real_candidate_smoke_voxel
```

Mode/transfer rows:

```text
none / engineering
penalty / engineering
moving_boundary / engineering
moving_boundary / link_area_experimental
```

Rows:

```text
2 candidates × 4 rows = 8 driver rows
```

Required parameters:

```text
n_grid = 48
n_particles = 4096
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
output_interval = 5
```

General acceptance:

```text
completed_lbm_steps >= 5
total_mpm_substeps >= 25
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
projected_mass > 0
active_cell_count > 0
no NaN
no Inf
stable == true
```

Mode-specific acceptance:

```text
none:
  cell_force_max_norm == 0
  hydro_force_max_norm == 0 or finite
  bb_link_count == 0

penalty:
  cell_force_max_norm > 0
  hydro_force_max_norm > 0
  bb_link_count == 0

moving_boundary engineering:
  cell_force_max_norm == 0
  bb_link_count > 0
  active_reaction_particle_count > 0
  hydro_force_max_norm > 0

moving_boundary link_area_experimental:
  cell_force_max_norm == 0
  bb_link_count > 0
  active_reaction_particle_count > 0
  area_scale_final finite
  0.25 <= area_scale_final <= 2.0
```

Step 26 must not include 64^3 driver feasibility in the required matrix. Keep 64^3 to projection-only scale diagnostics.

## 9. Baseline Runner Contracts

### 9.1 Candidate Fingerprint Guard

Script:

```text
baseline_tests/run_step26_candidate_fingerprint_guard.py
```

Outputs:

```text
outputs/step26_candidate_fingerprint_guard/fingerprint_guard.csv
outputs/step26_candidate_fingerprint_guard/fingerprint_guard.json
logs/step26_candidate_fingerprint_guard.log
```

Checks:

```text
row_count == 2
candidate_id matches Step 25 manifest
source_file is repo-relative or redacted
sha256 matches Step 25 manifest
size_bytes matches Step 25 manifest
validation_scope unchanged
quality_check_enabled == true
quality_check_strict == true
no private absolute path
```

Log marker:

```text
[OK] Step 26 candidate fingerprint guard finished
```

### 9.2 Generate Driver Geometry Configs

Script:

```text
baseline_tests/run_step26_generate_driver_geometry_configs.py
```

Outputs:

```text
configs/step26_real_candidate_smoke_mesh_geometry.json
configs/step26_real_candidate_smoke_voxel_geometry.json
outputs/step26_generated_geometry_configs/generated_geometry_configs.csv
outputs/step26_generated_geometry_configs/generated_geometry_configs.json
logs/step26_generate_driver_geometry_configs.log
```

Checks:

```text
both configs exist
GeometryConfig.from_json succeeds
geometry_type in {mesh, voxel}
n_particles == 4096
quality_check_enabled == true
quality_check_strict == true
source file exists
source fingerprint still matches Step 25 manifest
```

Log marker:

```text
[OK] Step 26 generated driver geometry configs finished
```

### 9.3 Projection Scale Diagnostics

Script:

```text
baseline_tests/run_step26_projection_scale_diagnostics.py
```

Outputs:

```text
outputs/step26_projection_scale_diagnostics/projection_scale_results.csv
outputs/step26_projection_scale_diagnostics/projection_scale_results.json
logs/step26_projection_scale_diagnostics.log
```

Checks:

```text
row_count == 6
all rows projection_pass == true
no NaN
no Inf
no FSI driver long-run claim
```

Log marker:

```text
[OK] Step 26 projection scale diagnostics finished
```

### 9.4 Step 25 Projection Regression

Script:

```text
baseline_tests/run_step26_step25_projection_regression.py
```

Outputs:

```text
outputs/step26_step25_projection_regression/step25_projection_regression.csv
outputs/step26_step25_projection_regression/step25_projection_regression.json
logs/step26_step25_projection_regression.log
```

Checks:

```text
compared_row_count == 2
abs(projected_mass_delta) <= 1e-6
active_cell_count_delta == 0
solid_phi_min_delta == 0
solid_phi_max_delta == 0
projection_pass_both == true
```

Log marker:

```text
[OK] Step 26 Step 25 projection regression finished
```

### 9.5 Short Driver Mesh 48 Modes

Script:

```text
baseline_tests/run_step26_short_driver_mesh_48_modes.py
```

Outputs:

```text
outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.csv
outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.npz
outputs/step26_short_driver_mesh_48_modes/<case>/geometry_quality_report.json
logs/step26_short_driver_mesh_48_modes.log
```

Rows:

```text
real_candidate_smoke_mesh none
real_candidate_smoke_mesh penalty
real_candidate_smoke_mesh moving_boundary engineering
real_candidate_smoke_mesh moving_boundary link_area_experimental
```

Log marker:

```text
[OK] Step 26 mesh 48 short driver modes finished
```

### 9.6 Short Driver Voxel 48 Modes

Script:

```text
baseline_tests/run_step26_short_driver_voxel_48_modes.py
```

Outputs:

```text
outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.csv
outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.npz
outputs/step26_short_driver_voxel_48_modes/<case>/geometry_quality_report.json
logs/step26_short_driver_voxel_48_modes.log
```

Rows:

```text
real_candidate_smoke_voxel none
real_candidate_smoke_voxel penalty
real_candidate_smoke_voxel moving_boundary engineering
real_candidate_smoke_voxel moving_boundary link_area_experimental
```

Log marker:

```text
[OK] Step 26 voxel 48 short driver modes finished
```

### 9.7 Short Driver Summary

Script:

```text
baseline_tests/run_step26_short_driver_summary.py
```

Outputs:

```text
outputs/step26_short_driver_summary/short_driver_summary.csv
outputs/step26_short_driver_summary/short_driver_summary.json
logs/step26_short_driver_summary.log
```

Checks:

```text
driver_row_count == 8
stable_count == 8
quality_report_count == 8
quality_pass_count == 8
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
max_step26_driver_total_time finite
```

Log marker:

```text
[OK] Step 26 short driver summary finished
```

### 9.8 Quality Report Aggregation

Script:

```text
baseline_tests/run_step26_quality_report_aggregation.py
```

Outputs:

```text
outputs/step26_quality_report_aggregation/quality_report_summary.csv
outputs/step26_quality_report_aggregation/quality_report_summary.json
logs/step26_quality_report_aggregation.log
```

Checks:

```text
quality_report_count == 8
pass_count == 8
error_count == 0
warning_count == 0
strict_count == 8
mesh_row_count == 4
voxel_row_count == 4
```

Log marker:

```text
[OK] Step 26 quality report aggregation finished
```

### 9.9 Step 25 Regression Guard

Script:

```text
baseline_tests/run_step26_step25_regression_guard.py
```

Outputs:

```text
outputs/step26_step25_regression_guard/step25_regression_guard.csv
outputs/step26_step25_regression_guard/step25_regression_guard.json
logs/step26_step25_regression_guard.log
```

Checks:

```text
STEP25 report exists
Step 25 candidate manifest row_count == 2
Step 25 sampling reproducibility pass == true for 2 rows
Step 25 projection smoke pass == true for 2 rows
Step 25 artifact large_file_count == 0
Step 25 scan_data_file_count == 0
Step 25 raw_candidate_large_file_count == 0
```

Log marker:

```text
[OK] Step 26 Step 25 regression guard finished
```

### 9.10 Artifact Manifest

Script:

```text
baseline_tests/run_step26_artifact_manifest.py
```

Outputs:

```text
outputs/step26_artifact_manifest/artifact_manifest.csv
outputs/step26_artifact_manifest/artifact_summary.csv
outputs/step26_artifact_manifest/artifact_summary.json
logs/step26_artifact_manifest.log
```

Budget:

```text
large_file_count == 0
raw_candidate_large_file_count == 0
scan_data_file_count == 0
step26_total_size_mb < 8
repo total_size_mb < 170
step26_vtr_count == 0
step26_particle_npy_count == 0
step26_quality_report_count == 8
no private absolute paths in committed outputs
```

Log marker:

```text
[OK] Step 26 artifact manifest finished
```

## 10. Contract Test Requirements

Create:

```text
tests/test_step26_controlled_real_geometry_short_feasibility_contract.py
```

Required tests:

```text
test_step26_required_artifacts_exist
test_step26_candidate_fingerprint_guard_is_valid
test_step26_generated_geometry_configs_are_valid
test_step26_projection_scale_diagnostics_are_valid
test_step26_step25_projection_regression_is_valid
test_step26_mesh_short_driver_outputs_are_valid
test_step26_voxel_short_driver_outputs_are_valid
test_step26_short_driver_summary_is_valid
test_step26_quality_report_aggregation_is_valid
test_step26_step25_regression_guard_is_valid
test_step26_default_modes_remain_unchanged
test_step26_docs_scope_and_forbidden_claims_are_valid
test_step26_artifact_budget_is_valid
test_step26_report_acceptance_complete
```

The contract test must verify:

- every required Step 26 source/config/doc/baseline file exists;
- every required Step 26 output exists after baselines run;
- candidate fingerprint guard matches Step 25 accepted manifest;
- generated geometry configs load through `GeometryConfig.from_json`;
- projection-only scale diagnostics pass at 32^3, 48^3, and 64^3;
- Step 25 projection regression passes for 32^3 rows;
- mesh and voxel 48^3 short driver rows all pass;
- all short driver rows are stable;
- all driver rows write strict quality reports;
- mode-specific force and bounce-back expectations pass;
- defaults remain disabled in `src/geometry_config.py` and `src/fsi_config.py`;
- docs and report include required scope language;
- docs and report do not include forbidden claims;
- artifact budget passes;
- `logs/step26_pytest.log` exists;
- all expected Step 26 logs contain success markers;
- `external/taichi_LBM3D` is unchanged.

## 11. Required Report

Create:

```text
STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md
```

Required sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. Candidate Fingerprint Guard
## 5. Generated Driver Geometry Configs
## 6. Projection-Only Scale Diagnostics
## 7. Step 25 Projection Regression
## 8. 48^3 Mesh Short Driver Feasibility
## 9. 48^3 Voxel Short Driver Feasibility
## 10. Short Driver Summary
## 11. Quality Report Aggregation
## 12. Step 25 Regression Guard
## 13. Artifact Manifest Summary
## 14. Verification Commands
## 15. GitHub Sync Information
## 16. Acceptance Checklist
## 17. Decision For Step 27
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
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_driver_config.py src\real_geometry_feasibility.py baseline_tests\step26_common.py baseline_tests\run_step26_candidate_fingerprint_guard.py baseline_tests\run_step26_generate_driver_geometry_configs.py baseline_tests\run_step26_projection_scale_diagnostics.py baseline_tests\run_step26_step25_projection_regression.py baseline_tests\run_step26_short_driver_mesh_48_modes.py baseline_tests\run_step26_short_driver_voxel_48_modes.py baseline_tests\run_step26_short_driver_summary.py baseline_tests\run_step26_quality_report_aggregation.py baseline_tests\run_step26_step25_regression_guard.py baseline_tests\run_step26_artifact_manifest.py tests\test_step26_controlled_real_geometry_short_feasibility_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_generate_driver_geometry_configs.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_projection_scale_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_projection_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_mesh_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_voxel_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_regression_guard.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step26_controlled_real_geometry_short_feasibility_contract.py -q

git diff --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Also write full pytest output to:

```text
logs/step26_pytest.log
```

If any baseline fails, stop and diagnose the failed artifact. Do not weaken thresholds, remove no-claim checks, or add solver shortcuts to force a pass.

## 13. Commit And Push Requirements

After Step 26 implementation is accepted locally:

1. Review `git diff`.
2. Confirm `external/taichi_LBM3D` is unchanged.
3. Confirm raw large candidate geometry and scan data are not staged.
4. Commit all relevant Step 26 code, configs, docs, logs, outputs, tests, goal, and report.
5. Use this conventional commit message:

```text
test: add step26 controlled real geometry short feasibility
```

6. Push to `origin/main` unless the user explicitly says not to push.
7. Report the final commit hash and remote branch in the completion message.

Do not add local raw real geometry, scan data, private absolute-path manifests, `.vtr`, or particle `.npy` outputs.

## 14. Acceptance Checklist

The final Step 26 report must include this checklist with every accepted item checked:

```text
- [ ] candidate fingerprint guard passes
- [ ] Step 25 manifest fingerprints match current candidate files
- [ ] generated driver GeometryConfig files are valid
- [ ] generated driver configs preserve strict quality gate
- [ ] projection-only scale diagnostics pass for 32^3 rows
- [ ] projection-only scale diagnostics pass for 48^3 rows
- [ ] projection-only scale diagnostics pass for 64^3 rows
- [ ] Step 25 projection regression passes for 32^3 rows
- [ ] mesh 48^3 none short driver passes
- [ ] mesh 48^3 penalty short driver passes
- [ ] mesh 48^3 moving_boundary engineering short driver passes
- [ ] mesh 48^3 moving_boundary link_area short driver passes
- [ ] voxel 48^3 none short driver passes
- [ ] voxel 48^3 penalty short driver passes
- [ ] voxel 48^3 moving_boundary engineering short driver passes
- [ ] voxel 48^3 moving_boundary link_area short driver passes
- [ ] every Step 26 driver row writes geometry_quality_report.json
- [ ] every Step 26 quality gate is strict
- [ ] every Step 26 quality report passes
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
- [ ] link_area rows have finite bounded area_scale
- [ ] Step 25 regression guard passes
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
- [ ] no Step 26 .vtr outputs
- [ ] no Step 26 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 26 output total size budget passes
- [ ] repo artifact_summary total_size_mb < 170
- [ ] logs/step26_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 26 contract test passes
- [ ] git diff --check passes
- [ ] pre-push hook passes
- [ ] Step 26 artifacts are pushed to origin/main
```

## 15. Decision For Step 27

If Step 26 passes, Step 27 should be:

```text
Step 27 Controlled Real Geometry 64^3 Short Driver Feasibility
```

Step 27 should carry only a conservative 64^3 short driver subset forward. It must still avoid actuation, swimming, production sharp-interface FSI claims, final readiness claims, production mesh repair, automatic remeshing, and solver formula changes.
