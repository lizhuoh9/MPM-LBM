# Step 13 Goal: Geometry Ingestion and Squid Proxy Geometry

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 13: Geometry ingestion and squid proxy geometry. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP13_GEOMETRY_INGESTION_GOAL.md.

Goal: without changing FSI physics or Step 10/12 validated behavior, add a reproducible procedural geometry ingestion layer for the current MPM-LBM FSI prototype. Add analytic geometry primitives, deterministic MPM particle-cloud sampling, geometry voxel diagnostics, squid_proxy procedural geometry, FSIDriver3D geometry_type support, Step 13 baselines, docs, report, logs, outputs, and a pytest contract. Preserve the none/penalty/moving_boundary mode matrix and keep all squid claims conservative.

Hard boundaries: do not implement new FSI physics, do not change lbm.step() default behavior, do not change penalty or moving_boundary formulas, do not replace PenaltyFSICoupler3D or MovingBoundaryFSICoupler3D, do not implement two-phase flow, contact angle physics, real squid geometry validation, squid actuation, swimming locomotion, mesh collision/contact, sparse storage, ReducedSquidFSI, production-grade geometry pipeline, or edits to external/taichi_LBM3D. The squid_proxy geometry is procedural and diagnostic only, not anatomical or validated squid simulation. Required artifacts, execution order, geometry settings, baseline contracts, artifact policy, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP13_GEOMETRY_INGESTION_GOAL.md. Finish only after all Step 13 baselines pass, pytest passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 12 is accepted and is the starting point.

Current Step 12 final commit:

```text
e67917bb4b560d1bae73939fa3db1b48e7af9b76
```

Step 12 validated:

```text
src/performance.py exists and estimates dense LBM, MPM, and coupling memory.
src/artifact_utils.py exists and scans artifact size/manifests.
docs/10_performance_memory.md exists.
docs/11_artifact_policy.md exists.
Step 12 memory, profile, artifact, and no-physics regression baselines pass.
tests/test_step12_performance_memory_contract.py exists.
pytest -q passes with 64 tests.
external/taichi_LBM3D remains unchanged.
No solver physics was changed by Step 12.
```

Step 12 means the repository currently has:

```text
1. a runnable MPM-LBM FSI engineering prototype
2. penalty and moving_boundary two-way coupling paths
3. a unified FSIDriver3D
4. documentation and method write-up
5. performance and memory lower-bound estimates
6. artifact hygiene tools
7. regression protection for the Step 10 mode matrix
```

Step 12 still does not mean:

```text
production-grade solver
large-grid readiness
strict final momentum-conserving sharp-interface FSI
real squid geometry simulation
validated squid swimming
two-phase LBM
contact angle physics
sparse storage
```

## 2. Step 13 Objective

Step 13 upgrades the project from a box-block based FSI prototype to a geometry-aware MPM-LBM FSI prototype.

Implement a procedural geometry ingestion layer that provides:

```text
1. analytic geometry primitives
2. deterministic particle sampling inside analytic geometry
3. box, ellipsoid, and squid_proxy geometry types
4. geometry-to-MPM particle cloud initialization
5. geometry-to-LBM diagnostic voxel and projection outputs
6. FSIDriverConfig.geometry_type support
7. FSIDriver3D initialization from geometry_type
8. none / penalty / moving_boundary mode baselines on squid_proxy geometry
9. artifact hygiene checks for new geometry outputs
10. docs and report with conservative, non-overclaiming language
```

This step is geometry ingestion and proxy-case scaffolding. It is not real squid validation.

Allowed language:

```text
squid proxy geometry
procedural squid-like geometry
geometry ingestion scaffold
geometry-aware MPM-LBM prototype
```

Forbidden overclaims:

```text
real squid validation
validated squid swimming simulation
biomechanical squid model
anatomically accurate squid
production-grade geometry pipeline
strict final momentum-conserving sharp-interface FSI
```

## 3. Workspace And Environment

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Primary verification command:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

If Taichi GPU initialization fails during a required baseline, record the exact error. Do not silently downgrade a required final acceptance run to CPU unless the report explicitly marks that run as a probe and the contract is revised.

## 4. Strict Non-Goals

Do not implement these in Step 13:

```text
1. No new FSI physics.
2. No new coupling mode.
3. No changes to lbm.step() default behavior.
4. No changes to the Step 8 moving bounce-back formula.
5. No changes to the Step 6/7 penalty-force formula.
6. No changes to the Step 9 moving-boundary reaction formula.
7. No replacement or deletion of PenaltyFSICoupler3D.
8. No replacement or deletion of MovingBoundaryFSICoupler3D.
9. No two-phase flow.
10. No contact angle physics.
11. No real squid geometry validation.
12. No squid actuation or muscle model.
13. No swimming locomotion model.
14. No mesh collision/contact.
15. No sparse storage implementation.
16. No ReducedSquidFSI.
17. No edits to external/taichi_LBM3D.
18. No production-grade geometry pipeline claim.
19. No deletion or weakening of Step 10/12 regression artifacts.
```

Allowed in Step 13:

```text
procedural analytic geometry
SDF-like or occupancy-style inside tests
deterministic particle-cloud sampling
voxel occupancy diagnostics
geometry configs
MPMSolid3D particle-cloud initialization entry point
FSIDriver3D geometry initialization option
small squid_proxy regression baselines
artifact manifest/summary for Step 13 outputs
docs, tests, logs, outputs, and report
```

Any solver-adjacent edits must be limited to initialization and orchestration. Do not alter collision, streaming, forcing, bounce-back, constitutive model, P2G/G2P, coupling formulas, or reaction-transfer physics.

## 5. Required Final Structure

Create:

```text
src/
  geometry_config.py
  geometry.py
  geometry_utils.py

configs/
  step13_box_geometry.json
  step13_ellipsoid_geometry.json
  step13_squid_proxy_geometry.json
  step13_squid_proxy_none.json
  step13_squid_proxy_penalty.json
  step13_squid_proxy_moving_boundary.json

baseline_tests/
  run_step13_geometry_sampler_box.py
  run_step13_geometry_sampler_ellipsoid.py
  run_step13_squid_proxy_geometry.py
  run_step13_driver_squid_proxy_modes.py
  run_step13_artifact_manifest.py

outputs/
  step13_geometry_box/
  step13_geometry_ellipsoid/
  step13_squid_proxy_geometry/
  step13_squid_proxy_modes/
  step13_artifact_manifest/

logs/
  step13_geometry_box.log
  step13_geometry_ellipsoid.log
  step13_squid_proxy_geometry.log
  step13_squid_proxy_modes.log
  step13_artifact_manifest.log
  step13_pytest.log

docs/
  12_geometry_ingestion.md

tests/
  test_step13_geometry_ingestion_contract.py

STEP13_GEOMETRY_INGESTION_REPORT.md
```

Update:

```text
src/__init__.py
src/mpm_solid.py
src/fsi_config.py
src/fsi_driver.py
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/11_artifact_policy.md
```

Do not delete Step 1-12 reports, logs, outputs, configs, docs, or tests.

## 6. GeometryConfig Contract

Create:

```text
src/geometry_config.py
```

Required public API:

```python
@dataclass(frozen=True)
class GeometryConfig:
    geometry_type: str = "box"
    n_particles: int = 4096

    domain_min: tuple[float, float, float] = (0.0, 0.0, 0.0)
    domain_max: tuple[float, float, float] = (1.0, 1.0, 1.0)

    center: tuple[float, float, float] = (0.5, 0.5, 0.5)
    scale: tuple[float, float, float] = (0.3, 0.3, 0.3)

    box_min: tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: tuple[float, float, float] = (0.55, 0.65, 0.55)

    ellipsoid_radii: tuple[float, float, float] = (0.15, 0.20, 0.12)

    mantle_center: tuple[float, float, float] = (0.50, 0.58, 0.50)
    mantle_radii: tuple[float, float, float] = (0.16, 0.24, 0.12)
    head_center: tuple[float, float, float] = (0.50, 0.36, 0.50)
    head_radii: tuple[float, float, float] = (0.11, 0.10, 0.09)
    arm_length: float = 0.22
    arm_radius: float = 0.018
    fin_radius: float = 0.07

    p_rho: float = 1.0
    particles_per_axis_hint: int = 32
    deterministic: bool = True
```

Supported geometry types:

```text
box
ellipsoid
squid_proxy
```

Validation behavior:

```text
geometry_type must be one of box, ellipsoid, squid_proxy.
n_particles must be positive.
domain_min and domain_max must have exactly 3 values.
domain_min[d] < domain_max[d] for each dimension.
box_min and box_max must have exactly 3 values.
box_min[d] < box_max[d] for each dimension.
all ellipsoid/squid radii must be positive.
arm_length and arm_radius must be positive.
p_rho must be positive.
particles_per_axis_hint must be positive.
```

Required helpers:

```python
@classmethod
def from_json(cls, path: str) -> "GeometryConfig":
    ...

def to_dict(self) -> dict:
    ...
```

JSON round trips must preserve tuple-like values as JSON lists.

## 7. Geometry Utility Contract

Create:

```text
src/geometry_utils.py
```

Required public API:

```python
def as_vec3(values, name: str) -> np.ndarray:
    ...

def inside_box(points: np.ndarray, box_min, box_max) -> np.ndarray:
    ...

def inside_ellipsoid(points: np.ndarray, center, radii) -> np.ndarray:
    ...

def distance_to_segment(points: np.ndarray, a, b) -> np.ndarray:
    ...

def inside_capsule(points: np.ndarray, a, b, radius: float) -> np.ndarray:
    ...
```

Rules:

```text
These helpers are NumPy geometry utilities only.
They must not initialize Taichi.
They must not modify solver state.
All returned masks must be deterministic boolean arrays.
```

## 8. GeometrySampler3D Contract

Create:

```text
src/geometry.py
```

Required public API:

```python
class GeometrySampler3D:
    def __init__(self, config: GeometryConfig):
        ...

    def inside(self, points: np.ndarray) -> np.ndarray:
        ...

    def sample_particles(self) -> dict:
        ...

    def voxelize(self, n_grid: int) -> dict:
        ...
```

`sample_particles()` must return:

```python
{
    "x": np.ndarray,              # shape (n_particles, 3), float32
    "vol0": np.ndarray,           # shape (n_particles,), float32
    "mass": np.ndarray,           # shape (n_particles,), float32
    "geometry_volume": float,
    "sampling_stats": dict,
}
```

`voxelize(n_grid)` must return:

```python
{
    "occupancy": np.ndarray,      # shape (n_grid, n_grid, n_grid), int8
    "phi": np.ndarray,            # shape (n_grid, n_grid, n_grid), float32
    "occupied_count": int,
    "geometry_volume_estimate": float,
}
```

Sampling rules:

```text
Use normalized [0, 1]^3 domain by default.
Use deterministic sampling by default.
Return exactly n_particles particles.
Reject or raise if the requested geometry cannot produce enough points.
All particle positions must be finite.
All particles must be inside the geometry.
All particles must remain inside domain_min/domain_max.
vol0 and mass must be finite and positive.
geometry_volume must be finite and positive.
```

Recommended deterministic sampling:

```text
Generate a structured candidate lattice with enough candidates.
Filter inside points.
If more candidates than n_particles are available, choose a deterministic evenly spaced subset.
If fewer candidates are available, increase the candidate lattice resolution until enough candidates are available or a clear error threshold is reached.
```

Do not use nondeterministic randomness unless `deterministic=False`, and do not use randomness in required baselines.

## 9. Geometry Definitions

### 9.1 Box

Definition:

```text
inside when box_min[d] <= x[d] <= box_max[d] for all d
```

Purpose:

```text
Regression geometry that should remain compatible with the existing box initialization region.
```

### 9.2 Ellipsoid

Definition:

```text
q = (x - center) / ellipsoid_radii
inside when dot(q, q) <= 1
```

Purpose:

```text
Non-box analytic geometry for verifying sampling, voxelization, and projection.
```

### 9.3 Squid Proxy

The squid_proxy must be a procedural union of analytic primitives:

```text
mantle ellipsoid
head ellipsoid
left fin ellipsoid-like primitive
right fin ellipsoid-like primitive
6 to 8 arm capsules
```

Recommended normalized layout:

```text
mantle:
  center = (0.50, 0.58, 0.50)
  radii  = (0.16, 0.24, 0.12)

head:
  center = (0.50, 0.36, 0.50)
  radii  = (0.11, 0.10, 0.09)

arms:
  start near y = 0.30
  extend toward y = 0.15
  use multiple x/z offsets

fins:
  place lateral ellipsoid-like primitives near mantle sides
```

The squid_proxy must report component counts if practical:

```text
mantle_particle_count
head_particle_count
arm_particle_count
fin_particle_count
```

If component labels are implemented, output:

```text
component_labels.npy
```

If labels are not implemented, `geometry_stats.json` must still explain that the proxy is a union of primitives.

Required language in docs and report:

```text
procedural squid proxy geometry, not anatomical or validated squid geometry
```

## 10. MPMSolid3D Initialization Contract

Update:

```text
src/mpm_solid.py
```

Required new public method:

```python
def init_from_numpy(self, x_np, vol0_np, mass_np, v_np=None):
    ...
```

Allowed alias:

```python
def init_from_particle_cloud(self, x_np, vol0_np=None, mass_np=None, v_np=None):
    ...
```

`init_from_numpy()` behavior:

```text
x_np shape must be (n_particles, 3).
vol0_np shape must be (n_particles,).
mass_np shape must be (n_particles,).
v_np is optional; if absent use zeros with shape (n_particles, 3).
all arrays must be finite.
vol0_np and mass_np must be positive.
data must be copied into Taichi fields using from_numpy.
deformation state must be reset.
```

Required deformation reset:

```text
C[p] = zero 3x3 matrix
F[p] = identity 3x3 matrix
Jp[p] = 1.0
```

This is an initialization entry point only. It must not change MPM constitutive physics, P2G, grid update, G2P, or boundary behavior.

## 11. FSIDriver Geometry Integration Contract

Update:

```text
src/fsi_config.py
src/fsi_driver.py
```

Add to `FSIDriverConfig`:

```python
geometry_type: str = "box"
```

Optional but allowed:

```python
geometry_config_path: str | None = None
```

If `geometry_config_path` is implemented, it must load `GeometryConfig` and override only geometry-related fields. If not implemented, the Step 13 configs must use direct `FSIDriverConfig` fields plus `geometry_type`.

Required behavior:

```text
geometry_type = "box" must preserve the existing Step 10 initialization path as much as possible.
For geometry_type = "box", FSIDriver3D may continue using self.solid.init_box().
For geometry_type = "ellipsoid" or "squid_proxy", FSIDriver3D must use GeometrySampler3D.sample_particles() and MPMSolid3D.init_from_numpy().
target_u_lbm must still be converted through GridUnitMapper and applied via set_uniform_velocity().
coupling_mode behavior must remain unchanged.
write_vtk/write_particles behavior must remain unchanged.
```

Do not make moving_boundary the default. Default mode and default geometry must remain backward-compatible with existing tests.

## 12. Config Contracts

Create:

```text
configs/step13_box_geometry.json
configs/step13_ellipsoid_geometry.json
configs/step13_squid_proxy_geometry.json
configs/step13_squid_proxy_none.json
configs/step13_squid_proxy_penalty.json
configs/step13_squid_proxy_moving_boundary.json
```

### `configs/step13_box_geometry.json`

```json
{
  "geometry_type": "box",
  "n_particles": 4096,
  "box_min": [0.25, 0.35, 0.25],
  "box_max": [0.55, 0.65, 0.55]
}
```

### `configs/step13_ellipsoid_geometry.json`

```json
{
  "geometry_type": "ellipsoid",
  "n_particles": 4096,
  "center": [0.5, 0.5, 0.5],
  "ellipsoid_radii": [0.15, 0.20, 0.12]
}
```

### `configs/step13_squid_proxy_geometry.json`

```json
{
  "geometry_type": "squid_proxy",
  "n_particles": 4096,
  "mantle_center": [0.50, 0.58, 0.50],
  "mantle_radii": [0.16, 0.24, 0.12],
  "head_center": [0.50, 0.36, 0.50],
  "head_radii": [0.11, 0.10, 0.09],
  "arm_length": 0.22,
  "arm_radius": 0.018,
  "fin_radius": 0.07
}
```

### Driver mode configs

All squid proxy driver mode configs must use:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
mpm_dt = 4.0e-4
geometry_type = "squid_proxy"
target_u_lbm = [0.01, 0.0, 0.0]
output_interval = 10
write_vtk = false
write_particles = true
```

Mode-specific values:

```text
step13_squid_proxy_none.json:
  coupling_mode = "none"

step13_squid_proxy_penalty.json:
  coupling_mode = "penalty"
  beta_lbm = 0.001
  penalty_force_cap_lbm = 0.0001

step13_squid_proxy_moving_boundary.json:
  coupling_mode = "moving_boundary"
  dynamic_solid_threshold = 0.5
  mb_reaction_scale = 1.0
  mb_force_cap_norm = 0.0001
```

These configs are small engineering baselines, not real squid simulations.

## 13. Baseline 1: Box Geometry Sampler Regression

Create:

```text
baseline_tests/run_step13_geometry_sampler_box.py
```

Purpose:

```text
Verify that GeometrySampler3D can reproduce a box-like particle cloud and initialize MPMSolid3D from NumPy arrays.
```

Required flow:

```text
1. Load or create GeometryConfig(geometry_type="box", n_particles=4096).
2. Call GeometrySampler3D.sample_particles().
3. Save particles_x.npy, particles_vol0.npy, particles_mass.npy.
4. Initialize MPMSolid3D with init_from_numpy().
5. Run solid.get_stats().
6. Run MPMToLBMProjector3D.project() against an initialized LBMFluid3D.
7. Save solid_phi.npy and geometry_stats.json.
```

Required outputs:

```text
outputs/step13_geometry_box/particles_x.npy
outputs/step13_geometry_box/particles_vol0.npy
outputs/step13_geometry_box/particles_mass.npy
outputs/step13_geometry_box/solid_phi.npy
outputs/step13_geometry_box/geometry_stats.json
logs/step13_geometry_box.log
```

Acceptance:

```text
particle_count = 4096
positions finite
all positions inside [0, 1]^3
particle_min >= box_min approximately
particle_max <= box_max approximately
vol0 finite and positive
mass finite and positive
total_mass > 0
MPM min_J = 1 within tolerance
projection active_cell_count > 0
projected_mass > 0
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 13 box geometry sampler finished
```

## 14. Baseline 2: Ellipsoid Geometry Sampler

Create:

```text
baseline_tests/run_step13_geometry_sampler_ellipsoid.py
```

Purpose:

```text
Verify that a non-box analytic geometry can generate a finite particle cloud, voxel occupancy, and LBM projection diagnostics.
```

Required flow:

```text
1. Load or create GeometryConfig(geometry_type="ellipsoid", n_particles=4096).
2. Call GeometrySampler3D.sample_particles().
3. Call GeometrySampler3D.voxelize(n_grid=32).
4. Initialize MPMSolid3D with init_from_numpy().
5. Run MPMToLBMProjector3D.project().
6. Export LBM projection VTK if the existing projection export path is available.
7. Save particles, occupancy, solid_phi, and geometry_stats.json.
```

Required outputs:

```text
outputs/step13_geometry_ellipsoid/particles_x.npy
outputs/step13_geometry_ellipsoid/particles_vol0.npy
outputs/step13_geometry_ellipsoid/particles_mass.npy
outputs/step13_geometry_ellipsoid/geometry_occupancy.npy
outputs/step13_geometry_ellipsoid/solid_phi.npy
outputs/step13_geometry_ellipsoid/geometry_stats.json
logs/step13_geometry_ellipsoid.log
```

If VTK export is produced, place it under:

```text
outputs/step13_geometry_ellipsoid/
```

Acceptance:

```text
particle_count = 4096
positions finite
particle bounds are inside ellipsoid bounding box
voxel occupied_count > 0
projected_mass > 0
projected_mass relative error <= 5.0e-2, or a tighter documented threshold
solid_phi finite
0 <= solid_phi <= 1 within numerical tolerance
cell_force remains zero
hydro_force remains zero
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 13 ellipsoid geometry sampler finished
```

## 15. Baseline 3: Squid Proxy Geometry

Create:

```text
baseline_tests/run_step13_squid_proxy_geometry.py
```

Purpose:

```text
Generate procedural squid-like proxy geometry and verify particle sampling, voxelization, MPM initialization, and LBM projection diagnostics.
```

Required flow:

```text
1. Load GeometryConfig from configs/step13_squid_proxy_geometry.json.
2. Call GeometrySampler3D.sample_particles().
3. Call GeometrySampler3D.voxelize(n_grid=32).
4. Initialize MPMSolid3D with init_from_numpy().
5. Run MPMToLBMProjector3D.project().
6. Save geometry_stats.json with explicit proxy/non-real-squid language.
7. Save particles, mass, vol0, occupancy, and solid_phi diagnostics.
```

Required outputs:

```text
outputs/step13_squid_proxy_geometry/particles_x.npy
outputs/step13_squid_proxy_geometry/particles_mass.npy
outputs/step13_squid_proxy_geometry/particles_vol0.npy
outputs/step13_squid_proxy_geometry/geometry_occupancy.npy
outputs/step13_squid_proxy_geometry/solid_phi.npy
outputs/step13_squid_proxy_geometry/geometry_stats.json
logs/step13_squid_proxy_geometry.log
```

If VTK export is produced, place it under:

```text
outputs/step13_squid_proxy_geometry/
```

Acceptance:

```text
particle_count = 4096
proxy geometry contains multiple analytic components
particle bounds finite
occupied voxel count > 0
projection active_cell_count > 0
projected_mass > 0
projected_mass relative error <= 5.0e-2, or a tighter documented threshold
solid_phi finite
solid_vel finite
cell_force remains zero
hydro_force remains zero
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 13 squid proxy geometry finished
```

## 16. Baseline 4: FSIDriver Squid Proxy Modes

Create:

```text
baseline_tests/run_step13_driver_squid_proxy_modes.py
```

Purpose:

```text
Verify that FSIDriver3D can run squid_proxy geometry through none, penalty, and moving_boundary modes without changing coupling physics.
```

Required modes:

```text
none
penalty
moving_boundary
```

Required settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
mpm_dt = 4.0e-4
target_u_lbm = [0.01, 0.0, 0.0]
geometry_type = "squid_proxy"
write_vtk = false
write_particles = true
output_interval = 10
```

Required outputs:

```text
outputs/step13_squid_proxy_modes/mode_results.csv
outputs/step13_squid_proxy_modes/mode_results.npz
outputs/step13_squid_proxy_modes/none/diagnostics_timeseries.csv
outputs/step13_squid_proxy_modes/penalty/diagnostics_timeseries.csv
outputs/step13_squid_proxy_modes/moving_boundary/diagnostics_timeseries.csv
outputs/step13_squid_proxy_modes/none/particles_x.npy
outputs/step13_squid_proxy_modes/penalty/particles_x.npy
outputs/step13_squid_proxy_modes/moving_boundary/particles_x.npy
logs/step13_squid_proxy_modes.log
```

Required `mode_results.csv` fields:

```text
mode
stable
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
active_cell_count
projected_mass
cell_force_max_norm
hydro_force_max_norm
bb_link_count
active_reaction_particle_count
max_grid_reaction_norm
```

Acceptance:

```text
none stable
penalty stable
moving_boundary stable
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
active_cell_count > 0
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
penalty and moving_boundary have nonzero response
all values finite
no NaN
no Inf
```

Do not require this Step 12 trend on squid_proxy:

```text
moving_boundary > penalty > none
```

Reason:

```text
The geometry changed. A short 10-step proxy run is a stability and plumbing baseline, not a quantitative mode-ranking validation.
```

Required log marker:

```text
[OK] Step 13 squid proxy driver modes finished
```

## 17. Baseline 5: Step 13 Artifact Manifest

Create:

```text
baseline_tests/run_step13_artifact_manifest.py
```

Purpose:

```text
Use the Step 12 artifact utilities to scan repository artifacts after adding geometry outputs.
```

Scan roots:

```text
logs/
outputs/
STEP*_REPORT.md
docs/
paper/
configs/
```

Required outputs:

```text
outputs/step13_artifact_manifest/artifact_manifest.csv
outputs/step13_artifact_manifest/artifact_summary.json
logs/step13_artifact_manifest.log
```

Acceptance:

```text
manifest exists
summary exists
file_count > 0
total_size_bytes > 0
large_file_count >= 0
large_file_count and total_size_mb are reported in STEP13_GEOMETRY_INGESTION_REPORT.md
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 13 artifact manifest finished
```

## 18. Documentation Updates

Create:

```text
docs/12_geometry_ingestion.md
```

Must include:

```text
Step 13 scope
supported geometry types: box, ellipsoid, squid_proxy
GeometryConfig role
GeometrySampler3D role
deterministic sampling behavior
voxel occupancy diagnostics
MPMSolid3D init_from_numpy path
FSIDriverConfig.geometry_type behavior
squid_proxy primitive-union definition
artifact policy note for geometry outputs
limitations and non-goals
```

Must state:

```text
The squid_proxy is a procedural union of analytic primitives.
The squid_proxy is not anatomical squid geometry.
The squid_proxy is not validated squid swimming simulation.
Step 13 does not add new FSI physics.
```

Update `README.md` with a concise section:

```markdown
## Geometry Support

Step 13 adds procedural geometry initialization:
- box
- ellipsoid
- squid_proxy

The squid_proxy is procedural and is not real squid validation.
```

Update `docs/08_roadmap.md`:

```text
Mark Step 13 as current while in progress, and completed after acceptance.
Set Step 14 to larger-grid validation.
State that future work must preserve the Step 10 mode matrix and Step 12 resource/artifact checks.
```

Update `docs/09_api_reference.md`:

```text
Add GeometryConfig.
Add GeometrySampler3D.
Add MPMSolid3D.init_from_numpy.
Add FSIDriverConfig.geometry_type.
```

Update `docs/11_artifact_policy.md`:

```text
Add a note that geometry particle clouds, voxel masks, and VTK files can grow quickly.
Small Step 13 baseline outputs may be committed.
Large ad-hoc geometry experiments must go under outputs/experiments/ or outputs/scratch/.
```

## 19. Step 13 Report Contract

Create:

```text
STEP13_GEOMETRY_INGESTION_REPORT.md
```

Required sections:

```markdown
# Step 13 Geometry Ingestion Report

## 1. Goal
## 2. Files
## 3. Explicit Non-Goals
## 4. Geometry Types
## 5. Squid Proxy Definition
## 6. Box Geometry Baseline
## 7. Ellipsoid Geometry Baseline
## 8. Squid Proxy Geometry Baseline
## 9. Squid Proxy Driver Modes
## 10. Artifact Manifest
## 11. Documentation Updates
## 12. Verification
## 13. GitHub Sync
## 14. Acceptance Checklist
## 15. Decision
```

The report must include:

```text
commands run
key particle/voxel/projection stats
mode_results table
artifact summary
pytest command/result
confirmation that external/taichi_LBM3D was unchanged
confirmation that no FSI physics changed
confirmation that squid_proxy is not real squid validation
final commit hash
remote branch after push
```

Before final verification, checklist items may be unchecked. They must be checked only after baselines and pytest pass.

## 20. Pytest Contract

Create:

```text
tests/test_step13_geometry_ingestion_contract.py
```

The test must check required paths:

```python
required_paths = [
    "src/geometry_config.py",
    "src/geometry.py",
    "src/geometry_utils.py",
    "docs/12_geometry_ingestion.md",
    "configs/step13_box_geometry.json",
    "configs/step13_ellipsoid_geometry.json",
    "configs/step13_squid_proxy_geometry.json",
    "configs/step13_squid_proxy_none.json",
    "configs/step13_squid_proxy_penalty.json",
    "configs/step13_squid_proxy_moving_boundary.json",
    "baseline_tests/run_step13_geometry_sampler_box.py",
    "baseline_tests/run_step13_geometry_sampler_ellipsoid.py",
    "baseline_tests/run_step13_squid_proxy_geometry.py",
    "baseline_tests/run_step13_driver_squid_proxy_modes.py",
    "baseline_tests/run_step13_artifact_manifest.py",
    "logs/step13_geometry_box.log",
    "logs/step13_geometry_ellipsoid.log",
    "logs/step13_squid_proxy_geometry.log",
    "logs/step13_squid_proxy_modes.log",
    "logs/step13_artifact_manifest.log",
    "outputs/step13_geometry_box/particles_x.npy",
    "outputs/step13_geometry_ellipsoid/geometry_occupancy.npy",
    "outputs/step13_squid_proxy_geometry/particles_x.npy",
    "outputs/step13_squid_proxy_geometry/geometry_occupancy.npy",
    "outputs/step13_squid_proxy_modes/mode_results.csv",
    "outputs/step13_artifact_manifest/artifact_summary.json",
    "STEP13_GEOMETRY_INGESTION_REPORT.md",
]
```

The test must check source keywords:

```text
class GeometryConfig
class GeometrySampler3D
geometry_type
sample_particles
voxelize
squid_proxy
ellipsoid
init_from_numpy
FSIDriver3D
MPMSolid3D
```

The test must check log success markers:

```text
[OK] Step 13 box geometry sampler finished
[OK] Step 13 ellipsoid geometry sampler finished
[OK] Step 13 squid proxy geometry finished
[OK] Step 13 squid proxy driver modes finished
[OK] Step 13 artifact manifest finished
```

The test must parse CSV/JSON/NPY outputs and verify:

```text
particle arrays have shape (4096, 3)
particle arrays are finite
voxel occupancy arrays are finite
voxel occupied_count > 0
mode_results.csv contains none, penalty, moving_boundary
all modes are stable
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
active_cell_count > 0
artifact summary file_count > 0
artifact summary total_size_bytes > 0
```

The test must check documentation/report do not contain overclaim phrases:

```text
real squid simulation is validated
validated squid swimming
biomechanically accurate squid
anatomically accurate squid
production-grade geometry pipeline
strict momentum-conserving FSI is complete
```

The test must check forbidden implementation claims:

```text
implements two_phase
implements contact_angle
ReducedSquidFSI
```

Do not forbid explanatory non-goal phrases such as:

```text
no two-phase flow
no contact angle physics
not real squid validation
```

The test must check `STEP13_GEOMETRY_INGESTION_REPORT.md` acceptance checklist items are marked `[x]`.

## 21. Required Execution Order

Follow this order:

```text
1. Confirm git status, branch, remote, README, roadmap, and Step 12 baseline.
2. Read STEP13_GEOMETRY_INGESTION_GOAL.md.
3. Read README.md, docs/08_roadmap.md, docs/09_api_reference.md, docs/11_artifact_policy.md, STEP12_PERFORMANCE_MEMORY_REPORT.md, src/fsi_config.py, src/fsi_driver.py, and src/mpm_solid.py.
4. Add tests/test_step13_geometry_ingestion_contract.py first.
5. Run pytest and confirm RED because Step 13 artifacts are missing.
6. Implement src/geometry_config.py and src/geometry_utils.py.
7. Implement src/geometry.py with box and ellipsoid support.
8. Add MPMSolid3D.init_from_numpy() and deformation reset.
9. Run box geometry sampler baseline and save log.
10. Run ellipsoid geometry sampler baseline and save log.
11. Implement squid_proxy union geometry.
12. Add Step 13 geometry JSON configs.
13. Run squid proxy geometry baseline and save log.
14. Add FSIDriverConfig.geometry_type and FSIDriver3D geometry initialization.
15. Run squid proxy driver modes baseline and save log.
16. Run Step 13 artifact manifest baseline and save log.
17. Add docs/12_geometry_ingestion.md.
18. Update README.md, docs/08_roadmap.md, docs/09_api_reference.md, and docs/11_artifact_policy.md.
19. Add STEP13_GEOMETRY_INGESTION_REPORT.md with unchecked checklist.
20. Run pytest -q.
21. Fix only Step 13 issues.
22. Save final pytest log as logs/step13_pytest.log.
23. Confirm src solver physics behavior is unchanged except initialization/orchestration additions.
24. Confirm external/taichi_LBM3D is unchanged.
25. Update STEP13_GEOMETRY_INGESTION_REPORT.md checklist to checked.
26. Run final pytest -q.
27. Run git diff --check and git diff --cached --check.
28. Commit Step 13 artifacts.
29. Push to GitHub.
30. Verify local HEAD equals origin/main.
```

Do not report a short probe as Step 13 acceptance. Step 13 acceptance requires all five Step 13 baselines, pytest, completed report, and GitHub push.

## 22. Verification Commands

Primary:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Baseline commands:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_geometry_sampler_box.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_geometry_sampler_ellipsoid.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_squid_proxy_geometry.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_driver_squid_proxy_modes.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_artifact_manifest.py
```

Log-saving form:

```powershell
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_geometry_sampler_box.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step13_geometry_box.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_geometry_sampler_ellipsoid.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step13_geometry_ellipsoid.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_squid_proxy_geometry.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step13_squid_proxy_geometry.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_driver_squid_proxy_modes.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step13_squid_proxy_modes.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step13_artifact_manifest.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step13_artifact_manifest.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' -m pytest -q 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step13_pytest.log; $out; if ($code -ne 0) { exit $code }
```

Git hygiene:

```powershell
git status --short --branch
git status --short external
git diff --check
git diff --cached --check
```

## 23. Hard Acceptance Checklist

All must be true before Step 13 is complete:

```text
[ ] main is on the Step 13 final commit
[ ] src/geometry_config.py exists
[ ] src/geometry.py exists
[ ] src/geometry_utils.py exists
[ ] src/__init__.py exports GeometryConfig and GeometrySampler3D
[ ] MPMSolid3D supports init_from_numpy or init_from_particle_cloud
[ ] FSIDriverConfig supports geometry_type
[ ] FSIDriver3D can initialize non-box geometry through geometry_type
[ ] geometry_type="box" preserves existing box/default behavior
[ ] configs/step13_box_geometry.json exists
[ ] configs/step13_ellipsoid_geometry.json exists
[ ] configs/step13_squid_proxy_geometry.json exists
[ ] configs/step13_squid_proxy_none.json exists
[ ] configs/step13_squid_proxy_penalty.json exists
[ ] configs/step13_squid_proxy_moving_boundary.json exists
[ ] box geometry sampler baseline passes
[ ] ellipsoid geometry sampler baseline passes
[ ] squid proxy geometry baseline passes
[ ] squid proxy driver modes baseline passes
[ ] Step 13 artifact manifest baseline passes
[ ] none / penalty / moving_boundary run on squid_proxy geometry
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] mpm_max_speed < 10
[ ] particle positions are finite
[ ] geometry occupancy is finite
[ ] active_cell_count > 0
[ ] projected_mass > 0
[ ] no NaN
[ ] no Inf
[ ] docs explicitly say squid_proxy is not real squid validation
[ ] report explicitly says squid_proxy is not real squid validation
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] artifact manifest reports total size and large_file_count
[ ] README.md documents geometry support
[ ] docs/08_roadmap.md updated
[ ] docs/09_api_reference.md updated
[ ] docs/11_artifact_policy.md updated
[ ] STEP13_GEOMETRY_INGESTION_REPORT.md complete
[ ] tests/test_step13_geometry_ingestion_contract.py exists
[ ] pytest -q passes
[ ] logs/step13_pytest.log exists
[ ] git diff --check passes
[ ] Step 13 artifacts are committed
[ ] Step 13 artifacts are pushed to GitHub
```

## 24. Failure Handling

If deterministic sampling cannot produce enough particles:

```text
Increase candidate lattice resolution first.
Do not switch to nondeterministic random sampling for accepted baselines.
Record the candidate count and accepted count in geometry_stats.json.
```

If projection mass error is too high:

```text
Inspect particle positions and boundary truncation.
Do not change MPMToLBMProjector3D projection math unless the user explicitly broadens scope.
If the error is a diagnostic tolerance issue, document the reason and set a conservative threshold in the report and tests.
```

If squid_proxy mode baselines become unstable:

```text
Reduce target_u_lbm or coupling strength only within the Step 13 config files.
Do not change penalty or moving_boundary formulas.
Do not report a shorter probe as full acceptance.
```

If Step 10 or Step 12 regression tests fail:

```text
Stop and inspect whether Step 13 changed existing behavior.
Fix initialization/orchestration compatibility.
Do not weaken existing tests unless the failure is a demonstrably stale documentation-only assertion.
```

If artifact manifest finds large files:

```text
Record them in STEP13_GEOMETRY_INGESTION_REPORT.md.
Do not delete committed baseline artifacts unless explicitly requested.
Move ad-hoc non-baseline outputs to scratch/experiments paths if needed.
```

If pytest fails:

```text
Record the exact failing tests and error text.
Fix only issues caused by Step 13 unless the user explicitly broadens scope.
```

If GitHub push fails:

```text
Keep the local commit.
Record the exact push error.
Do not force-push unless explicitly requested.
```

## 25. Completion Definition

Step 13 is complete only when:

```text
1. all required Step 13 files exist
2. GeometryConfig and GeometrySampler3D are implemented
3. MPMSolid3D can initialize from deterministic geometry particle clouds
4. FSIDriverConfig and FSIDriver3D support geometry_type
5. box geometry baseline passes
6. ellipsoid geometry baseline passes
7. squid_proxy geometry baseline passes
8. squid_proxy none/penalty/moving_boundary driver mode baseline passes
9. Step 13 artifact manifest baseline passes
10. documentation and README updates are complete
11. Step 13 report has a completed checklist
12. pytest -q passes
13. logs/step13_pytest.log is saved
14. external/taichi_LBM3D remains unchanged
15. no FSI physics was changed
16. no real squid validation is claimed
17. final Step 13 commit is pushed to GitHub
18. local HEAD matches origin/main
```

Only after those conditions are satisfied may the report mark:

```text
Can proceed to Step 14?

- [x] Yes
- [ ] No
```
