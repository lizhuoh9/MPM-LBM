# Step 24 Goal: Strict Quality-Gated Imported Geometry Long-Run Validation

This file is the authoritative execution contract for Step 24 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 24 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 24

Step 23 is accepted on GitHub at commit:

```text
7862046d1918df7a8e0e90fd3f3fee8178b9c280
```

Step 23 established:

- `quality_check_enabled = true` and `quality_check_strict = false` scale validation for good synthetic imported geometry;
- quality reports for all required Step 23 driver rows;
- 48^3 imported geometry rows for `voxel_sphere`, `mesh_cube`, and `mesh_ellipsoid`;
- 64^3 conservative imported geometry feasibility rows;
- Step 21 vs Step 23 comparable rows stayed stable with differences at approximately `1e-6` scale;
- 15 quality reports all passed with no errors and no warnings;
- `pytest -q`: 173 passed;
- `external/taichi_LBM3D` unchanged;
- artifact manifest with `large_file_count == 0`.

Step 23 explicitly did not validate real squid geometry and did not change:

- `PenaltyFSICoupler3D`;
- `MovingBoundaryFSICoupler3D`;
- `LinkAreaMovingBoundaryCoupler3D`;
- moving bounce-back formulas;
- LBM step formulas;
- default `reaction_transfer_mode = "engineering"`;
- default `quality_check_enabled = false`;
- default `quality_check_strict = false`.

Step 24 must preserve all of the above.

## 2. Step 24 Objective

Run strict quality-gated synthetic imported geometry validation over a longer moving-boundary window.

The correct description is:

```text
strict quality-gated synthetic imported geometry long-run validation
```

Step 24 bridges:

```text
Step 22 strict bad-geometry failure evidence
+
Step 23 non-strict good imported-geometry scale evidence
```

Step 24 must prove that:

1. `quality_check_enabled = true` and `quality_check_strict = true` do not falsely reject the current good synthetic imported geometry fixtures.
2. Strict quality gating does not change sampling, projection, LBM, MPM, FSI, or moving-boundary behavior.
3. Imported voxel and mesh geometries remain stable under a longer 48^3 moving-boundary window.
4. `link_area_experimental` remains finite, bounded, and comparable on imported geometry under the same longer window.
5. Selected 64^3 imported geometry rows remain feasible under strict quality gating.
6. Every Step 24 driver row writes `geometry_quality_report.json`.
7. Defaults remain unchanged: `quality_check_enabled = false`, `quality_check_strict = false`, and `reaction_transfer_mode = "engineering"`.
8. Artifact volume remains controlled and does not continue the Step 23 artifact growth trend.

Step 24 is not a real squid geometry validation step. It is not a new physics step. It is a strict-quality-gate workflow and evidence step over existing synthetic imported geometry fixtures.

## 3. Hard Boundaries

Do not implement:

- new FSI physics;
- new coupling formulas;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to the moving bounce-back formula;
- changes to LBM step formulas;
- changes to MPM constitutive formulas;
- changes to projection formulas;
- default `quality_check_enabled = true`;
- default `quality_check_strict = true`;
- default `reaction_transfer_mode = "link_area_experimental"`;
- real squid geometry validation;
- real squid geometry ingestion contract;
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

- strict quality-gated driver configs;
- long-run baseline runners for selected imported geometry rows;
- quality report aggregation;
- Step 23 prefix comparison;
- strict vs non-strict quality report comparison;
- timing and overhead diagnostics from existing driver timing fields;
- artifact budget enforcement;
- docs, reports, tests, logs, and small reproducibility outputs;
- helper code in `baseline_tests/step24_common.py` only;
- contract tests that verify files, configs, outputs, defaults, reports, logs, artifact budgets, and forbidden claims.

Any helper refactor must stay outside core solver behavior unless a contract test proves it is documentation-only or baseline-script-only plumbing.

## 4. Required Source And Artifact Files

Create:

```text
STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_GOAL.md
STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md

configs/step24_strict_voxel_sphere_48_moving_boundary.json
configs/step24_strict_voxel_sphere_48_link_area.json

configs/step24_strict_mesh_cube_48_moving_boundary.json
configs/step24_strict_mesh_cube_48_link_area.json

configs/step24_strict_mesh_ellipsoid_48_moving_boundary.json
configs/step24_strict_mesh_ellipsoid_48_link_area.json

configs/step24_strict_voxel_sphere_64_moving_boundary.json
configs/step24_strict_mesh_cube_64_moving_boundary.json
configs/step24_strict_mesh_cube_64_link_area.json

baseline_tests/step24_common.py
baseline_tests/run_step24_strict_voxel_sphere_48_long.py
baseline_tests/run_step24_strict_mesh_cube_48_long.py
baseline_tests/run_step24_strict_mesh_ellipsoid_48_long.py
baseline_tests/run_step24_strict_imported_geometry_64_feasibility.py
baseline_tests/run_step24_quality_report_aggregation.py
baseline_tests/run_step24_step23_prefix_comparison.py
baseline_tests/run_step24_strict_non_strict_report_comparison.py
baseline_tests/run_step24_timing_overhead_summary.py
baseline_tests/run_step24_artifact_manifest.py

docs/23_strict_quality_gated_imported_geometry_long_run.md
tests/test_step24_strict_quality_gated_imported_geometry_long_run_contract.py
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
docs/22_quality_gated_imported_geometry_validation.md
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Step 24 Validation Matrix

Use a risk-focused matrix rather than repeating every Step 23 row.

### 5.1 48^3 Long-Run Rows

Run six 48^3 long-window moving-boundary rows:

```text
voxel_sphere 48 moving_boundary engineering
voxel_sphere 48 moving_boundary link_area_experimental

mesh_cube 48 moving_boundary engineering
mesh_cube 48 moving_boundary link_area_experimental

mesh_ellipsoid 48 moving_boundary engineering
mesh_ellipsoid 48 moving_boundary link_area_experimental
```

Required config values:

```text
n_grid = 48
n_particles = 4096
n_lbm_steps = 30
mpm_substeps_per_lbm_step = 10
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
```

Rationale:

- Step 16 already used 50-step box and 30-step squid_proxy windows as long-run precedents.
- Step 19 already used 30/50-step windows for link-area long-run validation.
- A 30-step imported-geometry moving-boundary window is enough to bridge Step 23 to the next real-geometry intake contract without producing large artifacts.

### 5.2 64^3 Strict Feasibility Rows

Run three conservative 64^3 strict feasibility rows:

```text
voxel_sphere 64 moving_boundary engineering
mesh_cube 64 moving_boundary engineering
mesh_cube 64 moving_boundary link_area_experimental
```

Required config values:

```text
n_grid = 64
n_particles = 4096
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
```

Rationale:

- Preserve conservative 64^3 feasibility scope.
- Add strict quality-gated `mesh_cube 64 moving_boundary` coverage.
- Add strict quality-gated `mesh_cube 64 link_area_experimental` coverage.
- Avoid claiming production performance or final 64^3 readiness.

## 6. Step 24 Config Rules

All Step 24 configs must explicitly set:

```json
"quality_check_enabled": true,
"quality_check_strict": true,
"write_vtk": false,
"write_particles": false
```

All Step 24 configs must also explicitly preserve:

```json
"n_particles": 4096
```

48^3 configs must set:

```json
"n_grid": 48,
"n_lbm_steps": 30,
"mpm_substeps_per_lbm_step": 10
```

64^3 configs must set:

```json
"n_grid": 64,
"n_lbm_steps": 5,
"mpm_substeps_per_lbm_step": 5
```

All engineering rows must set:

```json
"coupling_mode": "moving_boundary",
"reaction_transfer_mode": "engineering"
```

All link-area rows must set:

```json
"coupling_mode": "moving_boundary",
"reaction_transfer_mode": "link_area_experimental",
"link_area_policy": "inverse_length",
"link_area_scale_min": 0.25,
"link_area_scale_max": 2.0
```

Every config must use existing synthetic imported geometry fixtures from Step 21/23. Do not introduce real squid geometry, production meshes, scan data, or large voxel files.

## 7. Required Common Helper Contract

Implement in:

```text
baseline_tests/step24_common.py
```

Recommended helpers:

```python
def make_strict_quality_gated_config(base_config_path, out_config_path, n_lbm_steps, mpm_substeps):
    ...

def enforce_step24_config(config, config_path):
    ...

def run_strict_quality_gated_driver_case(config_path, case, config, out_dir):
    ...

def collect_geometry_quality_report(out_dir):
    ...

def summarize_long_run_row(case, config, diagnostics, driver, report_payload, report_path):
    ...

def assert_step24_row_stable(row):
    ...

def write_step24_rows(rows, csv_path, npz_path):
    ...

def read_step23_comparison_rows():
    ...

def compare_step24_prefix_to_step23(step24_rows, step23_rows):
    ...

def compare_strict_and_non_strict_quality_reports(strict_reports, non_strict_reports):
    ...

def summarize_step24_artifacts(paths):
    ...
```

The helper may reuse Step 23 helper patterns, but Step 24 naming, fields, and output paths must be Step 24 specific.

## 8. `enforce_step24_config()` Requirements

`enforce_step24_config()` must reject:

- `quality_check_enabled != true`;
- `quality_check_strict != true`;
- `write_vtk != false`;
- `write_particles != false`;
- `coupling_mode != "moving_boundary"`;
- `reaction_transfer_mode` outside `{"engineering", "link_area_experimental"}`;
- `reaction_transfer_mode == "link_area_experimental"` without `link_area_policy == "inverse_length"`;
- `link_area_scale_min != 0.25` for link-area rows;
- `link_area_scale_max != 2.0` for link-area rows;
- `n_grid` outside `{48, 64}`;
- `n_particles != 4096`;
- 48^3 configs with `n_lbm_steps < 30`;
- 48^3 configs with `mpm_substeps_per_lbm_step < 10`;
- 64^3 configs with `n_lbm_steps < 5`;
- 64^3 configs with `mpm_substeps_per_lbm_step < 5`;
- missing imported geometry config path;
- missing geometry quality report after a driver run;
- any config path under `external/taichi_LBM3D`.

The helper should fail fast with clear errors and must not silently downgrade strict quality gating.

## 9. Row Summary Fields

Every Step 24 driver row should write CSV and NPZ records with at least:

```text
case
geometry_type
geometry_source
quality_kind
mode
reaction_transfer_mode
quality_check_enabled
quality_check_strict
quality_pass
quality_severity
quality_warnings_count
quality_reasons_count
quality_report_path
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
completed_lbm_steps
total_mpm_substeps
rho_min_global
rho_max_global
lbm_max_v_global
mpm_min_J_global
mpm_max_speed_global
projected_mass
active_cell_count
cell_force_max_norm
hydro_force_max_norm
bb_link_count_min
bb_link_count_max
active_reaction_particle_count_max
area_scale_final
area_scale_min
area_scale_max
raw_area_scale_final
stable
notes
```

It is acceptable to add additional diagnostics if they come from existing driver diagnostics and do not require solver formula changes.

## 10. Stability Contract

`assert_step24_row_stable()` must check:

- `stable == true`;
- `quality_pass == true`;
- `quality_severity == "ok"`;
- `quality_check_enabled == true`;
- `quality_check_strict == true`;
- `quality_reasons_count == 0`;
- `quality_warnings_count == 0`;
- `rho_min_global > 0.95`;
- `rho_max_global < 1.05`;
- `lbm_max_v_global < 0.1`;
- `mpm_min_J_global > 0.0`;
- `mpm_max_speed_global < 10.0`;
- `projected_mass > 0.0`;
- `active_cell_count > 0`;
- `completed_lbm_steps >= n_lbm_steps`;
- `total_mpm_substeps >= n_lbm_steps * mpm_substeps_per_lbm_step`;
- no NaN values;
- no Inf values;
- `geometry_quality_report.json` exists at `quality_report_path`.

For all moving-boundary rows:

- `cell_force_max_norm == 0.0`;
- `bb_link_count_min > 0`;
- `bb_link_count_max > 0`;
- `active_reaction_particle_count_max > 0`;
- `hydro_force_max_norm >= 0.0`.

For `reaction_transfer_mode == "engineering"` rows:

- `area_scale_final == 1.0` or the row clearly records area scale as not applicable;
- no link-area coupler should be active.

For `reaction_transfer_mode == "link_area_experimental"` rows:

- `area_scale_final` is finite;
- `area_scale_min` is finite;
- `area_scale_max` is finite;
- `raw_area_scale_final` is finite unless explicitly marked not available;
- `area_scale_min >= 0.25`;
- `area_scale_max <= 2.0`;
- `0.25 <= area_scale_final <= 2.0`;
- area scale is not NaN and is not continuously invalid.

For mesh reports:

- `vertices_count > 0`;
- `faces_count > 0`;
- `boundary_edge_count == 0`;
- `degenerate_face_count == 0`;
- `nonmanifold_edge_count == 0`;
- strict gate reports no reasons and no warnings.

For voxel reports:

- `occupied_count > 0`;
- `connected_component_count == 1`;
- `largest_component_fraction == 1.0`;
- strict gate reports no reasons and no warnings.

## 11. Required Baseline Runners

### 11.1 `run_step24_strict_voxel_sphere_48_long.py`

Run:

```text
voxel_sphere 48 moving_boundary engineering
voxel_sphere 48 moving_boundary link_area_experimental
```

Write:

```text
outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv
outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.npz
logs/step24_strict_voxel_sphere_48_long.log
```

Log success marker:

```text
[OK] Step 24 strict voxel_sphere 48 long-run finished
```

### 11.2 `run_step24_strict_mesh_cube_48_long.py`

Run:

```text
mesh_cube 48 moving_boundary engineering
mesh_cube 48 moving_boundary link_area_experimental
```

Write:

```text
outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv
outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.npz
logs/step24_strict_mesh_cube_48_long.log
```

Log success marker:

```text
[OK] Step 24 strict mesh_cube 48 long-run finished
```

### 11.3 `run_step24_strict_mesh_ellipsoid_48_long.py`

Run:

```text
mesh_ellipsoid 48 moving_boundary engineering
mesh_ellipsoid 48 moving_boundary link_area_experimental
```

Write:

```text
outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv
outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.npz
logs/step24_strict_mesh_ellipsoid_48_long.log
```

Log success marker:

```text
[OK] Step 24 strict mesh_ellipsoid 48 long-run finished
```

### 11.4 `run_step24_strict_imported_geometry_64_feasibility.py`

Run:

```text
voxel_sphere 64 moving_boundary engineering
mesh_cube 64 moving_boundary engineering
mesh_cube 64 moving_boundary link_area_experimental
```

Write:

```text
outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv
outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.npz
logs/step24_strict_imported_geometry_64_feasibility.log
```

Log success marker:

```text
[OK] Step 24 strict imported geometry 64 feasibility finished
```

## 12. Quality Report Aggregation

Implement:

```text
baseline_tests/run_step24_quality_report_aggregation.py
```

Aggregate every Step 24 `geometry_quality_report.json`.

Expected count:

```text
quality_report_count == 9
```

Write:

```text
outputs/step24_quality_report_aggregation/quality_report_summary.csv
outputs/step24_quality_report_aggregation/quality_report_summary.json
logs/step24_quality_report_aggregation.log
```

Required summary checks:

- `quality_report_count == 9`;
- `pass_count == 9`;
- `error_count == 0`;
- `warning_count == 0`;
- mesh row count matches the Step 24 matrix;
- voxel row count matches the Step 24 matrix;
- every row has `gate.strict == true`;
- every report has `gate.pass == true`;
- every report has `gate.severity == "ok"`;
- every report path exists and is smaller than 100 KB.

Log success marker:

```text
[OK] Step 24 quality report aggregation finished
```

## 13. Step 23 Prefix Comparison

Implement:

```text
baseline_tests/run_step24_step23_prefix_comparison.py
```

The goal is to prove strict quality report generation did not alter driver dynamics.

Comparison rules:

- 48^3 Step 24 rows: compare Step 24 diagnostic row at `step == 10` against the corresponding Step 23 final row at `step == 10`.
- 64^3 Step 24 rows: compare Step 24 diagnostic row at `step == 5` against the corresponding Step 23 row at `step == 5` where an overlapping Step 23 row exists.
- Rows without a Step 23 overlap must be explicitly marked `not_comparable_step23_overlap_missing` and are accepted only through Step 24 stability and strict quality report checks.

Required overlapping 48^3 rows:

```text
voxel_sphere 48 moving_boundary engineering
voxel_sphere 48 moving_boundary link_area_experimental
mesh_cube 48 moving_boundary engineering
mesh_cube 48 moving_boundary link_area_experimental
mesh_ellipsoid 48 moving_boundary engineering
mesh_ellipsoid 48 moving_boundary link_area_experimental
```

Required overlapping 64^3 rows:

```text
voxel_sphere 64 moving_boundary engineering
```

Acceptance thresholds:

```text
abs(rho_min_delta) <= 1e-5
abs(rho_max_delta) <= 1e-5
abs(lbm_max_v_delta) <= 1e-5
abs(mpm_min_J_delta) <= 1e-5
abs(projected_mass_delta) <= 1e-5
active_cell_count_delta == 0
stable_both == true
```

Write:

```text
outputs/step24_step23_prefix_comparison/step23_prefix_comparison.csv
outputs/step24_step23_prefix_comparison/step23_prefix_comparison.json
logs/step24_step23_prefix_comparison.log
```

Log success marker:

```text
[OK] Step 24 Step 23 prefix comparison finished
```

## 14. Strict Vs Non-Strict Report Comparison

Implement:

```text
baseline_tests/run_step24_strict_non_strict_report_comparison.py
```

The goal is to prove strict mode changes gate policy, not geometry diagnostics, for good synthetic imported geometry.

Comparison sources:

- Use Step 23 non-strict reports for rows that overlap Step 23.
- For Step 24-only rows with no Step 23 non-strict counterpart, generate QA-only non-strict reports from the same synthetic imported geometry fixture without running a full solver row.
- Do not add a second long solver matrix just to compare reports.

The comparison must ignore:

- output paths;
- timestamps if present;
- `gate.strict`;
- any field that is explicitly path-only or run-location-only.

The comparison must require:

- same `quality_kind`;
- same geometry type;
- same pass result;
- same severity;
- both strict and non-strict reports pass;
- strict severity is `"ok"`;
- non-strict severity is `"ok"`;
- both reasons counts are zero;
- both warnings counts are zero.

For mesh diagnostics, require:

- same `vertices_count`;
- same `faces_count`;
- same `boundary_edge_count`;
- same `degenerate_face_count`;
- same `nonmanifold_edge_count`.

For voxel diagnostics, require:

- same `occupied_count`;
- same `connected_component_count`;
- same `largest_component_fraction`.

Write:

```text
outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.csv
outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.json
logs/step24_strict_non_strict_report_comparison.log
```

Log success marker:

```text
[OK] Step 24 strict vs non-strict report comparison finished
```

## 15. Timing And Overhead Summary

Implement:

```text
baseline_tests/run_step24_timing_overhead_summary.py
```

Use existing `FSIDriver3D.performance_row()` or already recorded timing fields. Do not change solver timing instrumentation unless a minimal baseline-script-only read path is insufficient.

Write:

```text
outputs/step24_timing_overhead_summary/step24_timing_summary.csv
outputs/step24_timing_overhead_summary/step24_timing_summary.json
logs/step24_timing_overhead_summary.log
```

Required metrics:

```text
row_count
median_total_time
max_total_time
quality_report_count
quality_report_total_size_bytes
quality_report_max_size_bytes
```

Timing is a workflow and artifact-budget diagnostic only. Do not describe Step 24 timing as a production benchmark or performance proof.

Log success marker:

```text
[OK] Step 24 timing overhead summary finished
```

## 16. Artifact Budget

Implement:

```text
baseline_tests/run_step24_artifact_manifest.py
```

Write:

```text
outputs/step24_artifact_manifest/artifact_summary.csv
outputs/step24_artifact_manifest/artifact_summary.json
logs/step24_artifact_manifest.log
```

Required artifact checks:

- `large_file_count == 0`;
- `step24_quality_report_count == 9`;
- no Step 24 `.vtr` files;
- no Step 24 particle `.npy` outputs;
- each Step 24 `geometry_quality_report.json` is smaller than 100 KB;
- Step 24 output total size is smaller than 25 MB;
- repository artifact summary `total_size_mb < 150`;
- committed artifacts are small CSV, JSON, NPZ, and log files only;
- no large real mesh or voxel artifacts are introduced.

The artifact manifest must make the Step 24 budget explicit. Step 23 already reached approximately 117.3 MB total artifact size, so Step 24 must not casually grow the repository.

Log success marker:

```text
[OK] Step 24 artifact manifest finished
```

## 17. Documentation Requirements

Create:

```text
docs/23_strict_quality_gated_imported_geometry_long_run.md
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
docs/22_quality_gated_imported_geometry_validation.md
```

Required scope language must appear across docs and report:

```text
Step 24 runs strict quality-gated synthetic imported geometry long-run validation.
Step 24 uses quality_check_enabled=true and quality_check_strict=true for selected imported geometry rows.
Step 24 is not real squid validation.
Step 24 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 24 mesh path is not production mesh repair or automatic remeshing.
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

Docs must clearly state the next recommended step after Step 24:

```text
Step 25 should be a controlled real geometry intake contract, starting with geometry QA, normalization, and sampling reproducibility only.
```

Step 25 must not be described as validated squid swimming or production FSI.

## 18. Contract Test Requirements

Create:

```text
tests/test_step24_strict_quality_gated_imported_geometry_long_run_contract.py
```

The contract test must verify:

- every required Step 24 source file exists;
- every required Step 24 config exists;
- every config sets `quality_check_enabled is True`;
- every config sets `quality_check_strict is True`;
- every config sets `write_vtk is False`;
- every config sets `write_particles is False`;
- every config uses `coupling_mode == "moving_boundary"`;
- every config uses synthetic imported geometry;
- every 48^3 config uses `n_lbm_steps >= 30`;
- every 48^3 config uses `mpm_substeps_per_lbm_step >= 10`;
- every 64^3 config uses `n_lbm_steps >= 5`;
- every 64^3 config uses `mpm_substeps_per_lbm_step >= 5`;
- every driver output CSV exists and has the expected row count;
- every driver output row is finite;
- every driver output row is stable;
- every row has `quality_pass == true`;
- every row has `quality_severity == "ok"`;
- every row has `quality_check_strict == true`;
- every row has `rho_min_global > 0.95`;
- every row has `rho_max_global < 1.05`;
- every row has `lbm_max_v_global < 0.1`;
- every row has `mpm_min_J_global > 0`;
- every row has `mpm_max_speed_global < 10`;
- every row has positive projected mass and active cell count;
- every moving-boundary row has positive bounce-back link counts;
- every link-area row has finite bounded area scale;
- quality report aggregation has exactly 9 reports, all pass, no warnings, and no errors;
- Step 23 prefix comparison passes for every overlapping row;
- strict vs non-strict report comparison passes;
- timing summary exists and is not used as a production benchmark claim;
- artifact manifest passes the Step 24 budget;
- `logs/step24_pytest.log` exists;
- all expected Step 24 logs contain success markers;
- defaults remain disabled in `src/geometry_config.py` and `src/fsi_config.py`;
- report contains all required sections;
- report contains the complete acceptance checklist;
- docs and report include the required scope language;
- docs and report do not include forbidden claims;
- `external/taichi_LBM3D` is unchanged.

## 19. Required Report

Create:

```text
STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md
```

Required sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. 48^3 Voxel_Sphere Strict Long-Run
## 5. 48^3 Mesh_Cube Strict Long-Run
## 6. 48^3 Mesh_Ellipsoid Strict Long-Run
## 7. 64^3 Strict Imported Geometry Feasibility
## 8. Quality Report Aggregation
## 9. Step 23 Prefix Comparison
## 10. Strict Vs Non-Strict Report Comparison
## 11. Timing And Overhead Summary
## 12. Artifact Manifest Summary
## 13. Verification Commands
## 14. GitHub Sync Information
## 15. Acceptance Checklist
## 16. Decision For Step 25
```

The report must include exact commands, exact artifact paths, exact row counts, exact summary values, and the final commit hash after push.

## 20. Verification Command Order

Run in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_voxel_sphere_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_cube_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_ellipsoid_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_step23_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_non_strict_report_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_timing_overhead_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step24_strict_quality_gated_imported_geometry_long_run_contract.py -q
git diff --check
git status --short external/taichi_LBM3D
```

Also write full pytest output to:

```text
logs/step24_pytest.log
```

If any baseline fails, stop and diagnose the failed artifact. Do not weaken thresholds, downgrade strict mode, or remove checks to force a pass.

## 21. Commit And Push Requirements

After Step 24 implementation is accepted locally:

1. Review `git diff`.
2. Confirm `external/taichi_LBM3D` is unchanged.
3. Commit all relevant Step 24 code, configs, docs, logs, outputs, tests, goal, and report.
4. Use a conventional commit message, recommended:

```text
test: add step24 strict quality gated imported geometry validation
```

5. Push to the configured GitHub remote, normally `origin main`, unless the user explicitly says not to push.
6. Record the final commit hash and remote branch in the Step 24 report.

## 22. Acceptance Checklist

The final Step 24 report must include this checklist with every accepted item checked:

```text
- [ ] strict voxel_sphere 48^3 long-run engineering passes
- [ ] strict voxel_sphere 48^3 long-run link_area passes
- [ ] strict mesh_cube 48^3 long-run engineering passes
- [ ] strict mesh_cube 48^3 long-run link_area passes
- [ ] strict mesh_ellipsoid 48^3 long-run engineering passes
- [ ] strict mesh_ellipsoid 48^3 long-run link_area passes
- [ ] strict voxel_sphere 64^3 moving_boundary feasibility passes
- [ ] strict mesh_cube 64^3 moving_boundary feasibility passes
- [ ] strict mesh_cube 64^3 link_area feasibility passes
- [ ] every Step 24 row writes geometry_quality_report.json
- [ ] every Step 24 gate.strict == true
- [ ] every Step 24 quality_pass == true
- [ ] every Step 24 quality_severity == ok
- [ ] mesh reports have zero boundary/degen/nonmanifold errors
- [ ] voxel reports are non-empty and connected
- [ ] Step 23 prefix comparison passes for overlapping rows
- [ ] Step 24-only rows are explicitly marked as lacking Step 23 overlap
- [ ] strict vs non-strict report comparison passes
- [ ] quality report aggregation count == 9
- [ ] quality report warnings == 0
- [ ] quality report errors == 0
- [ ] rho_min_global > 0.95
- [ ] rho_max_global < 1.05
- [ ] lbm_max_v_global < 0.1
- [ ] mpm_min_J_global > 0
- [ ] mpm_max_speed_global < 10
- [ ] moving_boundary rows keep cell_force_max_norm == 0
- [ ] moving_boundary rows have bb_link_count_min > 0
- [ ] moving_boundary rows have active_reaction_particle_count_max > 0
- [ ] link_area rows have finite bounded area_scale
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
- [ ] no external/taichi_LBM3D edits
- [ ] no Step 24 .vtr outputs
- [ ] no Step 24 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 24 output total size budget passes
- [ ] repo artifact_summary total_size_mb < 150
- [ ] timing summary exists and is framed as workflow diagnostics only
- [ ] logs/step24_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 24 contract test passes
- [ ] git diff --check passes
- [ ] pre-push hook passes if push is performed
- [ ] Step 24 artifacts are pushed to GitHub origin/main unless user explicitly says not to push
```

## 23. Decision For Step 25

If Step 24 passes, the next step should be:

```text
Step 25 Controlled Real Geometry Intake Contract
```

Step 25 should start with:

- real geometry file contract;
- geometry QA;
- units and normalization;
- watertightness and topology diagnostics;
- sampling reproducibility;
- artifact budget;
- no swimming claim;
- no production FSI claim.

Step 25 should not immediately claim real squid swimming, production sharp-interface FSI, or final solver readiness.
