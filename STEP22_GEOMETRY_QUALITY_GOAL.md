# Step 22 Goal: Geometry Quality Checks and Import Robustness

This file is the authoritative execution contract for Step 22 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 22 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 22

Step 21 is accepted on GitHub at commit:

```text
f5e8ac16e3fce448c4dfee701259abe1e4f28e5f
```

Step 21 established:

- imported `voxel` and `mesh` geometry support through `GeometryConfig`, `GeometrySampler3D`, and `ImportedGeometrySampler3D`;
- fixture-controlled synthetic imported geometry under `data/geometry_fixtures/`;
- imported geometry 32^3 smoke validation from Step 20;
- imported geometry 48^3 mode validation for `voxel_sphere`, `mesh_cube`, and `mesh_ellipsoid`;
- imported geometry 64^3 feasibility rows for `voxel_sphere` and `mesh_cube`;
- projection quality diagnostics with `max_relative_mass_error = 2.470733e-06`;
- Step 21 summary with `driver_row_count = 15` and `projection_quality_row_count = 3`;
- artifact manifest with `large_file_count = 0`;
- `pytest -q`: 153 passed;
- Git pre-push hook: 153 passed;
- `external/taichi_LBM3D` unchanged.

Step 21 documents that:

- Step 21 is synthetic imported geometry scale validation, not real squid validation;
- imported geometry remains limited to small synthetic voxel and mesh fixtures;
- the Step 21 mesh path is not production mesh repair;
- default `reaction_transfer_mode` remains `engineering`;
- `link_area_experimental` remains opt-in;
- the moving bounce-back formula is unchanged;
- `PenaltyFSICoupler3D`, `MovingBoundaryFSICoupler3D`, and `LinkAreaMovingBoundaryCoupler3D` are unchanged.

Step 22 must preserve all of the above.

## 2. Step 22 Objective

Add a diagnostic quality and robustness layer for imported mesh and voxel geometry before moving toward more realistic or more complex imported geometry.

Step 22 must add:

1. Mesh quality diagnostics.
2. Voxel quality diagnostics.
3. Imported geometry quality aggregation through `GeometryConfig`.
4. Optional `GeometryQualityGate` with non-strict diagnostic mode and strict failure mode.
5. Bad geometry fixtures and expected-failure baselines.
6. Sampling and resolution sensitivity diagnostics.
7. `FSIDriver3D` geometry quality report integration, defaulting to disabled.
8. Step 22 artifact manifest.
9. Documentation, report, contract test, logs, outputs, and GitHub sync.

The correct description is:

```text
geometry QA / import robustness layer for small synthetic imported geometry
```

Do not describe Step 22 as:

```text
real squid simulation
validated squid swimming
production mesh repair
automatic remeshing
production-ready mesh import
production-ready sharp-interface FSI
final strict momentum-conserving sharp-interface FSI
```

## 3. Hard Boundaries

Do not implement or change:

- no new FSI coupling physics;
- no change to `PenaltyFSICoupler3D`;
- no change to `MovingBoundaryFSICoupler3D`;
- no change to `LinkAreaMovingBoundaryCoupler3D`;
- no change to the Step 8 moving bounce-back formula;
- no change to `LBMFluid3D.step()`;
- no change to `LBMFluid3D.step_moving_bounceback()` formula;
- no change to default `reaction_transfer_mode = "engineering"`;
- no change to the opt-in nature of `link_area_experimental`;
- no two-phase flow;
- no contact angle physics;
- no squid actuation;
- no squid swimming;
- no real squid validation claims;
- no production mesh repair claim;
- no automatic remeshing;
- no sparse storage;
- no `ReducedSquidFSI`;
- no large real mesh artifacts;
- no large real voxel artifacts;
- no large scan data;
- no edits to `external/taichi_LBM3D`.

Allowed work:

- mesh quality diagnostics;
- voxel quality diagnostics;
- diagnostic warnings;
- optional strict geometry quality gate;
- intentionally bad fixtures for failure tests;
- sampling and resolution sensitivity runs;
- small CSV/JSON/NPZ diagnostic artifacts;
- docs, tests, logs, outputs, and report;
- minimal bug fixes in geometry import helpers only if required by tests and disclosed in the report.

## 4. Required Source And Artifact Files

Create:

```text
src/mesh_quality.py
src/voxel_quality.py
src/geometry_quality.py

data/geometry_fixtures/bad_nonwatertight.obj
data/geometry_fixtures/bad_degenerate.obj
data/geometry_fixtures/bad_empty_voxel.npy
data/geometry_fixtures/bad_empty_voxel_metadata.json

configs/step22_quality_mesh_cube.json
configs/step22_quality_mesh_ellipsoid.json
configs/step22_quality_voxel_sphere.json
configs/step22_quality_bad_nonwatertight.json
configs/step22_quality_bad_degenerate.json
configs/step22_quality_bad_empty_voxel.json
configs/step22_resolution_sweep_voxel_sphere.json
configs/step22_resolution_sweep_mesh_ellipsoid.json
configs/step22_driver_quality_gate_voxel_penalty.json
configs/step22_driver_quality_gate_mesh_moving_boundary.json

baseline_tests/step22_common.py
baseline_tests/run_step22_mesh_quality_sanity.py
baseline_tests/run_step22_voxel_quality_sanity.py
baseline_tests/run_step22_bad_geometry_failure_checks.py
baseline_tests/run_step22_sampling_resolution_sensitivity.py
baseline_tests/run_step22_driver_quality_gate_smoke.py
baseline_tests/run_step22_artifact_manifest.py

docs/21_geometry_quality_checks.md
tests/test_step22_geometry_quality_contract.py
STEP22_GEOMETRY_QUALITY_REPORT.md
```

Update:

```text
src/geometry_config.py
src/geometry_import.py
src/fsi_driver.py
src/__init__.py
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
docs/20_imported_geometry_scale_validation.md
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Mesh Quality Diagnostics Contract

Implement in:

```text
src/mesh_quality.py
```

Required public API:

```python
def analyze_mesh(vertices, faces, eps=1.0e-12) -> dict:
    ...
```

The returned report must include at least:

```text
vertices_count
faces_count
bounds_min_x
bounds_min_y
bounds_min_z
bounds_max_x
bounds_max_y
bounds_max_z
bounds_span_x
bounds_span_y
bounds_span_z
has_finite_vertices
has_valid_face_indices
duplicate_vertex_count
degenerate_face_count
zero_area_face_count
boundary_edge_count
nonmanifold_edge_count
is_watertight_proxy
surface_area
volume_signed
volume_abs
orientation_consistent_proxy
euler_characteristic
stable
notes
```

Required behavior:

- reject non-finite vertices;
- reject face arrays that are not triangles;
- detect invalid face indices;
- count duplicate vertices;
- count degenerate or zero-area faces using triangle area;
- count boundary edges from sorted undirected triangle edges with count `== 1`;
- count nonmanifold edges from edge count `> 2`;
- set `is_watertight_proxy = boundary_edge_count == 0 and nonmanifold_edge_count == 0`;
- compute signed and absolute volume proxy by triangle tetrahedra;
- document that signed volume and watertightness are diagnostics, not production mesh repair.

## 6. Voxel Quality Diagnostics Contract

Implement in:

```text
src/voxel_quality.py
```

Required public API:

```python
def analyze_voxel_occupancy(occupancy, metadata=None) -> dict:
    ...
```

The returned report must include at least:

```text
shape_x
shape_y
shape_z
occupied_count
occupied_fraction
empty
bounds_index_min_x
bounds_index_min_y
bounds_index_min_z
bounds_index_max_x
bounds_index_max_y
bounds_index_max_z
bbox_size_x
bbox_size_y
bbox_size_z
touches_domain_boundary
connected_component_count
largest_component_size
largest_component_fraction
surface_voxel_count
interior_voxel_count
stable
notes
```

Required behavior:

- accept 3D occupancy arrays only;
- use occupied voxels after boolean conversion;
- handle empty occupancy deterministically;
- compute connected components using 6-neighborhood flood fill or BFS;
- count surface voxels and interior voxels;
- record whether occupied voxels touch the domain boundary;
- keep this diagnostic CPU/NumPy based and lightweight for the small fixtures.

## 7. Geometry Quality Aggregator Contract

Implement in:

```text
src/geometry_quality.py
```

Required public API:

```python
def analyze_geometry_config(config: GeometryConfig) -> dict:
    ...

class GeometryQualityGate:
    def __init__(self, strict=False):
        ...

    def evaluate(self, report) -> dict:
        ...
```

`analyze_geometry_config()` behavior:

- for `geometry_type == "mesh"`: load OBJ through existing mesh loader and call `analyze_mesh()`;
- for `geometry_type == "voxel"`: load voxel geometry through existing voxel loader and call `analyze_voxel_occupancy()`;
- for procedural `box`, `ellipsoid`, and `squid_proxy`: use `GeometrySampler3D.voxelize()` or deterministic procedural stats only as diagnostics;
- include `geometry_type`, `source_file`, `quality_kind`, and scope notes in every report.

`GeometryQualityGate.evaluate()` behavior:

- return a dictionary with:

```text
pass
severity
reasons
strict
```

- default non-strict behavior must allow warnings without blocking the driver;
- strict behavior must fail bad fixtures.

Mesh strict failures:

```text
no vertices
no faces
invalid face indices
degenerate_face_count > 0
boundary_edge_count > 0
nonmanifold_edge_count > 0
```

Mesh warnings:

```text
duplicate_vertex_count > 0
boundary_edge_count > 0
nonmanifold_edge_count > 0
volume_abs <= 0
```

Voxel strict failures:

```text
occupied_count == 0
connected_component_count == 0
```

Voxel warnings:

```text
connected_component_count > 1
touches_domain_boundary == true
occupied_fraction too small or too large
```

## 8. GeometryConfig Extension Contract

Extend `GeometryConfig` with:

```python
quality_check_enabled: bool = False
quality_check_strict: bool = False
quality_report_path: Optional[str] = None
```

Rules:

- defaults must preserve Step 20 and Step 21 behavior;
- existing Step 20 and Step 21 configs must still load without modification;
- `quality_check_enabled = false` means no driver-side quality gate;
- `quality_check_enabled = true` means write a quality report before imported geometry sampling;
- `quality_check_strict = true` means bad geometry raises an error in the driver quality gate.

## 9. FSIDriver Integration Contract

Integrate with `FSIDriver3D` without changing solver or coupling formulas.

Required behavior:

- when `geometry_config.quality_check_enabled` is false, driver behavior is unchanged;
- when it is true, call `analyze_geometry_config(geometry_config)` before imported-geometry particle sampling;
- evaluate with `GeometryQualityGate(strict=geometry_config.quality_check_strict)`;
- write `geometry_quality_report.json` under the driver case output directory unless `quality_report_path` is set;
- include the gate result in the saved report;
- if strict evaluation fails, raise a clear `ValueError` with reasons;
- do not route quality reports into FSI force fields;
- do not modify `LBMFluid3D`, `MPMSolid3D`, projector formulas, or coupler formulas.

## 10. Required Bad Fixtures

Create small fixture files only:

```text
data/geometry_fixtures/bad_nonwatertight.obj
data/geometry_fixtures/bad_degenerate.obj
data/geometry_fixtures/bad_empty_voxel.npy
data/geometry_fixtures/bad_empty_voxel_metadata.json
```

Fixture requirements:

- `bad_nonwatertight.obj` must have boundary edges and fail strict mesh gate;
- `bad_degenerate.obj` must have at least one degenerate face and fail strict mesh gate;
- `bad_empty_voxel.npy` must have zero occupied voxels or trigger a known expected loader failure;
- all bad fixtures must stay small and synthetic;
- no real geometry or scan data may be added.

## 11. Baseline 1: Mesh Quality Sanity

Script:

```text
baseline_tests/run_step22_mesh_quality_sanity.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_mesh_quality_sanity.py
```

Inputs:

```text
data/geometry_fixtures/cube.obj
data/geometry_fixtures/ellipsoid_proxy.obj
```

Outputs:

```text
outputs/step22_mesh_quality_sanity/mesh_quality_results.csv
outputs/step22_mesh_quality_sanity/mesh_quality_reports.json
logs/step22_mesh_quality_sanity.log
```

Acceptance:

```text
cube vertices_count == 8
cube faces_count == 12
cube boundary_edge_count == 0
cube nonmanifold_edge_count == 0
cube degenerate_face_count == 0
cube is_watertight_proxy == true
cube volume_abs > 0
ellipsoid_proxy vertices_count > 0
ellipsoid_proxy faces_count > 0
ellipsoid_proxy degenerate_face_count == 0
ellipsoid_proxy volume_abs > 0
all rows finite
```

Final marker:

```text
[OK] Step 22 mesh quality sanity finished
```

## 12. Baseline 2: Voxel Quality Sanity

Script:

```text
baseline_tests/run_step22_voxel_quality_sanity.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_voxel_quality_sanity.py
```

Input:

```text
data/geometry_fixtures/voxel_sphere.npy
```

Outputs:

```text
outputs/step22_voxel_quality_sanity/voxel_quality_results.csv
outputs/step22_voxel_quality_sanity/voxel_quality_report.json
logs/step22_voxel_quality_sanity.log
```

Acceptance:

```text
occupied_count > 0
connected_component_count >= 1
largest_component_fraction > 0.95
surface_voxel_count > 0
interior_voxel_count > 0
empty == false
all rows finite
```

Final marker:

```text
[OK] Step 22 voxel quality sanity finished
```

## 13. Baseline 3: Bad Geometry Failure Checks

Script:

```text
baseline_tests/run_step22_bad_geometry_failure_checks.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_bad_geometry_failure_checks.py
```

Inputs:

```text
bad_nonwatertight.obj
bad_degenerate.obj
bad_empty_voxel.npy
```

Outputs:

```text
outputs/step22_bad_geometry_failure_checks/bad_geometry_results.csv
outputs/step22_bad_geometry_failure_checks/bad_geometry_reports.json
logs/step22_bad_geometry_failure_checks.log
```

Acceptance:

```text
bad_nonwatertight boundary_edge_count > 0
bad_nonwatertight strict_pass == false
bad_degenerate degenerate_face_count > 0
bad_degenerate strict_pass == false
bad_empty_voxel occupied_count == 0 or expected loader ValueError recorded
bad_empty_voxel strict_pass == false
expected_failure == true for all bad rows
```

Final marker:

```text
[OK] Step 22 bad geometry failure checks finished
```

## 14. Baseline 4: Sampling Resolution Sensitivity

Script:

```text
baseline_tests/run_step22_sampling_resolution_sensitivity.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_sampling_resolution_sensitivity.py
```

Cases:

```text
voxel_sphere
mesh_ellipsoid
```

Sweep:

```text
particles_per_axis_hint = [24, 32, 40]
mesh_voxel_resolution = [24, 32, 48] when applicable
```

Outputs:

```text
outputs/step22_sampling_resolution_sensitivity/resolution_sensitivity.csv
outputs/step22_sampling_resolution_sensitivity/resolution_sensitivity.npz
logs/step22_sampling_resolution_sensitivity.log
```

Required fields:

```text
case
geometry_type
particles_per_axis_hint
mesh_voxel_resolution
geometry_volume
projected_mass
relative_mass_error
active_cell_count
occupied_count
stable
notes
```

Acceptance:

```text
all rows finite
geometry_volume > 0
projected_mass > 0
relative_mass_error finite
active_cell_count > 0
max_volume_ratio per case < 2.0
no NaN
no Inf
```

Final marker:

```text
[OK] Step 22 sampling resolution sensitivity finished
```

## 15. Baseline 5: Driver Quality Gate Smoke

Script:

```text
baseline_tests/run_step22_driver_quality_gate_smoke.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_driver_quality_gate_smoke.py
```

Cases:

```text
voxel_sphere penalty
mesh_cube moving_boundary engineering
```

Config requirements:

```text
quality_check_enabled = true
quality_check_strict = false
n_grid = 32
n_particles = 4096
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
write_vtk = false
write_particles = false
```

Outputs:

```text
outputs/step22_driver_quality_gate_smoke/<case>/geometry_quality_report.json
outputs/step22_driver_quality_gate_smoke/quality_gate_driver_results.csv
outputs/step22_driver_quality_gate_smoke/quality_gate_driver_results.npz
logs/step22_driver_quality_gate_smoke.log
```

Acceptance:

```text
geometry_quality_report.json exists for every case
gate pass == true for every good case
driver rows stable
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
projected_mass > 0
active_cell_count > 0
```

Final marker:

```text
[OK] Step 22 driver quality gate smoke finished
```

## 16. Baseline 6: Artifact Manifest

Script:

```text
baseline_tests/run_step22_artifact_manifest.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_artifact_manifest.py
```

Outputs:

```text
outputs/step22_artifact_manifest/artifact_manifest.csv
outputs/step22_artifact_manifest/artifact_summary.json
logs/step22_artifact_manifest.log
```

Acceptance:

```text
file_count recorded
total_size_bytes recorded
total_size_mb recorded
large_file_count == 0
bad fixtures remain small
no large real geometry artifacts
Step 22 driver configs have write_vtk == false
Step 22 driver configs have write_particles == false
```

Final marker:

```text
[OK] Step 22 artifact manifest finished
```

## 17. Required Documentation

Create:

```text
docs/21_geometry_quality_checks.md
STEP22_GEOMETRY_QUALITY_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
docs/20_imported_geometry_scale_validation.md
```

Required phrases in docs/report:

```text
Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.
```

Forbidden overclaims:

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

## 18. Step 22 Report Contract

`STEP22_GEOMETRY_QUALITY_REPORT.md` must contain:

```text
1. Goal
2. Files created and updated
3. Explicit non-goals
4. Mesh quality sanity
5. Voxel quality sanity
6. Bad geometry failure checks
7. Sampling resolution sensitivity
8. Driver quality gate smoke
9. Artifact manifest summary
10. Verification commands
11. GitHub sync information
12. Acceptance checklist
13. Decision for Step 23
```

The report must include tables with at least:

```text
case
geometry_type
quality_kind
strict
pass
severity
boundary_edge_count
nonmanifold_edge_count
degenerate_face_count
occupied_count
connected_component_count
largest_component_fraction
relative_mass_error
rho_min
rho_max
mpm_min_J
stable
```

## 19. Required Contract Test

Create:

```text
tests/test_step22_geometry_quality_contract.py
```

The contract test must avoid importing heavy optional runtime paths unless it handles missing packages. Prefer file/text/artifact checks for Git pre-push compatibility.

Required file checks:

```python
required_paths = [
    "src/mesh_quality.py",
    "src/voxel_quality.py",
    "src/geometry_quality.py",
    "data/geometry_fixtures/bad_nonwatertight.obj",
    "data/geometry_fixtures/bad_degenerate.obj",
    "data/geometry_fixtures/bad_empty_voxel.npy",
    "data/geometry_fixtures/bad_empty_voxel_metadata.json",
    "baseline_tests/run_step22_mesh_quality_sanity.py",
    "baseline_tests/run_step22_voxel_quality_sanity.py",
    "baseline_tests/run_step22_bad_geometry_failure_checks.py",
    "baseline_tests/run_step22_sampling_resolution_sensitivity.py",
    "baseline_tests/run_step22_driver_quality_gate_smoke.py",
    "baseline_tests/run_step22_artifact_manifest.py",
    "docs/21_geometry_quality_checks.md",
    "STEP22_GEOMETRY_QUALITY_REPORT.md",
]
```

Required log markers:

```text
[OK] Step 22 mesh quality sanity finished
[OK] Step 22 voxel quality sanity finished
[OK] Step 22 bad geometry failure checks finished
[OK] Step 22 sampling resolution sensitivity finished
[OK] Step 22 driver quality gate smoke finished
[OK] Step 22 artifact manifest finished
```

Required artifact checks:

- mesh quality CSV proves cube watertight proxy true;
- bad non-watertight mesh strict failure is recorded;
- bad degenerate mesh strict failure is recorded;
- voxel quality CSV proves voxel sphere has occupied voxels and connected components;
- bad empty voxel expected failure is recorded;
- resolution sensitivity CSV has finite rows and `projected_mass > 0`;
- driver quality gate smoke writes `geometry_quality_report.json`;
- driver quality gate rows are stable;
- artifact summary has `large_file_count == 0`;
- `logs/step22_pytest.log` exists;
- docs/report include required scope phrases and avoid forbidden claims.

## 20. Execution Order

Use this order:

1. Read this goal, current repo state, Step 20/21 geometry import code, and existing tests.
2. Add `tests/test_step22_geometry_quality_contract.py` first and confirm RED.
3. Implement mesh and voxel quality diagnostic modules with focused unit tests if needed.
4. Add bad fixtures and geometry quality aggregator/gate.
5. Extend `GeometryConfig` with quality gate fields, default disabled.
6. Integrate `FSIDriver3D` quality report writing without changing solver formulas.
7. Add Step 22 configs and baseline runners.
8. Run mesh quality sanity and voxel quality sanity.
9. Run bad geometry failure checks.
10. Run sampling resolution sensitivity.
11. Run driver quality gate smoke.
12. Write docs and Step 22 report.
13. Run full `pytest -q` and save `logs/step22_pytest.log`.
14. Run artifact manifest after pytest.
15. Re-run Step 22 contract test.
16. Run `git diff --check`.
17. Confirm `external/taichi_LBM3D` remains unchanged.
18. Commit and push all code, docs, logs, outputs, and report to GitHub `origin/main`.

## 21. Hard Acceptance Checklist

All items must be true before Step 22 is complete:

```text
[ ] main is at the Step 22 final commit
[ ] src/mesh_quality.py exists
[ ] src/voxel_quality.py exists
[ ] src/geometry_quality.py exists
[ ] GeometryConfig quality_check_enabled defaults to false
[ ] GeometryConfig quality_check_strict defaults to false
[ ] existing Step 20/21 configs still load
[ ] FSIDriver3D default behavior is unchanged when quality_check_enabled is false
[ ] FSIDriver3D writes geometry_quality_report.json when quality_check_enabled is true
[ ] mesh quality sanity passes
[ ] voxel quality sanity passes
[ ] bad geometry failure checks pass
[ ] bad geometry expected failures are recorded
[ ] sampling resolution sensitivity passes
[ ] driver quality gate smoke passes
[ ] no FSI formula changes
[ ] default reaction_transfer_mode remains engineering
[ ] moving bounce-back formula is unchanged
[ ] no production mesh repair claims
[ ] no automatic remeshing claims
[ ] no real squid validation claims
[ ] no squid actuation/swimming
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count == 0
[ ] docs/21_geometry_quality_checks.md exists
[ ] STEP22_GEOMETRY_QUALITY_REPORT.md complete
[ ] logs/step22_pytest.log exists
[ ] pytest -q passes
[ ] Git pre-push pytest hook passes
[ ] git diff --check passes
[ ] Step 22 artifacts are pushed to GitHub origin/main
```

## 22. Failure Handling

If a required baseline fails:

- do not relax the acceptance threshold silently;
- inspect the failing geometry report or CSV first;
- fix diagnostic code or fixture/config mistakes with a focused test;
- if a geometry quality diagnostic must be tuned, document the final rule and reason in the report;
- do not replace a failing strict bad-geometry test with a weaker warning-only test;
- do not claim completion from a short probe;
- keep solver/coupling formulas unchanged.

If runtime becomes excessive:

- keep baselines small and diagnostic-only;
- prefer reducing diagnostic sweep breadth only if the report documents the final sweep;
- do not omit required rows from final artifacts.

## 23. Completion Definition

Step 22 is complete only when:

- all required source files, configs, fixtures, tests, docs, logs, outputs, and report exist;
- all required Step 22 baselines pass with final `[OK]` markers;
- full `pytest -q` passes and is saved to `logs/step22_pytest.log`;
- Step 22 artifact manifest passes with `large_file_count == 0`;
- Step 22 contract test passes;
- `git diff --check` passes;
- `external/taichi_LBM3D` remains unchanged;
- code/docs/logs/outputs/report are committed and pushed to GitHub `origin/main`.

Do not mark Step 22 complete before the GitHub push succeeds.
