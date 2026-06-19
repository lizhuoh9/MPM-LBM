# Step 23 Goal: Quality-Gated Imported Geometry Scale Validation

This file is the authoritative execution contract for Step 23 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 23 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 23

Step 22 is accepted on GitHub at commit:

```text
fbd962700bb7d1df3faeaf99491f600e600606cc
```

Step 22 established:

- mesh quality diagnostics in `src/mesh_quality.py`;
- voxel quality diagnostics in `src/voxel_quality.py`;
- imported geometry quality aggregation in `src/geometry_quality.py`;
- `GeometryQualityGate` with non-strict diagnostic mode and strict expected-failure mode;
- `quality_check_enabled`, `quality_check_strict`, and `quality_report_path` fields in `GeometryConfig` and `FSIDriverConfig`;
- optional `FSIDriver3D` `geometry_quality_report.json` output when quality checks are enabled;
- strict expected-failure fixtures for non-watertight mesh, degenerate mesh, and empty voxel occupancy;
- sampling and resolution sensitivity diagnostics;
- Step 22 driver quality gate smoke baselines;
- Step 22 artifact manifest with `large_file_count == 0`;
- `pytest -q`: 164 passed;
- Git pre-push hook: 164 passed;
- `external/taichi_LBM3D` unchanged.

Step 22 documents that:

- Step 22 is a geometry QA and import robustness layer, not real squid validation;
- imported geometry remains limited to small synthetic voxel and mesh fixtures;
- the Step 22 mesh path is not production mesh repair or automatic remeshing;
- default `reaction_transfer_mode` remains `engineering`;
- `link_area_experimental` remains opt-in;
- the moving bounce-back formula is unchanged;
- `PenaltyFSICoupler3D`, `MovingBoundaryFSICoupler3D`, and `LinkAreaMovingBoundaryCoupler3D` are unchanged.

Step 23 must preserve all of the above.

## 2. Step 23 Objective

Run imported geometry 48^3 and 64^3 scale validation with the Step 22 quality gate enabled.

Step 23 combines:

```text
Step 21 imported geometry scale validation
+
Step 22 geometry quality gate and quality report output
```

The correct description is:

```text
quality-gated synthetic imported geometry validation
```

Step 23 must prove that:

1. `quality_check_enabled = true` and `quality_check_strict = false` work across the existing imported geometry scale baselines.
2. Every Step 23 driver row writes a `geometry_quality_report.json`.
3. Every good synthetic imported geometry row passes the non-strict quality gate.
4. Step 23 48^3 and 64^3 scale rows remain stable.
5. Step 21 ungated results and Step 23 quality-gated results remain comparable.
6. Quality report generation does not alter solver formulas, FSI formulas, default driver behavior, or default config behavior.
7. Artifacts remain small and reproducible.

Step 23 does not make real squid validation claims and does not implement production mesh repair.

## 3. Hard Boundaries

Do not implement:

- new FSI physics;
- new coupling formulas;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to the moving bounce-back formula;
- changes to LBM step formulas;
- changes to the default `reaction_transfer_mode = "engineering"`;
- changes to the default `quality_check_enabled = false`;
- default strict quality gating for scale validation;
- real squid geometry validation;
- squid actuation;
- squid swimming;
- production mesh repair;
- automatic remeshing;
- mesh cleanup or mesh fixing;
- two-phase flow;
- contact angle physics;
- sparse storage;
- `ReducedSquidFSI`;
- large real mesh artifacts;
- large real voxel artifacts;
- scan data;
- edits to `external/taichi_LBM3D`.

Allowed work:

- quality-gated driver configs;
- `quality_check_enabled = true`;
- `quality_check_strict = false` for scale baselines;
- driver quality report aggregation;
- Step 21 vs Step 23 regression comparison;
- quality gate timing/overhead diagnostics if available from existing timing data;
- docs, tests, logs, outputs, and report;
- minimal helper refactors in baseline scripts only if they do not change solver behavior.

## 4. Required Source And Artifact Files

Create:

```text
configs/step23_quality_gated_voxel_sphere_48_none.json
configs/step23_quality_gated_voxel_sphere_48_penalty.json
configs/step23_quality_gated_voxel_sphere_48_moving_boundary.json
configs/step23_quality_gated_voxel_sphere_48_link_area.json

configs/step23_quality_gated_mesh_cube_48_none.json
configs/step23_quality_gated_mesh_cube_48_penalty.json
configs/step23_quality_gated_mesh_cube_48_moving_boundary.json
configs/step23_quality_gated_mesh_cube_48_link_area.json

configs/step23_quality_gated_mesh_ellipsoid_48_none.json
configs/step23_quality_gated_mesh_ellipsoid_48_penalty.json
configs/step23_quality_gated_mesh_ellipsoid_48_moving_boundary.json
configs/step23_quality_gated_mesh_ellipsoid_48_link_area.json

configs/step23_quality_gated_voxel_sphere_64_penalty.json
configs/step23_quality_gated_voxel_sphere_64_moving_boundary.json
configs/step23_quality_gated_mesh_cube_64_penalty.json

baseline_tests/step23_common.py
baseline_tests/run_step23_quality_gated_voxel_sphere_48_modes.py
baseline_tests/run_step23_quality_gated_mesh_cube_48_modes.py
baseline_tests/run_step23_quality_gated_mesh_ellipsoid_48_modes.py
baseline_tests/run_step23_quality_gated_imported_geometry_64_feasibility.py
baseline_tests/run_step23_quality_report_aggregation.py
baseline_tests/run_step23_step21_vs_quality_gated_comparison.py
baseline_tests/run_step23_artifact_manifest.py

docs/22_quality_gated_imported_geometry_validation.md
tests/test_step23_quality_gated_geometry_scale_contract.py
STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
docs/20_imported_geometry_scale_validation.md
docs/21_geometry_quality_checks.md
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Step 23 Config Rules

All Step 23 imported geometry driver configs must set:

```json
"quality_check_enabled": true,
"quality_check_strict": false,
"write_vtk": false,
"write_particles": false
```

The scale-validation quality gate must be non-strict because Step 22 already validates strict failure behavior with bad geometry fixtures. Step 23 validates good synthetic imported geometry under an enabled diagnostic gate.

Every Step 23 driver config must preserve the Step 21 baseline intent:

- 48^3 voxel_sphere modes;
- 48^3 mesh_cube modes;
- 48^3 mesh_ellipsoid modes;
- required 64^3 imported geometry feasibility rows.

Step 23 may derive configs from Step 21 configs, but the final committed configs must be explicit JSON artifacts.

## 6. Required Common Helper Contract

Implement in:

```text
baseline_tests/step23_common.py
```

Recommended helpers:

```python
def make_quality_gated_config(base_config_path, out_config_path):
    ...

def run_quality_gated_driver_case(config_path, out_dir):
    ...

def collect_quality_report(out_dir):
    ...

def write_quality_gated_rows(rows, csv_path, npz_path):
    ...

def assert_quality_gated_row_stable(row):
    ...
```

The helper must enforce:

```text
quality_check_enabled == true
quality_check_strict == false
write_vtk == false
write_particles == false
```

The helper must not weaken physics acceptance thresholds. It must treat missing `geometry_quality_report.json` as a failure.

## 7. Baseline 1: 48^3 Voxel_Sphere Quality-Gated Modes

Script:

```text
baseline_tests/run_step23_quality_gated_voxel_sphere_48_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_voxel_sphere_48_modes.py
```

Cases:

```text
voxel_sphere none
voxel_sphere penalty
voxel_sphere moving_boundary engineering
voxel_sphere moving_boundary link_area_experimental
```

Outputs:

```text
outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv
outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.npz
outputs/step23_quality_gated_voxel_sphere_48_modes/<case>/geometry_quality_report.json
logs/step23_quality_gated_voxel_sphere_48_modes.log
```

Acceptance:

```text
all four modes stable
all four rows have geometry_quality_report.json
quality pass == true
severity == ok or warning
n_grid == 48
completed_lbm_steps >= 10
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
projected_mass > 0
active_cell_count > 0
moving_boundary rows cell_force_max_norm == 0
penalty row cell_force_max_norm > 0
link_area row area_scale finite
```

Success log marker:

```text
[OK] Step 23 quality-gated voxel_sphere 48 modes finished
```

## 8. Baseline 2: 48^3 Mesh_Cube Quality-Gated Modes

Script:

```text
baseline_tests/run_step23_quality_gated_mesh_cube_48_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_cube_48_modes.py
```

Cases:

```text
mesh_cube none
mesh_cube penalty
mesh_cube moving_boundary engineering
mesh_cube moving_boundary link_area_experimental
```

Outputs:

```text
outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv
outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.npz
outputs/step23_quality_gated_mesh_cube_48_modes/<case>/geometry_quality_report.json
logs/step23_quality_gated_mesh_cube_48_modes.log
```

Acceptance:

```text
all four modes stable
quality report exists for every row
quality pass == true
severity == ok or warning
mesh reports have boundary_edge_count == 0
mesh reports have degenerate_face_count == 0
n_grid == 48
completed_lbm_steps >= 10
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
projected_mass > 0
active_cell_count > 0
```

Success log marker:

```text
[OK] Step 23 quality-gated mesh_cube 48 modes finished
```

## 9. Baseline 3: 48^3 Mesh_Ellipsoid Quality-Gated Modes

Script:

```text
baseline_tests/run_step23_quality_gated_mesh_ellipsoid_48_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_ellipsoid_48_modes.py
```

Cases:

```text
mesh_ellipsoid none
mesh_ellipsoid penalty
mesh_ellipsoid moving_boundary engineering
mesh_ellipsoid moving_boundary link_area_experimental
```

Outputs:

```text
outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv
outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.npz
outputs/step23_quality_gated_mesh_ellipsoid_48_modes/<case>/geometry_quality_report.json
logs/step23_quality_gated_mesh_ellipsoid_48_modes.log
```

Acceptance:

```text
all four modes stable
quality report exists for every row
quality pass == true
severity == ok or warning
mesh reports have boundary_edge_count == 0
mesh reports have degenerate_face_count == 0
n_grid == 48
completed_lbm_steps >= 10
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
projected_mass > 0
active_cell_count > 0
```

Success log marker:

```text
[OK] Step 23 quality-gated mesh_ellipsoid 48 modes finished
```

## 10. Baseline 4: 64^3 Quality-Gated Imported Geometry Feasibility

Script:

```text
baseline_tests/run_step23_quality_gated_imported_geometry_64_feasibility.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_imported_geometry_64_feasibility.py
```

Required cases:

```text
voxel_sphere penalty
voxel_sphere moving_boundary engineering
mesh_cube penalty
```

Optional cases may be added only if runtime remains reasonable:

```text
mesh_cube moving_boundary engineering
voxel_sphere moving_boundary link_area_experimental
```

Outputs:

```text
outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv
outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.npz
outputs/step23_quality_gated_imported_geometry_64_feasibility/<case>/geometry_quality_report.json
logs/step23_quality_gated_imported_geometry_64_feasibility.log
```

Acceptance:

```text
all required rows stable
quality report exists for every required row
quality pass == true
severity == ok or warning
n_grid == 64
completed_lbm_steps >= 5
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
projected_mass > 0
active_cell_count > 0
```

Success log marker:

```text
[OK] Step 23 quality-gated imported geometry 64 feasibility finished
```

## 11. Baseline 5: Quality Report Aggregation

Script:

```text
baseline_tests/run_step23_quality_report_aggregation.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_report_aggregation.py
```

Inputs:

```text
outputs/step23_quality_gated_voxel_sphere_48_modes/
outputs/step23_quality_gated_mesh_cube_48_modes/
outputs/step23_quality_gated_mesh_ellipsoid_48_modes/
outputs/step23_quality_gated_imported_geometry_64_feasibility/
```

Outputs:

```text
outputs/step23_quality_report_aggregation/quality_report_summary.csv
outputs/step23_quality_report_aggregation/quality_report_summary.json
logs/step23_quality_report_aggregation.log
```

Required fields:

```text
case
geometry_type
quality_kind
pass
severity
warnings_count
reasons_count
vertices_count
faces_count
boundary_edge_count
degenerate_face_count
occupied_count
connected_component_count
largest_component_fraction
source_report_path
```

Acceptance:

```text
quality report count >= required driver row count
all pass == true
no severity == error
mesh rows have boundary_edge_count == 0
mesh rows have degenerate_face_count == 0
voxel rows have occupied_count > 0
voxel rows have connected_component_count >= 1
all numeric fields finite where present
```

Success log marker:

```text
[OK] Step 23 quality report aggregation finished
```

## 12. Baseline 6: Step 21 Vs Quality-Gated Comparison

Script:

```text
baseline_tests/run_step23_step21_vs_quality_gated_comparison.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_step21_vs_quality_gated_comparison.py
```

Inputs:

```text
Step 21 result CSVs
Step 23 quality-gated result CSVs
```

Outputs:

```text
outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.csv
outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.json
logs/step23_step21_vs_quality_gated_comparison.log
```

Required comparison fields:

```text
case
mode
reaction_transfer_mode
n_grid
rho_min_delta
rho_max_delta
lbm_max_v_delta
mpm_min_J_delta
projected_mass_delta
active_cell_count_delta
stable_both
```

Acceptance:

```text
stable_both == true for required comparable rows
deltas finite
quality gate does not introduce failure
do not require bitwise identical values
do not require zero deltas
document max deltas in the report
```

Reasoning:

Quality report generation should not intentionally change solver state. However, Taichi reruns and scheduling can produce tiny numerical differences, so the comparison must check stable finite trends instead of bitwise identity.

Success log marker:

```text
[OK] Step 23 Step 21 vs quality-gated comparison finished
```

## 13. Baseline 7: Artifact Manifest

Script:

```text
baseline_tests/run_step23_artifact_manifest.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_artifact_manifest.py
```

Outputs:

```text
outputs/step23_artifact_manifest/artifact_manifest.csv
outputs/step23_artifact_manifest/artifact_summary.json
logs/step23_artifact_manifest.log
```

Acceptance:

```text
file_count recorded
total_size_bytes recorded
large_file_count == 0
quality reports are small
Step 23 driver configs have write_vtk == false
Step 23 driver configs have write_particles == false
no large real geometry artifacts
```

Success log marker:

```text
[OK] Step 23 artifact manifest finished
```

## 14. Required Documentation

Create:

```text
docs/22_quality_gated_imported_geometry_validation.md
STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
docs/20_imported_geometry_scale_validation.md
docs/21_geometry_quality_checks.md
```

Required phrases in docs/report:

```text
Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.
The default quality_check_enabled remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.
```

Forbidden claims:

```text
real squid simulation is validated
validated squid swimming
production mesh repair is complete
automatic remeshing is implemented
production-ready mesh import
production-ready sharp-interface FSI
strict momentum-conserving FSI is complete
implements two_phase
implements contact_angle
```

## 15. Step 23 Report Contract

`STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md` must contain:

```text
1. Goal
2. Files created and updated
3. Explicit non-goals
4. 48^3 voxel_sphere quality-gated modes
5. 48^3 mesh_cube quality-gated modes
6. 48^3 mesh_ellipsoid quality-gated modes
7. 64^3 quality-gated feasibility
8. Quality report aggregation
9. Step 21 vs Step 23 comparison
10. Artifact manifest summary
11. Verification commands
12. GitHub sync information
13. Acceptance checklist
14. Decision for Step 24
```

The report must include tables with at least:

```text
case
geometry_type
mode
reaction_transfer_mode
n_grid
quality_check_enabled
quality_check_strict
quality_pass
quality_severity
rho_min
rho_max
lbm_max_v
mpm_min_J
projected_mass
active_cell_count
stable
```

The comparison section must include:

```text
required_comparable_row_count
stable_both_count
max_abs_rho_min_delta
max_abs_rho_max_delta
max_abs_lbm_max_v_delta
max_abs_mpm_min_J_delta
max_abs_projected_mass_delta
max_abs_active_cell_count_delta
```

## 16. Required Contract Test

Create:

```text
tests/test_step23_quality_gated_geometry_scale_contract.py
```

The contract test must avoid importing heavy optional runtime paths unless it handles missing packages. Prefer file/text/artifact checks for Git pre-push compatibility.

Required file checks:

```python
required_paths = [
    "baseline_tests/step23_common.py",
    "baseline_tests/run_step23_quality_gated_voxel_sphere_48_modes.py",
    "baseline_tests/run_step23_quality_gated_mesh_cube_48_modes.py",
    "baseline_tests/run_step23_quality_gated_mesh_ellipsoid_48_modes.py",
    "baseline_tests/run_step23_quality_gated_imported_geometry_64_feasibility.py",
    "baseline_tests/run_step23_quality_report_aggregation.py",
    "baseline_tests/run_step23_step21_vs_quality_gated_comparison.py",
    "baseline_tests/run_step23_artifact_manifest.py",
    "docs/22_quality_gated_imported_geometry_validation.md",
    "STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md",
]
```

Required log markers:

```text
[OK] Step 23 quality-gated voxel_sphere 48 modes finished
[OK] Step 23 quality-gated mesh_cube 48 modes finished
[OK] Step 23 quality-gated mesh_ellipsoid 48 modes finished
[OK] Step 23 quality-gated imported geometry 64 feasibility finished
[OK] Step 23 quality report aggregation finished
[OK] Step 23 Step 21 vs quality-gated comparison finished
[OK] Step 23 artifact manifest finished
```

Required artifact checks:

- quality-gated 48^3 result CSVs exist and all required rows are stable;
- quality-gated 64^3 result CSV exists and all required rows are stable;
- every required driver row records `quality_check_enabled == true`;
- every required driver row records `quality_check_strict == false`;
- every required driver row records `quality_pass == true`;
- every required driver row has `geometry_quality_report.json`;
- quality report aggregation has at least the required driver row count;
- quality report aggregation has no `severity == error`;
- Step 21 vs Step 23 comparison has finite deltas and `stable_both == true`;
- artifact summary has `large_file_count == 0`;
- `logs/step23_pytest.log` exists;
- docs/report include required scope phrases and avoid forbidden claims.

## 17. Execution Order

Use this order:

1. Read this goal, current repo state, Step 21 scale scripts/results, Step 22 quality code/results, and existing tests.
2. Add `tests/test_step23_quality_gated_geometry_scale_contract.py` first and confirm RED.
3. Add Step 23 configs with `quality_check_enabled = true`, `quality_check_strict = false`, `write_vtk = false`, and `write_particles = false`.
4. Add `baseline_tests/step23_common.py`.
5. Add and run 48^3 voxel_sphere quality-gated modes.
6. Add and run 48^3 mesh_cube quality-gated modes.
7. Add and run 48^3 mesh_ellipsoid quality-gated modes.
8. Add and run 64^3 quality-gated imported geometry feasibility.
9. Add and run quality report aggregation.
10. Add and run Step 21 vs Step 23 comparison.
11. Write docs and Step 23 report.
12. Run full `pytest -q` and save `logs/step23_pytest.log`.
13. Run artifact manifest after pytest.
14. Re-run Step 23 contract test.
15. Run `git diff --check`.
16. Confirm `external/taichi_LBM3D` remains unchanged.
17. Commit and push all code, docs, logs, outputs, and report to GitHub `origin/main`.

## 18. Hard Acceptance Checklist

All items must be true before Step 23 is complete:

```text
[ ] main is at the Step 23 final commit
[ ] all Step 23 configs exist
[ ] every Step 23 scale config has quality_check_enabled == true
[ ] every Step 23 scale config has quality_check_strict == false
[ ] every Step 23 scale config has write_vtk == false
[ ] every Step 23 scale config has write_particles == false
[ ] default GeometryConfig quality_check_enabled remains false
[ ] default FSIDriverConfig quality_check_enabled remains false
[ ] quality-gated voxel_sphere 48^3 modes pass
[ ] quality-gated mesh_cube 48^3 modes pass
[ ] quality-gated mesh_ellipsoid 48^3 modes pass
[ ] quality-gated imported geometry 64^3 feasibility passes
[ ] every required driver row has geometry_quality_report.json
[ ] all required quality reports pass
[ ] no required quality report severity == error
[ ] Step 21 vs Step 23 comparison passes
[ ] quality report aggregation passes
[ ] rho_min > 0.95 for every required driver row
[ ] rho_max < 1.05 for every required driver row
[ ] lbm_max_v < 0.1 for every required driver row
[ ] mpm_min_J > 0 for every required driver row
[ ] projected_mass > 0 for every required driver row
[ ] active_cell_count > 0 for every required driver row
[ ] no NaN in required artifacts
[ ] no Inf in required artifacts
[ ] no FSI formula changes
[ ] default reaction_transfer_mode remains engineering
[ ] moving bounce-back formula is unchanged
[ ] no production mesh repair claims
[ ] no automatic remeshing claims
[ ] no real squid validation claims
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no sparse storage
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count == 0
[ ] docs/22_quality_gated_imported_geometry_validation.md exists
[ ] STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md complete
[ ] logs/step23_pytest.log exists
[ ] pytest -q passes
[ ] Git pre-push pytest hook passes
[ ] git diff --check passes
[ ] Step 23 artifacts are pushed to GitHub origin/main
```

## 19. Failure Handling

If a required baseline fails:

- do not relax thresholds silently;
- inspect `geometry_quality_report.json` first if quality gating fails;
- inspect driver CSV diagnostics if solver stability fails;
- inspect Step 21 comparison artifacts if deltas look suspicious;
- fix config/helper/report mistakes with focused tests;
- do not switch Step 23 scale validation to `quality_check_strict = true`;
- do not weaken Step 22 strict bad-geometry tests;
- do not claim completion from short probes;
- keep solver/coupling formulas unchanged.

If runtime is too high:

- keep required cases;
- remove only optional 64^3 cases if they were added;
- document the final executed case set in the report;
- do not omit required 48^3 rows or required 64^3 rows.

## 20. Completion Definition

Step 23 is complete only when:

- all required source files, configs, tests, docs, logs, outputs, and report exist;
- all required Step 23 baselines pass with final `[OK]` markers;
- full `pytest -q` passes and is saved to `logs/step23_pytest.log`;
- Step 23 artifact manifest passes with `large_file_count == 0`;
- Step 23 contract test passes;
- `git diff --check` passes;
- `external/taichi_LBM3D` remains unchanged;
- code/docs/logs/outputs/report are committed and pushed to GitHub `origin/main`.

Do not mark Step 23 complete before the GitHub push succeeds.
