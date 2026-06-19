# Step 20 Goal: Mesh / Voxel Geometry Import Pipeline

This file is the authoritative execution contract for Step 20 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 20 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 20

Step 19 is accepted on GitHub at commit:

```text
37483708b056a30c45208cfc3fa6e33d245b3d45
```

Step 19 established:

- `link_area_experimental` long-window validation for 48^3 box;
- `link_area_experimental` long-window validation for 48^3 procedural `squid_proxy`;
- conservative 64^3 `link_area_experimental` feasibility;
- 64^3 engineering-vs-link-area comparison;
- 48^3 long engineering-vs-link-area comparison;
- Step 18 regression;
- area_scale drift diagnostics;
- summary artifacts;
- artifact manifest with `large_file_count = 0`;
- `pytest -q`: 133 passed;
- Git pre-push hook: 133 passed;
- `external/taichi_LBM3D` unchanged.

Step 19 documents that:

- the default `reaction_transfer_mode` remains `engineering`;
- the moving bounce-back formula is unchanged;
- `LinkAreaMovingBoundaryCoupler3D` formula is unchanged;
- `MovingBoundaryFSICoupler3D` is unchanged;
- the link-area transfer remains experimental;
- `squid_proxy` is procedural and not real squid validation;
- this is not final strict momentum-conserving sharp-interface FSI.

Step 20 must preserve all of the above.

## 2. Step 20 Objective

Build a reproducible, testable, artifact-controlled geometry import pipeline that moves the project from procedural-only geometry toward external geometry input.

Step 20 must add:

1. Small voxel geometry import.
2. Small synthetic mesh geometry import.
3. Geometry normalization into the normalized cubic domain.
4. Imported-geometry MPM particle cloud generation.
5. Imported-geometry LBM projection diagnostics.
6. `GeometryConfig`, `GeometrySampler3D`, `FSIDriverConfig`, and `FSIDriver3D` integration for imported geometry.
7. Small synthetic mesh and voxel fixtures.
8. Baseline scripts and outputs proving imported geometry works.
9. Documentation, report, contract test, logs, and artifact manifest.
10. GitHub sync to `origin/main`.

Step 20 must not claim real squid validation. Correct wording:

```text
geometry import pipeline
synthetic mesh import
synthetic voxel import
real-geometry-ready scaffold
```

Step 20 should prepare the project for future real geometry, not validate a real squid.

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
- no sparse storage;
- no `ReducedSquidFSI`;
- no large mesh artifacts;
- no large VTK/particle artifacts for Step 20;
- no edits to `external/taichi_LBM3D`.

Allowed work:

- small synthetic voxel fixtures;
- small synthetic OBJ mesh fixtures;
- import utilities;
- geometry normalization;
- voxel occupancy loading and diagnostics;
- minimal OBJ loading;
- small synthetic mesh inside/voxelization path;
- imported geometry particle sampling;
- imported geometry projection diagnostics;
- 32^3 driver smoke baselines;
- docs, tests, logs, outputs, and report.

## 4. Required Design

Current geometry support is:

```text
box
ellipsoid
squid_proxy
```

Step 20 must add:

```text
voxel
mesh
```

Keep `FSIDriver3D` integration through the existing pattern:

```text
FSIDriverConfig.geometry_type
FSIDriverConfig.geometry_config_path
GeometryConfig.from_json()
GeometrySampler3D(...).sample_particles()
MPMSolid3D.init_from_numpy(...)
MPMToLBMProjector3D.project(...)
```

Do not add a separate driver path for imported geometry.

Do not change coupling logic. Imported geometry should only affect the initial solid particle cloud and diagnostic/projection occupancy.

## 5. GeometryConfig Contract

Update:

```text
src/geometry_config.py
```

Add `voxel` and `mesh` to `VALID_GEOMETRY_TYPES`.

Add fields:

```python
geometry_file: Optional[str] = None
metadata_file: Optional[str] = None
normalize_to_domain: bool = True
preserve_aspect_ratio: bool = True
padding: float = 0.05
voxel_threshold: float = 0.5
voxel_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
mesh_inside_method: str = "ray_cast"
mesh_voxel_resolution: int = 32
```

Validation requirements:

```text
geometry_type == "voxel" requires geometry_file
geometry_type == "mesh" requires geometry_file
padding >= 0
padding < 0.5
voxel_threshold finite
voxel_spacing values positive
mesh_inside_method in {"ray_cast", "voxelized"}
mesh_voxel_resolution > 0
geometry_file path must be relative to repo root or absolute
metadata_file path must be relative to repo root or absolute
```

Tuple fields must round-trip through `to_dict()` as JSON lists.

## 6. Required Source Files

Create:

```text
src/voxel_io.py
src/mesh_io.py
src/geometry_import.py
```

Update:

```text
src/geometry_config.py
src/geometry.py
src/fsi_config.py
src/fsi_driver.py
src/__init__.py
```

Only update `fsi_config.py` / `fsi_driver.py` as needed to accept the new geometry types through the existing config path. Do not change any FSI update formulas.

## 7. `src/voxel_io.py` Contract

Implement small voxel geometry I/O utilities.

Required public surface:

```python
class VoxelGeometry:
    ...

def load_voxel_geometry(path, metadata_path=None, threshold=0.5):
    ...

def save_voxel_geometry(path, occupancy, metadata_path=None, metadata=None):
    ...

def voxel_centers_to_points(occupancy, domain_min=(0, 0, 0), domain_max=(1, 1, 1)):
    ...
```

Input support:

- `.npy` occupancy arrays only for Step 20 hard requirement;
- optional JSON metadata.

Validation:

```text
occupancy must be 3D
occupancy must be finite
occupancy may be bool, integer, or float
threshold converts numeric arrays to bool occupancy
occupied_count > 0
occupied_fraction > 0
metadata JSON must be valid if provided
```

Required stats:

```text
shape
occupied_count
occupied_fraction
bounds_index_min
bounds_index_max
domain_min
domain_max
voxel_order
```

Metadata schema for fixture:

```json
{
  "source": "synthetic",
  "description": "small voxel sphere fixture",
  "domain_min": [0.0, 0.0, 0.0],
  "domain_max": [1.0, 1.0, 1.0],
  "voxel_order": "ijk"
}
```

## 8. `src/mesh_io.py` Contract

Implement a minimal ASCII OBJ parser for small synthetic fixtures.

Required public surface:

```python
def load_obj(path):
    ...

def write_obj(path, vertices, faces):
    ...

def mesh_bounds(vertices):
    ...

def normalize_vertices(
    vertices,
    domain_min=(0, 0, 0),
    domain_max=(1, 1, 1),
    padding=0.05,
    preserve_aspect_ratio=True,
):
    ...
```

Supported OBJ features:

```text
v x y z
f i j k
f i j k l
comments
blank lines
1-based positive OBJ indices
slash-separated face tokens such as f 1/1/1 2/2/2 3/3/3
```

Quad faces must be triangulated into two triangles.

Not supported in Step 20:

```text
materials
textures
normal dependency
non-manifold repair
negative OBJ indices
arbitrary production mesh cleanup
```

Validation:

```text
vertices shape == (n, 3)
faces shape == (m, 3)
n > 0
m > 0
all values finite
face indices in range
normalized bounds inside [0, 1]^3
```

## 9. `src/geometry_import.py` Contract

Create an imported geometry helper used by `GeometrySampler3D`.

Required public surface may be:

```python
class ImportedGeometrySampler3D:
    def __init__(self, config):
        ...

    def inside(self, points):
        ...

    def voxelize(self, n_grid):
        ...

    def sample_particles(self):
        ...

    def get_stats(self):
        ...
```

Alternative names are acceptable if the public behavior is equivalent and documented.

Voxel inside test:

```text
points in normalized domain
idx = floor((points - domain_min) / domain_span * voxel_shape)
clip to valid range
inside = occupancy[idx_i, idx_j, idx_k]
```

Mesh inside test:

- Use a simple CPU ray-casting or mesh-to-voxel path.
- The hard requirement is only for small synthetic watertight fixtures.
- Document that this is not production mesh repair.

Sampling:

```text
structured deterministic candidate points over [0, 1]^3
inside mask from voxel or mesh
select deterministic subset
vol0 = estimated_geometry_volume / n_particles
mass = vol0 * p_rho
```

Required stats:

```text
geometry_type
source_file
candidate_resolution
candidate_count
accepted_count
particle_count
geometry_volume
deterministic
imported_geometry_note
```

## 10. GeometrySampler3D Integration

Update:

```text
src/geometry.py
```

`GeometrySampler3D.inside()` must support:

```text
voxel
mesh
```

`GeometrySampler3D.sample_particles()` and `GeometrySampler3D.voxelize()` must work for imported geometries.

Acceptable implementation:

```python
if self.config.geometry_type in {"voxel", "mesh"}:
    return ImportedGeometrySampler3D(self.config).inside(points)
```

Avoid repeatedly reloading large data in tight loops. Since Step 20 fixtures are small, a simple cached helper inside `GeometrySampler3D` is acceptable.

## 11. FSIDriver Integration

`FSIDriverConfig.geometry_type` must accept:

```text
voxel
mesh
```

`FSIDriver3D._make_geometry_config()` must continue to enforce:

```text
geometry_config_path geometry_type == FSIDriverConfig.geometry_type
geometry_config_path n_particles == FSIDriverConfig.n_particles
```

Do not add new coupling modes.

Driver imported geometry baselines must run through normal `FSIDriver3D`.

## 12. Required Fixture Files

Create:

```text
data/geometry_fixtures/README.md
data/geometry_fixtures/cube.obj
data/geometry_fixtures/ellipsoid_proxy.obj
data/geometry_fixtures/voxel_sphere.npy
data/geometry_fixtures/voxel_sphere_metadata.json
```

Fixture rules:

```text
voxel_sphere.npy shape should be 32 x 32 x 32
cube.obj should be 8 vertices and 12 triangles
ellipsoid_proxy.obj should be small, preferably < 250 vertices and < 500 triangles
all fixture files should be small
do not commit large real geometry
do not commit large scans
do not commit large VTK outputs
```

The fixtures may be generated by a script if the final files are committed and deterministic.

## 13. Required Config Files

Create:

```text
configs/step20_voxel_sphere_geometry.json
configs/step20_mesh_cube_geometry.json
configs/step20_mesh_ellipsoid_geometry.json
configs/step20_driver_voxel_penalty.json
configs/step20_driver_mesh_moving_boundary.json
```

### 13.1 `configs/step20_voxel_sphere_geometry.json`

Required effective settings:

```json
{
  "geometry_type": "voxel",
  "n_particles": 4096,
  "geometry_file": "data/geometry_fixtures/voxel_sphere.npy",
  "metadata_file": "data/geometry_fixtures/voxel_sphere_metadata.json",
  "voxel_threshold": 0.5,
  "p_rho": 1.0,
  "deterministic": true
}
```

### 13.2 `configs/step20_mesh_cube_geometry.json`

Required effective settings:

```json
{
  "geometry_type": "mesh",
  "n_particles": 4096,
  "geometry_file": "data/geometry_fixtures/cube.obj",
  "mesh_inside_method": "ray_cast",
  "mesh_voxel_resolution": 32,
  "normalize_to_domain": true,
  "preserve_aspect_ratio": true,
  "padding": 0.05,
  "p_rho": 1.0,
  "deterministic": true
}
```

### 13.3 `configs/step20_mesh_ellipsoid_geometry.json`

Required effective settings:

```json
{
  "geometry_type": "mesh",
  "n_particles": 4096,
  "geometry_file": "data/geometry_fixtures/ellipsoid_proxy.obj",
  "mesh_inside_method": "ray_cast",
  "mesh_voxel_resolution": 32,
  "normalize_to_domain": true,
  "preserve_aspect_ratio": true,
  "padding": 0.05,
  "p_rho": 1.0,
  "deterministic": true
}
```

### 13.4 Driver Configs

Driver configs must use small 32^3 runs and must disable heavy outputs:

```json
{
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "write_vtk": false,
  "write_particles": false
}
```

`step20_driver_voxel_penalty.json` must use:

```text
coupling_mode = "penalty"
geometry_type = "voxel"
geometry_config_path = "configs/step20_voxel_sphere_geometry.json"
```

`step20_driver_mesh_moving_boundary.json` must use:

```text
coupling_mode = "moving_boundary"
reaction_transfer_mode = "engineering"
geometry_type = "mesh"
geometry_config_path = "configs/step20_mesh_cube_geometry.json"
```

## 14. Required Baseline Scripts

Create:

```text
baseline_tests/step20_common.py
baseline_tests/run_step20_voxel_import_sanity.py
baseline_tests/run_step20_mesh_import_sanity.py
baseline_tests/run_step20_imported_geometry_projection.py
baseline_tests/run_step20_driver_imported_geometry_modes.py
baseline_tests/run_step20_artifact_manifest.py
```

All scripts must:

- use deterministic inputs;
- write under `outputs/step20_*`;
- save logs under `logs/step20_*.log` when run through acceptance commands;
- raise on NaN or Inf;
- raise on missing output files;
- raise on threshold failures;
- print a final `[OK] ... finished` marker.

## 15. Baseline 1: Voxel Import Sanity

Script:

```text
baseline_tests/run_step20_voxel_import_sanity.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
```

Inputs:

```text
configs/step20_voxel_sphere_geometry.json
data/geometry_fixtures/voxel_sphere.npy
data/geometry_fixtures/voxel_sphere_metadata.json
```

Outputs:

```text
outputs/step20_voxel_import_sanity/particles_x.npy
outputs/step20_voxel_import_sanity/particle_vol0.npy
outputs/step20_voxel_import_sanity/particle_mass.npy
outputs/step20_voxel_import_sanity/geometry_occupancy.npy
outputs/step20_voxel_import_sanity/import_stats.json
logs/step20_voxel_import_sanity.log
```

Acceptance:

```text
voxel shape == [32, 32, 32]
occupied_count > 0
occupied_fraction > 0
particle_count == 4096
positions finite
all positions inside [0, 1]^3
vol0 positive
mass positive
geometry_volume > 0
```

Final marker:

```text
[OK] Step 20 voxel import sanity finished
```

## 16. Baseline 2: Mesh Import Sanity

Script:

```text
baseline_tests/run_step20_mesh_import_sanity.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
```

Inputs:

```text
data/geometry_fixtures/cube.obj
data/geometry_fixtures/ellipsoid_proxy.obj
configs/step20_mesh_cube_geometry.json
configs/step20_mesh_ellipsoid_geometry.json
```

Outputs:

```text
outputs/step20_mesh_import_sanity/cube_particles_x.npy
outputs/step20_mesh_import_sanity/ellipsoid_particles_x.npy
outputs/step20_mesh_import_sanity/mesh_import_stats.json
logs/step20_mesh_import_sanity.log
```

Acceptance:

```text
vertices_count > 0
faces_count > 0
normalized bounds inside [0, 1]^3
particle_count == 4096 for each case
voxel occupied_count > 0 for each case
positions finite
vol0 positive
mass positive
```

Final marker:

```text
[OK] Step 20 mesh import sanity finished
```

## 17. Baseline 3: Imported Geometry Projection

Script:

```text
baseline_tests/run_step20_imported_geometry_projection.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
```

Required cases:

```text
voxel_sphere
mesh_cube
mesh_ellipsoid
```

Outputs:

```text
outputs/step20_imported_geometry_projection/projection_results.csv
outputs/step20_imported_geometry_projection/projection_results.npz
outputs/step20_imported_geometry_projection/<case>/solid_phi.npy
outputs/step20_imported_geometry_projection/<case>/particles_x.npy
logs/step20_imported_geometry_projection.log
```

Acceptance:

```text
all cases projected_mass > 0
all cases active_cell_count > 0
solid_phi finite
0 <= solid_phi <= 1
cell_force_max_norm == 0
hydro_force_max_norm == 0
particle positions finite
```

Final marker:

```text
[OK] Step 20 imported geometry projection finished
```

## 18. Baseline 4: Driver Imported Geometry Modes

Script:

```text
baseline_tests/run_step20_driver_imported_geometry_modes.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
```

Required rows:

```text
voxel_sphere / none
voxel_sphere / penalty
mesh_cube / none
mesh_cube / penalty
mesh_cube / moving_boundary engineering
```

Optional row if stable without extra work:

```text
mesh_cube / moving_boundary link_area_experimental
```

Baseline settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
target_u_lbm = [0.005, 0.0, 0.0]
write_vtk = false
write_particles = false
```

Outputs:

```text
outputs/step20_driver_imported_geometry_modes/imported_geometry_mode_results.csv
outputs/step20_driver_imported_geometry_modes/imported_geometry_mode_results.npz
logs/step20_driver_imported_geometry_modes.log
```

Acceptance:

```text
required rows stable
rho_min > 0.95 for stable driver rows
rho_max < 1.05 for stable driver rows
lbm_max_v < 0.1 for stable driver rows
mpm_min_J > 0
mpm_max_speed < 10
active_cell_count > 0
projected_mass > 0
moving_boundary rows keep cell_force_max_norm == 0
penalty rows have finite cell_force_max_norm
no NaN
no Inf
```

Do not run 48^3 or 64^3 for Step 20. This step is geometry import, not scale validation.

Final marker:

```text
[OK] Step 20 driver imported geometry modes finished
```

## 19. Baseline 5: Artifact Manifest

Script:

```text
baseline_tests/run_step20_artifact_manifest.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_artifact_manifest.py
```

Outputs:

```text
outputs/step20_artifact_manifest/artifact_manifest.csv
outputs/step20_artifact_manifest/artifact_summary.json
logs/step20_artifact_manifest.log
```

Acceptance:

```text
file_count recorded
total_size_bytes recorded
total_size_mb recorded
large_file_count == 0
fixture files are small
Step 20 driver configs have write_vtk == false
Step 20 driver configs have write_particles == false
```

Final marker:

```text
[OK] Step 20 artifact manifest finished
```

## 20. Required Documentation

Create:

```text
docs/19_geometry_import_pipeline.md
STEP20_GEOMETRY_IMPORT_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/12_geometry_ingestion.md
docs/18_link_area_long_run.md
```

Required phrases in docs/report:

```text
Step 20 adds a small synthetic mesh and voxel geometry import pipeline.
Step 20 is a geometry-ingestion scaffold, not real squid validation.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D.
The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair.
```

Forbidden overclaims:

```text
real squid simulation is validated
validated squid swimming
production mesh repair
production-ready mesh import
production-ready sharp-interface FSI
strict momentum-conserving FSI is complete
```

## 21. Step 20 Report Contract

`STEP20_GEOMETRY_IMPORT_REPORT.md` must contain:

```text
1. Goal
2. Files created and updated
3. Explicit non-goals
4. GeometryConfig and sampler integration
5. Voxel import sanity result
6. Mesh import sanity result
7. Imported geometry projection result
8. Driver imported geometry modes result
9. Artifact manifest summary
10. Verification commands
11. GitHub sync information
12. Acceptance checklist
13. Decision for Step 21
```

The report must include tables for:

```text
case
geometry_type
particle_count
occupied_count
projected_mass
active_cell_count
rho_min
rho_max
lbm_max_v
mpm_min_J
cell_force_max_norm
stable
```

## 22. Required Contract Test

Create:

```text
tests/test_step20_geometry_import_contract.py
```

The contract test must avoid importing heavy optional runtime paths unless it handles missing packages. Prefer file/text/artifact checks for Git pre-push compatibility.

Required file checks:

```python
required_paths = [
    "src/voxel_io.py",
    "src/mesh_io.py",
    "src/geometry_import.py",
    "data/geometry_fixtures/README.md",
    "data/geometry_fixtures/cube.obj",
    "data/geometry_fixtures/ellipsoid_proxy.obj",
    "data/geometry_fixtures/voxel_sphere.npy",
    "data/geometry_fixtures/voxel_sphere_metadata.json",
    "configs/step20_voxel_sphere_geometry.json",
    "configs/step20_mesh_cube_geometry.json",
    "configs/step20_mesh_ellipsoid_geometry.json",
    "configs/step20_driver_voxel_penalty.json",
    "configs/step20_driver_mesh_moving_boundary.json",
    "baseline_tests/step20_common.py",
    "baseline_tests/run_step20_voxel_import_sanity.py",
    "baseline_tests/run_step20_mesh_import_sanity.py",
    "baseline_tests/run_step20_imported_geometry_projection.py",
    "baseline_tests/run_step20_driver_imported_geometry_modes.py",
    "baseline_tests/run_step20_artifact_manifest.py",
    "docs/19_geometry_import_pipeline.md",
    "STEP20_GEOMETRY_IMPORT_REPORT.md",
]
```

Required log markers:

```text
[OK] Step 20 voxel import sanity finished
[OK] Step 20 mesh import sanity finished
[OK] Step 20 imported geometry projection finished
[OK] Step 20 driver imported geometry modes finished
[OK] Step 20 artifact manifest finished
```

Required artifact checks:

```text
voxel_sphere.npy shape == (32, 32, 32)
OBJ fixture files are small
projection_results.csv all required rows stable
driver mode results all required rows stable
artifact large_file_count == 0
logs/step20_pytest.log exists
```

Required source text checks:

```text
VALID_GEOMETRY_TYPES includes voxel and mesh
GeometrySampler3D supports voxel and mesh
FSIDriverConfig accepts imported geometry through geometry_type
default reaction_transfer_mode remains engineering
coupler source files do not gain Step 20 formula changes
```

## 23. Required Execution Order

Follow this sequence:

1. Re-read this goal file and inspect current `main`.
2. Confirm `external/taichi_LBM3D` is clean.
3. Add `tests/test_step20_geometry_import_contract.py` first and run it to confirm RED.
4. Add `GeometryConfig` fields and validations.
5. Add `src/voxel_io.py`.
6. Add deterministic voxel fixture.
7. Add `src/mesh_io.py`.
8. Add deterministic OBJ fixtures.
9. Add `src/geometry_import.py`.
10. Integrate imported geometry into `GeometrySampler3D`.
11. Integrate imported geometry into `FSIDriverConfig` / `FSIDriver3D` only through existing geometry config flow.
12. Add Step 20 configs.
13. Add Step 20 common helpers and baseline runners.
14. Run voxel import sanity.
15. Run mesh import sanity.
16. Run imported geometry projection.
17. Run driver imported geometry modes.
18. Run artifact manifest.
19. Update docs and `STEP20_GEOMETRY_IMPORT_REPORT.md`.
20. Run full `pytest -q` and save `logs/step20_pytest.log`.
21. Regenerate artifact manifest after pytest log exists.
22. Run final `pytest -q`.
23. Run `git diff --check`.
24. Confirm `git status --short external/taichi_LBM3D` is empty.
25. Commit all Step 20 code/docs/logs/outputs/report.
26. Push to GitHub `origin/main`.
27. Report commit hash, branch, verification commands, and key baseline numbers.

## 24. Required Commands

Use this interpreter unless unavailable:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore ...
```

Run baselines:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_artifact_manifest.py
```

Save logs with UTF-8 encoding. In Windows PowerShell, prefer:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py 2>&1 | Out-File -FilePath logs\step20_voxel_import_sanity.log -Encoding utf8
```

Run pytest and save the required log:

```powershell
Set-Content -Path logs\step20_pytest.log -Value 'pytest started' -Encoding utf8
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q 2>&1 | Out-File -FilePath logs\step20_pytest.log -Encoding utf8
```

Also ensure Git pre-push hook compatibility. If the hook uses a different Python and fails due to test import environment, fix the contract test so it can run without importing optional runtime packages.

## 25. Hard Acceptance Checklist

All items must be true before Step 20 is complete:

```text
[ ] main is on the Step 20 final commit
[ ] geometry_type supports voxel
[ ] geometry_type supports mesh
[ ] src/voxel_io.py exists
[ ] src/mesh_io.py exists
[ ] src/geometry_import.py exists
[ ] data/geometry_fixtures/README.md exists
[ ] voxel_sphere.npy exists and is small
[ ] cube.obj exists and is small
[ ] ellipsoid_proxy.obj exists and is small
[ ] configs/step20_voxel_sphere_geometry.json exists
[ ] configs/step20_mesh_cube_geometry.json exists
[ ] configs/step20_mesh_ellipsoid_geometry.json exists
[ ] configs/step20_driver_voxel_penalty.json exists
[ ] configs/step20_driver_mesh_moving_boundary.json exists
[ ] voxel import sanity passes
[ ] mesh import sanity passes
[ ] imported geometry projection passes
[ ] driver imported geometry modes pass
[ ] imported geometry particle positions are finite
[ ] imported geometry particle positions are inside [0, 1]^3
[ ] imported geometry vol0 values are positive
[ ] imported geometry mass values are positive
[ ] projected_mass > 0 for projection rows
[ ] active_cell_count > 0 for projection rows
[ ] rho_min > 0.95 for required stable driver rows
[ ] rho_max < 1.05 for required stable driver rows
[ ] lbm_max_v < 0.1 for required stable driver rows
[ ] mpm_min_J > 0 for required stable driver rows
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
[ ] docs/19_geometry_import_pipeline.md exists
[ ] STEP20_GEOMETRY_IMPORT_REPORT.md complete
[ ] tests/test_step20_geometry_import_contract.py exists
[ ] logs/step20_pytest.log exists
[ ] pytest -q passes
[ ] Git pre-push pytest hook passes
[ ] git diff --check passes
[ ] Step 20 artifacts are committed
[ ] Step 20 artifacts are pushed to GitHub origin/main
```

## 26. Failure Handling

If voxel import fails:

1. Do not proceed to mesh import.
2. Inspect occupancy shape, threshold, metadata paths, and occupied_count.
3. Keep fixtures small.
4. Do not replace voxel import with procedural geometry while claiming success.

If mesh import fails:

1. First inspect OBJ parsing and face triangulation.
2. Then inspect normalization bounds.
3. Then inspect inside-test robustness for the small synthetic fixture.
4. If ray casting is unreliable, use a documented mesh-to-voxel fallback for Step 20.
5. Do not claim arbitrary production mesh support.

If driver imported geometry mode becomes unstable:

1. Keep the import baselines intact.
2. Reduce `target_u_lbm`.
3. Reduce step count only if the report clearly marks Step 20 incomplete.
4. Do not change coupling formulas.

If fixture or output artifacts are too large:

1. Reduce fixture resolution.
2. Disable heavy exports.
3. Do not commit large real geometry.

If `external/taichi_LBM3D` is modified:

```text
Step 20 is not complete.
```

Revert only unintended external edits made by this task. Never revert unrelated user changes without permission.

## 27. Completion Definition

Step 20 is complete only when:

1. All required source files exist.
2. `voxel` and `mesh` are valid geometry types.
3. Small voxel and mesh fixtures are committed.
4. Voxel import sanity passes.
5. Mesh import sanity passes.
6. Imported geometry projection passes.
7. Driver imported geometry mode baseline passes.
8. Artifact manifest exists and reports `large_file_count == 0`.
9. `pytest -q` passes.
10. Git pre-push pytest hook passes.
11. `logs/step20_pytest.log` exists and records the passing pytest result.
12. Documentation and report are complete and avoid forbidden overclaims.
13. `external/taichi_LBM3D` remains unchanged.
14. Step 20 code/docs/logs/outputs/report are committed.
15. The commit is pushed to GitHub `origin/main`.
16. The final response reports the commit hash and remote branch.

## 28. Decision After Step 20

If Step 20 passes, the recommended Step 21 is:

```text
Step 21: Imported geometry scale validation
```

Reason: Step 20 should prove 32^3 imported geometry works. Step 21 should then take the small imported voxel/mesh cases to larger validation windows, such as 48^3, across:

```text
none
penalty
moving_boundary engineering
moving_boundary link_area_experimental
```

Do not proceed to real squid validation until imported geometry quality checks, scaling behavior, and artifact policy are stable.
