# Step 21 Goal: Imported Geometry Scale Validation

This file is the authoritative execution contract for Step 21 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 21 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 21

Step 20 is accepted on GitHub at commit:

```text
d4b08bdafd63dff8d38baa544e6130ddad805be9
```

Step 20 established:

- small synthetic voxel geometry import;
- small synthetic OBJ mesh geometry import;
- `voxel` and `mesh` in `VALID_GEOMETRY_TYPES`;
- imported geometry support through `GeometryConfig`, `GeometrySampler3D`, and `ImportedGeometrySampler3D`;
- existing `FSIDriver3D` integration through `geometry_type` and `geometry_config_path`;
- 32^3 imported-geometry projection diagnostics;
- 32^3 imported-geometry driver smoke baselines;
- fixture-controlled synthetic geometry under `data/geometry_fixtures/`;
- artifact manifest with `large_file_count = 0`;
- `pytest -q`: 143 passed;
- Git pre-push hook: 143 passed;
- `external/taichi_LBM3D` unchanged.

Step 20 documents that:

- imported geometry is a scaffold for small synthetic voxel and mesh fixtures;
- imported geometry is not real squid validation;
- the Step 20 mesh path is not production mesh repair;
- default `reaction_transfer_mode` remains `engineering`;
- `link_area_experimental` remains opt-in;
- the moving bounce-back formula is unchanged;
- `PenaltyFSICoupler3D`, `MovingBoundaryFSICoupler3D`, and `LinkAreaMovingBoundaryCoupler3D` are unchanged;
- this project is still not final strict momentum-conserving sharp-interface FSI.

Step 21 must preserve all of the above.

## 2. Step 21 Objective

Carry Step 20 synthetic imported voxel and mesh geometries from 32^3 smoke validation to larger engineering validation.

Step 21 must add:

1. `voxel_sphere` 48^3 imported geometry mode validation.
2. `mesh_cube` 48^3 imported geometry mode validation.
3. `mesh_ellipsoid` 48^3 imported geometry mode validation.
4. Imported-geometry 64^3 feasibility baselines.
5. Imported-geometry projection quality diagnostics.
6. Imported-geometry scale summary artifacts.
7. Step 21 artifact manifest.
8. Documentation, report, contract test, logs, outputs, and GitHub sync.

The correct description is:

```text
synthetic imported voxel / mesh geometry scale validation
```

Do not describe Step 21 as:

```text
real squid simulation
validated squid swimming
production mesh repair
production-ready mesh import
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
- no change to Step 20 imported geometry formulas unless needed only for bug fixes with tests and report disclosure;
- no two-phase flow;
- no contact angle physics;
- no squid actuation;
- no squid swimming;
- no real squid validation claims;
- no production mesh repair claim;
- no sparse storage;
- no `ReducedSquidFSI`;
- no large real mesh artifacts;
- no large real voxel artifacts;
- no large Step 21 VTK outputs;
- no edits to `external/taichi_LBM3D`.

Allowed work:

- imported geometry 48^3 validation runs;
- imported geometry 64^3 feasibility runs;
- mode matrix comparisons for imported geometry;
- projection quality diagnostics;
- memory / timing / artifact summaries;
- docs, tests, logs, outputs, and report;
- conservative config-only tuning of `target_u_lbm`, `mb_force_cap_norm`, `penalty_force_cap_lbm`, or step counts when needed for stability, as long as the report documents the final values.

## 4. Required Source And Artifact Files

Create:

```text
baseline_tests/step21_common.py
baseline_tests/run_step21_voxel_sphere_48_modes.py
baseline_tests/run_step21_mesh_cube_48_modes.py
baseline_tests/run_step21_mesh_ellipsoid_48_modes.py
baseline_tests/run_step21_imported_geometry_64_feasibility.py
baseline_tests/run_step21_imported_geometry_projection_quality.py
baseline_tests/run_step21_imported_geometry_scale_summary.py
baseline_tests/run_step21_artifact_manifest.py
docs/20_imported_geometry_scale_validation.md
tests/test_step21_imported_geometry_scale_contract.py
STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md
```

Create config files:

```text
configs/step21_voxel_sphere_48_none.json
configs/step21_voxel_sphere_48_penalty.json
configs/step21_voxel_sphere_48_moving_boundary.json
configs/step21_voxel_sphere_48_link_area.json

configs/step21_mesh_cube_48_none.json
configs/step21_mesh_cube_48_penalty.json
configs/step21_mesh_cube_48_moving_boundary.json
configs/step21_mesh_cube_48_link_area.json

configs/step21_mesh_ellipsoid_48_none.json
configs/step21_mesh_ellipsoid_48_penalty.json
configs/step21_mesh_ellipsoid_48_moving_boundary.json
configs/step21_mesh_ellipsoid_48_link_area.json

configs/step21_voxel_sphere_64_penalty.json
configs/step21_voxel_sphere_64_moving_boundary.json
configs/step21_mesh_cube_64_penalty.json
configs/step21_mesh_cube_64_moving_boundary_optional.json
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/10_performance_memory.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Shared Step 21 Baseline Contract

All Step 21 baseline scripts must:

- use deterministic imported geometry configs from Step 20;
- run through `FSIDriver3D` for driver baselines;
- use `GeometrySampler3D` and `MPMToLBMProjector3D` for projection-quality diagnostics;
- write under `outputs/step21_*`;
- save logs under `logs/step21_*.log` when run through acceptance commands;
- raise on NaN or Inf;
- raise on missing output files;
- raise on threshold failures;
- print a final `[OK] ... finished` marker.

Shared output fields should include:

```text
case
geometry_type
geometry_source
mode
reaction_transfer_mode
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
completed_lbm_steps
total_mpm_substeps
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
projected_mass
active_cell_count
cell_force_max_norm
hydro_force_max_norm
bb_link_count
active_reaction_particle_count
area_scale_final
stable
notes
```

Shared stable-row thresholds:

```text
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
projected_mass > 0
active_cell_count > 0
no NaN
no Inf
```

Mode boundary checks:

```text
none rows: cell_force_max_norm == 0
penalty rows: cell_force_max_norm is finite and > 0
moving_boundary rows: cell_force_max_norm == 0
moving_boundary rows: bb_link_count > 0
moving_boundary rows: hydro_force_max_norm > 0
link_area_experimental rows: area_scale_final finite
link_area_experimental rows: reaction_transfer_mode == link_area_experimental
engineering rows: reaction_transfer_mode == engineering
```

## 6. Recommended Config Values

### 6.1 48^3 `voxel_sphere`

Use:

```text
geometry_type = voxel
geometry_config_path = configs/step20_voxel_sphere_geometry.json
n_grid = 48
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = [0.005, 0.0, 0.0]
output_interval = 10
write_vtk = false
write_particles = false
```

Required modes:

```text
none
penalty
moving_boundary engineering
moving_boundary link_area_experimental
```

### 6.2 48^3 `mesh_cube`

Because `mesh_cube` occupies a large volume, use conservative velocity:

```text
geometry_type = mesh
geometry_config_path = configs/step20_mesh_cube_geometry.json
n_grid = 48
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = [0.003, 0.0, 0.0]
mb_force_cap_norm = 1.0e-5
output_interval = 10
write_vtk = false
write_particles = false
```

Required modes:

```text
none
penalty
moving_boundary engineering
moving_boundary link_area_experimental
```

If moving-boundary rows approach density limits, tune only config values:

```text
target_u_lbm = [0.0025, 0.0, 0.0]
mb_force_cap_norm = 5.0e-6
```

Do not change solver formulas.

### 6.3 48^3 `mesh_ellipsoid`

Use:

```text
geometry_type = mesh
geometry_config_path = configs/step20_mesh_ellipsoid_geometry.json
n_grid = 48
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = [0.005, 0.0, 0.0]
mb_force_cap_norm = 1.0e-5
output_interval = 10
write_vtk = false
write_particles = false
```

Required modes:

```text
none
penalty
moving_boundary engineering
moving_boundary link_area_experimental
```

If runtime becomes excessive, `none` may be retained as required in the contract test but run with the same short 10-step window. Do not omit required rows from final artifacts.

### 6.4 64^3 Imported Geometry Feasibility

Use:

```text
n_grid = 64
n_particles = 4096
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
target_u_lbm = [0.0025, 0.0, 0.0]
output_interval = 5
write_vtk = false
write_particles = false
```

Required rows:

```text
voxel_sphere penalty
voxel_sphere moving_boundary engineering
mesh_cube penalty
```

Optional row:

```text
mesh_cube moving_boundary engineering
```

If optional `mesh_cube moving_boundary engineering` fails or is too slow, do not block Step 21. Mark it optional in outputs and report.

## 7. Baseline 1: `voxel_sphere` 48^3 Modes

Script:

```text
baseline_tests/run_step21_voxel_sphere_48_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_voxel_sphere_48_modes.py
```

Required rows:

```text
voxel_sphere / none / engineering
voxel_sphere / penalty / engineering
voxel_sphere / moving_boundary / engineering
voxel_sphere / moving_boundary / link_area_experimental
```

Outputs:

```text
outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv
outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.npz
logs/step21_voxel_sphere_48_modes.log
```

Acceptance:

```text
all four rows stable
n_grid == 48
n_particles == 4096
completed_lbm_steps == 10
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
projected_mass > 0
active_cell_count > 0
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
link_area_experimental area_scale_final finite
```

Final marker:

```text
[OK] Step 21 voxel_sphere 48 modes finished
```

## 8. Baseline 2: `mesh_cube` 48^3 Modes

Script:

```text
baseline_tests/run_step21_mesh_cube_48_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_cube_48_modes.py
```

Required rows:

```text
mesh_cube / none / engineering
mesh_cube / penalty / engineering
mesh_cube / moving_boundary / engineering
mesh_cube / moving_boundary / link_area_experimental
```

Outputs:

```text
outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv
outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.npz
logs/step21_mesh_cube_48_modes.log
```

Acceptance:

```text
all four rows stable
n_grid == 48
n_particles == 4096
completed_lbm_steps == 10
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
projected_mass > 0
active_cell_count > 0
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
link_area_experimental area_scale_final finite
```

Final marker:

```text
[OK] Step 21 mesh_cube 48 modes finished
```

## 9. Baseline 3: `mesh_ellipsoid` 48^3 Modes

Script:

```text
baseline_tests/run_step21_mesh_ellipsoid_48_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_ellipsoid_48_modes.py
```

Required rows:

```text
mesh_ellipsoid / none / engineering
mesh_ellipsoid / penalty / engineering
mesh_ellipsoid / moving_boundary / engineering
mesh_ellipsoid / moving_boundary / link_area_experimental
```

Outputs:

```text
outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv
outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.npz
logs/step21_mesh_ellipsoid_48_modes.log
```

Acceptance:

```text
all four rows stable
n_grid == 48
n_particles == 4096
completed_lbm_steps == 10
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
projected_mass > 0
active_cell_count > 0
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
link_area_experimental area_scale_final finite
```

Final marker:

```text
[OK] Step 21 mesh_ellipsoid 48 modes finished
```

## 10. Baseline 4: Imported Geometry 64^3 Feasibility

Script:

```text
baseline_tests/run_step21_imported_geometry_64_feasibility.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_64_feasibility.py
```

Required rows:

```text
voxel_sphere / penalty / engineering
voxel_sphere / moving_boundary / engineering
mesh_cube / penalty / engineering
```

Optional row:

```text
mesh_cube / moving_boundary / engineering
```

Outputs:

```text
outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv
outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.npz
logs/step21_imported_geometry_64_feasibility.log
```

Acceptance:

```text
required rows stable
n_grid == 64
n_particles == 4096
completed_lbm_steps == 5
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
projected_mass > 0
active_cell_count > 0
no NaN
no Inf
```

Final marker:

```text
[OK] Step 21 imported geometry 64 feasibility finished
```

## 11. Baseline 5: Imported Geometry Projection Quality

Script:

```text
baseline_tests/run_step21_imported_geometry_projection_quality.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_projection_quality.py
```

Required cases:

```text
voxel_sphere
mesh_cube
mesh_ellipsoid
```

Required metrics:

```text
case
geometry_type
particle_count
geometry_volume
particle_mass_sum
projected_mass
relative_mass_error
active_cell_count
solid_phi_min
solid_phi_max
occupied_count_32
occupied_fraction_32
particle_bounds_min_x
particle_bounds_min_y
particle_bounds_min_z
particle_bounds_max_x
particle_bounds_max_y
particle_bounds_max_z
stable
notes
```

Outputs:

```text
outputs/step21_imported_geometry_projection_quality/projection_quality.csv
outputs/step21_imported_geometry_projection_quality/projection_quality.npz
logs/step21_imported_geometry_projection_quality.log
```

Acceptance:

```text
all required cases stable
relative_mass_error finite
relative_mass_error < 1.0e-4
solid_phi finite
0 <= solid_phi_min
solid_phi_max <= 1
active_cell_count > 0
particle bounds inside [0, 1]^3
particle_count == 4096
```

Final marker:

```text
[OK] Step 21 imported geometry projection quality finished
```

## 12. Baseline 6: Imported Geometry Scale Summary

Script:

```text
baseline_tests/run_step21_imported_geometry_scale_summary.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_scale_summary.py
```

Inputs:

```text
outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv
outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv
outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv
outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv
outputs/step21_imported_geometry_projection_quality/projection_quality.csv
```

Outputs:

```text
outputs/step21_imported_geometry_scale_summary/step21_summary.csv
outputs/step21_imported_geometry_scale_summary/step21_summary.json
logs/step21_imported_geometry_scale_summary.log
```

Acceptance:

```text
summary includes all required baseline groups
required row counts match this goal
all required rows stable
global rho_min > 0.95
global rho_max < 1.05
global lbm_max_v < 0.1
global mpm_min_J > 0
projection_quality rows stable
no NaN
no Inf
```

Final marker:

```text
[OK] Step 21 imported geometry scale summary finished
```

## 13. Baseline 7: Artifact Manifest

Script:

```text
baseline_tests/run_step21_artifact_manifest.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_artifact_manifest.py
```

Outputs:

```text
outputs/step21_artifact_manifest/artifact_manifest.csv
outputs/step21_artifact_manifest/artifact_summary.json
logs/step21_artifact_manifest.log
```

Acceptance:

```text
file_count recorded
total_size_bytes recorded
total_size_mb recorded
large_file_count == 0
fixtures remain small
Step 21 driver configs have write_vtk == false
Step 21 driver configs have write_particles == false
no large real geometry artifacts
```

Final marker:

```text
[OK] Step 21 artifact manifest finished
```

## 14. Required Documentation

Create:

```text
docs/20_imported_geometry_scale_validation.md
STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/10_performance_memory.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
```

Required phrases in docs/report:

```text
Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.
Step 21 is synthetic imported geometry scale validation, not real squid validation.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 21 mesh path is not production mesh repair.
```

Forbidden overclaims:

```text
real squid simulation is validated
validated squid swimming
production mesh repair is complete
production-ready mesh import
production-ready sharp-interface FSI
strict momentum-conserving FSI is complete
```

## 15. Step 21 Report Contract

`STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md` must contain:

```text
1. Goal
2. Files created and updated
3. Explicit non-goals
4. Config matrix
5. 48^3 voxel_sphere mode validation
6. 48^3 mesh_cube mode validation
7. 48^3 mesh_ellipsoid mode validation
8. 64^3 imported geometry feasibility
9. Projection quality diagnostics
10. Scale summary
11. Artifact manifest summary
12. Verification commands
13. GitHub sync information
14. Acceptance checklist
15. Decision for Step 22
```

The report must include tables with at least:

```text
case
geometry_type
mode
reaction_transfer_mode
n_grid
particle_count
completed_lbm_steps
projected_mass
active_cell_count
rho_min
rho_max
lbm_max_v
mpm_min_J
cell_force_max_norm
hydro_force_max_norm
area_scale_final
stable
```

## 16. Required Contract Test

Create:

```text
tests/test_step21_imported_geometry_scale_contract.py
```

The contract test must avoid importing heavy optional runtime paths unless it handles missing packages. Prefer file/text/artifact checks for Git pre-push compatibility.

Required file checks:

```python
required_paths = [
    "configs/step21_voxel_sphere_48_none.json",
    "configs/step21_voxel_sphere_48_penalty.json",
    "configs/step21_voxel_sphere_48_moving_boundary.json",
    "configs/step21_voxel_sphere_48_link_area.json",
    "configs/step21_mesh_cube_48_none.json",
    "configs/step21_mesh_cube_48_penalty.json",
    "configs/step21_mesh_cube_48_moving_boundary.json",
    "configs/step21_mesh_cube_48_link_area.json",
    "configs/step21_mesh_ellipsoid_48_none.json",
    "configs/step21_mesh_ellipsoid_48_penalty.json",
    "configs/step21_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step21_mesh_ellipsoid_48_link_area.json",
    "configs/step21_voxel_sphere_64_penalty.json",
    "configs/step21_voxel_sphere_64_moving_boundary.json",
    "configs/step21_mesh_cube_64_penalty.json",
    "baseline_tests/step21_common.py",
    "baseline_tests/run_step21_voxel_sphere_48_modes.py",
    "baseline_tests/run_step21_mesh_cube_48_modes.py",
    "baseline_tests/run_step21_mesh_ellipsoid_48_modes.py",
    "baseline_tests/run_step21_imported_geometry_64_feasibility.py",
    "baseline_tests/run_step21_imported_geometry_projection_quality.py",
    "baseline_tests/run_step21_imported_geometry_scale_summary.py",
    "baseline_tests/run_step21_artifact_manifest.py",
    "docs/20_imported_geometry_scale_validation.md",
    "STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md",
]
```

Required log markers:

```text
[OK] Step 21 voxel_sphere 48 modes finished
[OK] Step 21 mesh_cube 48 modes finished
[OK] Step 21 mesh_ellipsoid 48 modes finished
[OK] Step 21 imported geometry 64 feasibility finished
[OK] Step 21 imported geometry projection quality finished
[OK] Step 21 imported geometry scale summary finished
[OK] Step 21 artifact manifest finished
```

Required artifact checks:

```text
voxel_sphere_48_results.csv contains none / penalty / moving_boundary engineering / link_area_experimental
mesh_cube_48_results.csv contains none / penalty / moving_boundary engineering / link_area_experimental
mesh_ellipsoid_48_results.csv contains none / penalty / moving_boundary engineering / link_area_experimental
imported_geometry_64_results.csv contains required 64^3 feasibility rows
projection_quality.csv contains voxel_sphere / mesh_cube / mesh_ellipsoid
all required rows stable
all required rows finite
artifact large_file_count == 0
logs/step21_pytest.log exists
```

Required source text checks:

```text
default reaction_transfer_mode remains engineering
link_area_experimental remains opt-in
coupler source files do not gain Step 21 formula changes
external/taichi_LBM3D unchanged
```

## 17. Required Execution Order

Follow this sequence:

1. Re-read this goal file and inspect current `main`.
2. Confirm `external/taichi_LBM3D` is clean.
3. Add `tests/test_step21_imported_geometry_scale_contract.py` first and run it to confirm RED.
4. Add Step 21 configs.
5. Add `baseline_tests/step21_common.py`.
6. Add and run `run_step21_voxel_sphere_48_modes.py`.
7. Add and run `run_step21_mesh_cube_48_modes.py`.
8. Add and run `run_step21_mesh_ellipsoid_48_modes.py`.
9. Add and run `run_step21_imported_geometry_64_feasibility.py`.
10. Add and run `run_step21_imported_geometry_projection_quality.py`.
11. Add and run `run_step21_imported_geometry_scale_summary.py`.
12. Add and run `run_step21_artifact_manifest.py`.
13. Update docs and `STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md`.
14. Run full `pytest -q` and save `logs/step21_pytest.log`.
15. Regenerate artifact manifest after pytest log exists.
16. Run final `pytest -q`.
17. Run `git diff --check`.
18. Confirm `git status --short external/taichi_LBM3D` is empty.
19. Commit all Step 21 code/docs/logs/outputs/report.
20. Push to GitHub `origin/main`.
21. Report commit hash, branch, verification commands, and key baseline numbers.

## 18. Required Commands

Use this interpreter unless unavailable:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore ...
```

Run baselines:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_voxel_sphere_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_cube_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_ellipsoid_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_projection_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_scale_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_artifact_manifest.py
```

Save logs with UTF-8 encoding. In Windows PowerShell, prefer:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_voxel_sphere_48_modes.py 2>&1 | Out-File -FilePath logs\step21_voxel_sphere_48_modes.log -Encoding utf8
```

Run pytest and save the required log:

```powershell
Set-Content -Path logs\step21_pytest.log -Value 'pytest started' -Encoding utf8
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q 2>&1 | Out-File -FilePath logs\step21_pytest.log -Encoding utf8
```

Also ensure Git pre-push hook compatibility. If the hook uses a different Python and fails due to test import environment, fix the contract test so it can run without importing optional runtime packages.

## 19. Hard Acceptance Checklist

All items must be true before Step 21 is complete:

```text
[ ] main is on the Step 21 final commit
[ ] voxel_sphere 48^3 modes baseline passes
[ ] mesh_cube 48^3 modes baseline passes
[ ] mesh_ellipsoid 48^3 modes baseline passes
[ ] imported geometry 64^3 feasibility passes
[ ] imported geometry projection quality passes
[ ] imported geometry scale summary passes
[ ] artifact manifest passes
[ ] none / penalty / moving_boundary engineering / link_area_experimental mode boundaries are clear
[ ] penalty rows cell_force_max_norm > 0
[ ] moving_boundary rows cell_force_max_norm == 0
[ ] moving_boundary rows bb_link_count > 0
[ ] link_area rows area_scale_final finite
[ ] rho_min > 0.95 for all required stable rows
[ ] rho_max < 1.05 for all required stable rows
[ ] lbm_max_v < 0.1 for all required stable rows
[ ] mpm_min_J > 0 for all required stable rows
[ ] mpm_max_speed < 10 for all required stable rows
[ ] projected_mass > 0 for all required rows
[ ] active_cell_count > 0 for all required rows
[ ] projection quality relative_mass_error < 1.0e-4
[ ] no NaN
[ ] no Inf
[ ] no FSI formula changes
[ ] default reaction_transfer_mode remains engineering
[ ] link_area_experimental remains opt-in
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no squid swimming validation claims
[ ] no production mesh repair claims
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count == 0
[ ] docs/20_imported_geometry_scale_validation.md exists
[ ] STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md complete
[ ] tests/test_step21_imported_geometry_scale_contract.py exists
[ ] logs/step21_pytest.log exists
[ ] pytest -q passes
[ ] Git pre-push pytest hook passes
[ ] git diff --check passes
[ ] Step 21 artifacts are committed
[ ] Step 21 artifacts are pushed to GitHub origin/main
```

## 20. Failure Handling

If a 48^3 imported geometry mode fails:

1. Do not claim Step 21 complete.
2. Inspect density bounds, max velocity, MPM `J`, projected mass, and active cell count.
3. Tune config values only before changing code.
4. Prefer lower `target_u_lbm`, lower `mb_force_cap_norm`, or shorter accepted Step 21 windows only if the report clearly records the final baseline settings.
5. Do not change coupling formulas to make a case pass.

If a `link_area_experimental` row fails:

1. Preserve engineering rows.
2. Inspect `area_scale`, `raw_area_scale`, active reaction count, and hydro force diagnostics.
3. Keep `link_area_experimental` opt-in.
4. Do not change default reaction transfer mode.

If a 64^3 feasibility row fails:

1. Keep 48^3 validation artifacts intact.
2. Reduce `target_u_lbm` before changing any code.
3. Keep `write_vtk = false` and `write_particles = false`.
4. Do not replace a failed required row with an optional row.

If projection quality fails:

1. Inspect particle mass sum, projected mass, solid_phi bounds, and particle bounds.
2. Do not replace imported geometry with procedural geometry while claiming success.
3. Keep fixture files small.

If artifact size grows too much:

1. Disable heavy exports.
2. Remove scratch outputs from the committed artifact set.
3. Do not commit large real geometry.

If `external/taichi_LBM3D` is modified:

```text
Step 21 is not complete.
```

Revert only unintended external edits made by this task. Never revert unrelated user changes without permission.

## 21. Completion Definition

Step 21 is complete only when:

1. All required source files exist.
2. All Step 21 configs exist.
3. `voxel_sphere` 48^3 mode validation passes.
4. `mesh_cube` 48^3 mode validation passes.
5. `mesh_ellipsoid` 48^3 mode validation passes.
6. Required 64^3 imported geometry feasibility rows pass.
7. Projection quality diagnostics pass.
8. Scale summary exists and marks all required rows stable.
9. Artifact manifest exists and reports `large_file_count == 0`.
10. `pytest -q` passes.
11. Git pre-push pytest hook passes.
12. `logs/step21_pytest.log` exists and records passing pytest.
13. Documentation and report are complete and avoid forbidden overclaims.
14. `external/taichi_LBM3D` remains unchanged.
15. Step 21 code/docs/logs/outputs/report are committed.
16. The commit is pushed to GitHub `origin/main`.
17. The final response reports the commit hash and remote branch.

## 22. Decision After Step 21

If Step 21 passes, the recommended Step 22 is:

```text
Step 22: Geometry quality checks and import robustness
```

Reason:

Step 21 should prove that small synthetic imported voxel/mesh geometry scales from 32^3 smoke baselines to 48^3 mode validation and 64^3 feasibility. Before real squid geometry work, the next risk is geometry quality:

```text
watertightness checks
normal/orientation checks
mesh bounds checks
voxel resolution sensitivity
mesh-to-voxel fallback diagnostics
failure reporting for bad geometry files
artifact policy for larger geometry experiments
```

Do not proceed to real squid validation until imported geometry quality checks, scale behavior, and artifact policy are stable.

## 23. Paste-Ready Compact Goal

Use this compact `/goal` text to execute Step 21:

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 21: Imported geometry scale validation. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP21_IMPORTED_GEOMETRY_SCALE_GOAL.md.

Goal: carry Step 20 synthetic imported voxel/mesh geometries from 32^3 smoke validation to 48^3 mode validation and 64^3 feasibility, add projection quality diagnostics, scale summaries, artifact manifest, docs, tests, logs, outputs, report, and GitHub sync.

Hard boundaries: do not add new FSI physics, do not change PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, LinkAreaMovingBoundaryCoupler3D, moving bounce-back formula, LBM step formulas, default reaction_transfer_mode=engineering, or opt-in link_area_experimental behavior. Do not add two-phase flow, contact angle physics, squid actuation/swimming, real squid validation claims, production mesh repair claims, sparse storage, ReducedSquidFSI, large real geometry artifacts, or edits to external/taichi_LBM3D.

Required configs, baselines, diagnostics, execution order, pytest contract, acceptance checklist, failure handling, completion definition, and GitHub sync requirements are all defined in STEP21_IMPORTED_GEOMETRY_SCALE_GOAL.md. Finish only after all Step 21 baselines pass, pytest passes, Git pre-push pytest hook passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/outputs/report are committed and pushed to GitHub origin/main.
```
