# Step 18 Goal: Experimental Link-Area Reaction Transfer Mode

This file is the authoritative execution contract for Step 18 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 18 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 18

Step 17 is accepted on GitHub at commit:

```text
e369a9555da992a4f936e03bc71cdaf3ed80f31f
```

Step 17 established:

- diagnostic-only per-D3Q19-direction moving-boundary link accounting;
- `LinkAreaMomentumAccounting3D`;
- `uniform`, `inverse_length`, and `length` link-area proxy policies;
- 32^3 directional sanity and wall Couette link-area proxy baselines;
- 48^3 box link budget baseline;
- 48^3 procedural squid_proxy link budget baseline;
- 64^3 box link budget baseline;
- Step 16 moving_boundary regression evidence;
- artifact manifest with `large_file_count = 0`;
- `pytest -q`: 112 passed;
- `external/taichi_LBM3D` unchanged.

Step 17 documents that:

- the moving bounce-back formula is unchanged;
- `MovingBoundaryFSICoupler3D` is unchanged;
- link-area policies are diagnostic proxies, not final surface-area reconstruction;
- squid_proxy is procedural and not real squid validation;
- strict link-area momentum-conserving sharp-interface FSI remains future work.

Step 18 must preserve all of the above.

## 2. Step 18 Objective

Add an opt-in experimental link-area reaction transfer mode for the existing moving_boundary path.

The project currently has:

```text
moving_boundary boundary handling + engineering-scale reaction transfer + Step 17 diagnostic link-area accounting
```

Step 18 should add:

```text
moving_boundary boundary handling + opt-in experimental link-area reaction transfer + direct comparison baselines
```

The Step 18 target is an experimental prototype and validation scaffold. It is not a declaration that final strict link-area momentum-conserving FSI is solved.

Step 18 must:

1. Keep the existing Step 9/15/16 engineering-scale `MovingBoundaryFSICoupler3D` path available and unchanged.
2. Keep `coupling_mode = "moving_boundary"` as the FSI mode.
3. Add `reaction_transfer_mode = "engineering" | "link_area_experimental"`.
4. Keep `reaction_transfer_mode = "engineering"` as the default.
5. Add a dedicated `LinkAreaMovingBoundaryCoupler3D` for the experimental path.
6. Use Step 17 direction-wise / link-area proxy accounting to compute a bounded global `area_scale`.
7. Apply that bounded `area_scale` only to the MPM reaction transfer magnitude in the experimental path.
8. Keep the local spatial reaction distribution based on the existing `lbm.hydro_force` grid field.
9. Add 32^3 sanity and policy sweep baselines.
10. Add 48^3 box and 48^3 procedural squid_proxy experimental baselines.
11. Add engineering-vs-link-area comparison evidence.
12. Add existing-mode regression evidence proving the current engineering path remains stable.
13. Add a Step 18 report, documentation, logs, outputs, artifact manifest, and contract test.

## 3. Required Design Choice

Use this architecture:

```text
coupling_mode = "moving_boundary"
reaction_transfer_mode = "engineering" | "link_area_experimental"
```

Do not add a new production coupling mode such as:

```text
coupling_mode = "moving_boundary_link_area_experimental"
```

Reason: Step 18 changes only the MPM reaction transfer path. It does not change the LBM moving-boundary condition, the Step 8 moving bounce-back formula, or the high-level FSI mode identity.

## 4. Hard Boundaries

Do not implement or change:

- no change to the Step 8 moving bounce-back formula;
- no change to `LBMFluid3D.step()`;
- no change to the default `LBMFluid3D.step_moving_bounceback()` behavior except optional diagnostics that do not affect state;
- no change to `MovingBoundaryFSICoupler3D` reaction transfer formula;
- no deletion, replacement, or behavior change of `MovingBoundaryFSICoupler3D`;
- no change to `PenaltyFSICoupler3D`;
- no change to `FSIDriver3D` default behavior for existing configs;
- no replacement of the existing engineering moving_boundary path;
- no new default FSI mode;
- no two-phase flow;
- no contact angle physics;
- no real squid validation claims;
- no squid actuation or swimming simulation;
- no mesh import;
- no sparse storage;
- no `ReducedSquidFSI`;
- no edits to `external/taichi_LBM3D`;
- no claim that strict momentum-conserving sharp-interface FSI is complete.

Allowed work:

- a new opt-in experimental reaction-transfer branch;
- new config fields for transfer mode and area-scale bounds;
- a new dedicated experimental coupler class;
- new baseline scripts and comparison scripts;
- new docs, report, logs, outputs, and contract tests;
- diagnostic use of Step 17 direction-wise accounting.

## 5. Required Source Changes

### 5.1 `src/fsi_config.py`

Add:

```python
VALID_REACTION_TRANSFER_MODES = ("engineering", "link_area_experimental")
VALID_LINK_AREA_POLICIES = ("uniform", "inverse_length", "length")
```

Add frozen dataclass fields to `FSIDriverConfig`:

```python
reaction_transfer_mode: str = "engineering"
link_area_policy: str = "inverse_length"
link_area_scale_min: float = 0.25
link_area_scale_max: float = 2.0
```

Validation requirements:

- `reaction_transfer_mode` must be one of `VALID_REACTION_TRANSFER_MODES`;
- `link_area_policy` must be one of `VALID_LINK_AREA_POLICIES`;
- `link_area_scale_min` must be positive;
- `link_area_scale_max` must be positive;
- `link_area_scale_min <= link_area_scale_max`;
- `reaction_transfer_mode = "link_area_experimental"` is valid only when `coupling_mode == "moving_boundary"`;
- existing configs that omit these fields must still load with `reaction_transfer_mode == "engineering"`.

Do not change the default `coupling_mode` value unless an existing accepted contract already requires it. The key default for Step 18 is:

```text
reaction_transfer_mode == "engineering"
```

### 5.2 `src/link_area_coupling.py`

Create:

```python
@ti.data_oriented
class LinkAreaMovingBoundaryCoupler3D:
    """
    Experimental opt-in moving-boundary reaction transfer using a bounded
    global area_scale derived from Step 17 link-area proxy accounting.

    This class does not change LBM bounce-back, does not modify lbm.cell_force,
    and does not replace MovingBoundaryFSICoupler3D.
    """
```

Constructor:

```python
def __init__(
    self,
    sim_config,
    area_policy: str = "inverse_length",
    reaction_scale: float = 1.0,
    force_cap_norm: float = 1.0e-5,
    phi_min: float = 1.0e-6,
    area_scale_min: float = 0.25,
    area_scale_max: float = 2.0,
):
    ...
```

Required fields:

```text
n_grid
dx_norm
inv_dx_norm
lbm_dt_phys
area_policy
reaction_scale
force_cap_norm
phi_min
force_density_scale_lbm_to_norm
area_scale_min
area_scale_max
area_scale
active_reaction_particle_count
max_particle_reaction_norm
max_grid_reaction_norm
net_particle_reaction_force
net_grid_reaction_force
area_weighted_hydro_sum
area_proxy_total
```

Required methods:

```python
def update_area_scale_from_lbm(self, lbm):
    ...

@ti.kernel
def set_area_scale(self, value: ti.f32):
    ...

@ti.kernel
def clear_reaction_diagnostics(self):
    ...

@ti.kernel
def add_link_area_reaction_to_mpm_grid(self, solid: ti.template(), lbm: ti.template()):
    ...

def get_stats(self):
    ...
```

`update_area_scale_from_lbm()` must use `LinkAreaMomentumAccounting3D.summarize_link_accounting(lbm, policy=self.area_policy)`.

Recommended formula:

```text
raw_area_scale =
    abs(area_weighted_solid_force_x) / (abs(bb_net_solid_force_x) + eps)

area_scale = clip(raw_area_scale, area_scale_min, area_scale_max)
```

Use a small positive `eps`, for example:

```text
eps = 1.0e-12
```

The method must return a Python summary dictionary that includes at least:

```text
area_policy
raw_area_scale
area_scale
area_proxy_total
bb_net_solid_force_x
area_weighted_solid_force_x
```

If `bb_net_solid_force_x` is near zero, the bounded result must remain finite and must not produce NaN or Inf.

### 5.3 Experimental Transfer Formula

The experimental coupler must keep the same local hydro-force sampling concept as the engineering path:

```text
sampled_hydro_lbm = sum particle_stencil_weight * lbm.hydro_force[I]
```

Then apply the bounded global link-area scale:

```text
particle_force =
    sampled_hydro_lbm
    * force_density_scale_lbm_to_norm
    * particle_volume
    * reaction_scale
    * area_scale
```

The force must still be capped by `force_cap_norm`.

The force must be added to the MPM grid external force field, not to `lbm.cell_force`:

```text
solid.grid_f_ext
```

Do not route this experimental transfer through:

```text
lbm.cell_force
```

Do not claim this is local surface-area reconstruction. Step 18 uses a global proxy scale from Step 17 accounting.

### 5.4 `src/fsi_driver.py`

Add an attribute:

```python
self.link_area_coupler = None
```

In `initialize()`:

```python
if self.config.coupling_mode == "moving_boundary":
    if self.config.reaction_transfer_mode == "engineering":
        self.mb_coupler = MovingBoundaryFSICoupler3D(...)
    elif self.config.reaction_transfer_mode == "link_area_experimental":
        self.link_area_coupler = LinkAreaMovingBoundaryCoupler3D(...)
```

Do not create both couplers for the same driver run unless a baseline script explicitly creates separate drivers for comparison.

In `_step_moving_boundary()` preserve the existing LBM path:

```python
self._project()
self.lbm.update_dynamic_solid(self.config.dynamic_solid_threshold)
self.lbm.reinitialize_new_fluid_cells()
self.lbm.step_moving_bounceback()
```

Then branch only the MPM reaction transfer:

```python
if self.config.reaction_transfer_mode == "engineering":
    use self.mb_coupler.add_moving_boundary_reaction_to_mpm_grid(...)

elif self.config.reaction_transfer_mode == "link_area_experimental":
    area_summary = self.link_area_coupler.update_area_scale_from_lbm(self.lbm)
    use self.link_area_coupler.add_link_area_reaction_to_mpm_grid(...)
```

Diagnostics:

- Existing CSV fields must remain compatible.
- Add `reaction_transfer_mode` to diagnostics only if all existing tests and output contracts are updated safely.
- Prefer not to change the common `DIAGNOSTIC_FIELDS` unless necessary.
- Step 18 baseline scripts may save separate link-area transfer summaries without changing existing driver CSVs.

If common diagnostics are updated, ensure older rows and mode matrix tests still pass.

### 5.5 `src/__init__.py`

Export:

```python
LinkAreaMovingBoundaryCoupler3D
```

## 6. Required Config Files

Create:

```text
configs/step18_link_area_transfer_sanity_32.json
configs/step18_link_area_policy_sweep_box_32.json
configs/step18_link_area_transfer_box_48.json
configs/step18_link_area_transfer_squid_proxy_48.json
configs/step18_compare_engineering_vs_link_area_box_48.json
configs/step18_compare_engineering_vs_link_area_squid_proxy_48.json
```

All Step 18 configs must include:

```json
{
  "coupling_mode": "moving_boundary",
  "write_vtk": false,
  "write_particles": false
}
```

Experimental configs must include:

```json
{
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0
}
```

Engineering comparison configs must include:

```json
{
  "reaction_transfer_mode": "engineering"
}
```

### 6.1 `configs/step18_link_area_transfer_sanity_32.json`

Required baseline settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "geometry_type": "box",
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.01, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00001,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "write_vtk": false,
  "write_particles": false
}
```

### 6.2 `configs/step18_link_area_policy_sweep_box_32.json`

Required baseline settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "geometry_type": "box",
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.01, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00001,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "write_vtk": false,
  "write_particles": false
}
```

The runner must evaluate all policies:

```text
uniform
inverse_length
length
```

### 6.3 `configs/step18_link_area_transfer_box_48.json`

Required baseline settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00001,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "write_vtk": false,
  "write_particles": false
}
```

### 6.4 `configs/step18_link_area_transfer_squid_proxy_48.json`

Required baseline settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 0.5,
  "mb_force_cap_norm": 0.000025,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "write_vtk": false,
  "write_particles": false
}
```

## 7. Required Baseline Scripts

Create:

```text
baseline_tests/step18_common.py
baseline_tests/run_step18_link_area_transfer_sanity.py
baseline_tests/run_step18_link_area_policy_sweep_box_32.py
baseline_tests/run_step18_link_area_transfer_box_48.py
baseline_tests/run_step18_link_area_transfer_squid_proxy_48.py
baseline_tests/run_step18_compare_engineering_vs_link_area.py
baseline_tests/run_step18_regression_existing_modes.py
baseline_tests/run_step18_artifact_manifest.py
```

All scripts must:

- write deterministic CSV/NPZ or JSON outputs under `outputs/step18_*`;
- write logs under `logs/step18_*.log` when executed through the acceptance commands;
- raise on NaN or Inf;
- raise on unstable required rows;
- print a final `[OK] ... finished` marker;
- use small baseline sizes exactly as specified unless a failure requires documented conservative reduction.

### 7.1 Baseline: Link-Area Transfer Sanity

Script:

```text
baseline_tests/run_step18_link_area_transfer_sanity.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_sanity.py
```

Output:

```text
outputs/step18_link_area_transfer_sanity/sanity_results.csv
outputs/step18_link_area_transfer_sanity/sanity_results.npz
logs/step18_link_area_transfer_sanity.log
```

Required CSV fields:

```text
step
area_policy
raw_area_scale
area_scale
area_proxy_total
bb_link_count
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
active_reaction_particle_count
max_grid_reaction_norm
net_grid_reaction_force_x
cell_force_max_norm
stable
```

Acceptance:

```text
area_scale finite
0.25 <= area_scale <= 2.0
active_reaction_particle_count > 0
max_grid_reaction_norm > 0
cell_force_max_norm == 0
bb_link_count > 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
no NaN
no Inf
```

The sign of `net_grid_reaction_force_x` must be recorded, but do not require a specific sign unless the runner uses a controlled geometry where the sign is provably fixed.

Final marker:

```text
[OK] Step 18 link-area transfer sanity finished
```

### 7.2 Baseline: Area Policy Sweep Box 32

Script:

```text
baseline_tests/run_step18_link_area_policy_sweep_box_32.py
```

Output:

```text
outputs/step18_link_area_policy_sweep_box_32/policy_sweep.csv
outputs/step18_link_area_policy_sweep_box_32/policy_sweep.npz
logs/step18_link_area_policy_sweep_box_32.log
```

Required CSV fields:

```text
policy
stable
area_scale_final
raw_area_scale_final
area_proxy_total
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
solid_slowdown
projection_zone_ux_final
cell_force_max_norm
bb_link_count
active_reaction_particle_count
```

Acceptance:

```text
uniform row exists
inverse_length row exists
length row exists
inverse_length stable == True
all stable rows have rho_min > 0.95
all stable rows have rho_max < 1.05
all stable rows have lbm_max_v < 0.1
all stable rows have mpm_min_J > 0
all stable rows have finite bounded area_scale_final
cell_force_max_norm == 0 for every row
bb_link_count > 0 for every row
```

Do not require all policies to outperform engineering. This is a sweep, not an optimization claim.

Final marker:

```text
[OK] Step 18 link-area policy sweep box 32 finished
```

### 7.3 Baseline: 48^3 Box Experimental Transfer

Script:

```text
baseline_tests/run_step18_link_area_transfer_box_48.py
```

Output:

```text
outputs/step18_link_area_transfer_box_48/box_48_link_area_results.csv
outputs/step18_link_area_transfer_box_48/box_48_link_area_results.npz
outputs/step18_link_area_transfer_box_48/diagnostics_timeseries.csv
logs/step18_link_area_transfer_box_48.log
```

Acceptance:

```text
stable == True
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
bb_link_count > 0
active_reaction_particle_count > 0
area_scale finite
0.25 <= area_scale <= 2.0
cell_force_max_norm == 0
no NaN
no Inf
```

Final marker:

```text
[OK] Step 18 link-area transfer box 48 finished
```

### 7.4 Baseline: 48^3 Procedural Squid Proxy Experimental Transfer

Script:

```text
baseline_tests/run_step18_link_area_transfer_squid_proxy_48.py
```

Output:

```text
outputs/step18_link_area_transfer_squid_proxy_48/squid_proxy_48_link_area_results.csv
outputs/step18_link_area_transfer_squid_proxy_48/squid_proxy_48_link_area_results.npz
outputs/step18_link_area_transfer_squid_proxy_48/diagnostics_timeseries.csv
logs/step18_link_area_transfer_squid_proxy_48.log
```

Acceptance:

```text
stable == True
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
bb_link_count > 0
active_reaction_particle_count > 0
area_scale finite
0.25 <= area_scale <= 2.0
cell_force_max_norm == 0
no NaN
no Inf
```

The report and docs must explicitly state:

```text
squid_proxy is procedural and not real squid validation.
```

Final marker:

```text
[OK] Step 18 link-area transfer squid proxy 48 finished
```

### 7.5 Baseline: Engineering vs Link-Area Comparison

Script:

```text
baseline_tests/run_step18_compare_engineering_vs_link_area.py
```

Cases:

```text
box_48 / engineering
box_48 / link_area_experimental
squid_proxy_48 / engineering
squid_proxy_48 / link_area_experimental
```

Output:

```text
outputs/step18_compare_engineering_vs_link_area/comparison.csv
outputs/step18_compare_engineering_vs_link_area/comparison.npz
logs/step18_compare_engineering_vs_link_area.log
```

Required CSV fields:

```text
case
transfer_mode
policy
stable
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
solid_slowdown
projection_zone_ux_final
area_scale_final
bb_link_count
active_reaction_particle_count
max_grid_reaction_norm
cell_force_max_norm
```

Acceptance:

```text
engineering rows exist
link_area_experimental rows exist
all rows stable == True
link_area_experimental rows have finite bounded area_scale_final
engineering rows may use area_scale_final = 1.0 or blank/NaN only if the CSV contract explicitly handles it
moving_boundary rows have cell_force_max_norm == 0
no NaN / Inf in required numeric fields
```

Do not require the experimental rows to be better than engineering rows. Step 18 establishes an experimental prototype and comparison evidence.

Final marker:

```text
[OK] Step 18 engineering vs link-area comparison finished
```

### 7.6 Baseline: Existing Mode Regression

Script:

```text
baseline_tests/run_step18_regression_existing_modes.py
```

Purpose:

```text
prove the new experimental transfer path does not break existing engineering moving_boundary behavior or Step 17 accounting behavior
```

Required checks:

```text
Step 16-style box 48 engineering moving_boundary short run
Step 17-style link-area accounting diagnostic short run
default FSIDriverConfig reaction_transfer_mode == engineering
```

Output:

```text
outputs/step18_regression_existing_modes/regression_results.csv
outputs/step18_regression_existing_modes/regression_results.npz
logs/step18_regression_existing_modes.log
```

Acceptance:

```text
engineering moving_boundary row stable
directional accounting row stable
default reaction_transfer_mode == engineering
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
cell_force_max_norm == 0 for moving_boundary rows
no NaN
no Inf
```

Final marker:

```text
[OK] Step 18 existing mode regression finished
```

### 7.7 Artifact Manifest

Script:

```text
baseline_tests/run_step18_artifact_manifest.py
```

Output:

```text
outputs/step18_artifact_manifest/artifact_manifest.csv
outputs/step18_artifact_manifest/artifact_summary.json
logs/step18_artifact_manifest.log
```

Acceptance:

```text
file_count recorded
total_size_bytes recorded
total_size_mb recorded
large_file_count == 0
```

Final marker:

```text
[OK] Step 18 artifact manifest finished
```

## 8. Required Documentation

Create:

```text
docs/17_experimental_link_area_transfer.md
STEP18_LINK_AREA_TRANSFER_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/16_link_area_momentum_accounting.md
```

Required phrases in docs/report:

```text
Step 18 adds an opt-in experimental link-area reaction transfer mode.
The default moving_boundary reaction transfer remains engineering.
The moving bounce-back formula is unchanged.
MovingBoundaryFSICoupler3D is unchanged.
The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting.
This is not final strict momentum-conserving sharp-interface FSI.
squid_proxy is procedural and not real squid validation.
```

Forbidden overclaims:

```text
strict momentum-conserving FSI is complete
real squid simulation is validated
validated squid swimming
production-ready sharp-interface FSI
final surface-area reconstruction
```

## 9. Step 18 Report Contract

`STEP18_LINK_AREA_TRANSFER_REPORT.md` must contain:

```text
1. Goal
2. Files created and updated
3. Explicit non-goals
4. Experimental transfer formula
5. Sanity baseline results
6. Area policy sweep results
7. 48^3 box experimental transfer results
8. 48^3 procedural squid_proxy experimental transfer results
9. Engineering vs link-area comparison results
10. Existing mode regression results
11. Artifact manifest summary
12. Verification commands
13. GitHub sync information
14. Acceptance checklist
15. Decision for Step 19
```

The report must include the formula:

```text
area_scale = clip(
    |area_weighted_solid_force_x| / (|bb_net_solid_force_x| + eps),
    area_scale_min,
    area_scale_max
)

particle_force =
    sampled_hydro_lbm
    * force_density_scale_lbm_to_norm
    * particle_volume
    * reaction_scale
    * area_scale
```

The report must explicitly state that this is a global proxy scale, not local surface-area reconstruction.

## 10. Required Contract Test

Create:

```text
tests/test_step18_link_area_transfer_contract.py
```

The test must verify required files exist:

```python
required_paths = [
    "src/link_area_coupling.py",
    "configs/step18_link_area_transfer_sanity_32.json",
    "configs/step18_link_area_policy_sweep_box_32.json",
    "configs/step18_link_area_transfer_box_48.json",
    "configs/step18_link_area_transfer_squid_proxy_48.json",
    "configs/step18_compare_engineering_vs_link_area_box_48.json",
    "configs/step18_compare_engineering_vs_link_area_squid_proxy_48.json",
    "baseline_tests/step18_common.py",
    "baseline_tests/run_step18_link_area_transfer_sanity.py",
    "baseline_tests/run_step18_link_area_policy_sweep_box_32.py",
    "baseline_tests/run_step18_link_area_transfer_box_48.py",
    "baseline_tests/run_step18_link_area_transfer_squid_proxy_48.py",
    "baseline_tests/run_step18_compare_engineering_vs_link_area.py",
    "baseline_tests/run_step18_regression_existing_modes.py",
    "baseline_tests/run_step18_artifact_manifest.py",
    "docs/17_experimental_link_area_transfer.md",
    "STEP18_LINK_AREA_TRANSFER_REPORT.md",
]
```

The test must verify source keywords:

```text
class LinkAreaMovingBoundaryCoupler3D
reaction_transfer_mode
engineering
link_area_experimental
area_scale
link_area_policy
link_area_scale_min
link_area_scale_max
add_link_area_reaction_to_mpm_grid
update_area_scale_from_lbm
```

The test must verify default behavior:

```text
FSIDriverConfig().reaction_transfer_mode == "engineering"
existing moving_boundary configs without reaction_transfer_mode still load as engineering
link_area_experimental is opt-in only
```

The test must verify output/log markers:

```text
[OK] Step 18 link-area transfer sanity finished
[OK] Step 18 link-area policy sweep box 32 finished
[OK] Step 18 link-area transfer box 48 finished
[OK] Step 18 link-area transfer squid proxy 48 finished
[OK] Step 18 engineering vs link-area comparison finished
[OK] Step 18 existing mode regression finished
[OK] Step 18 artifact manifest finished
```

The test must verify CSV/JSON outputs:

```text
policy_sweep.csv has uniform / inverse_length / length
inverse_length policy row is stable
comparison.csv has engineering and link_area_experimental rows
comparison.csv has box_48 and squid_proxy_48 cases
link_area_experimental rows have finite bounded area_scale_final
all required stable rows satisfy rho/J/velocity bounds
artifact_summary.json has large_file_count == 0
logs/step18_pytest.log exists
```

The test must reject forbidden overclaims in docs/report:

```text
strict momentum-conserving FSI is complete
real squid simulation is validated
validated squid swimming
production-ready sharp-interface FSI
final surface-area reconstruction
```

## 11. Required Execution Order

Follow this sequence:

1. Re-read this goal file and inspect current `main`.
2. Confirm `external/taichi_LBM3D` is clean.
3. Add `tests/test_step18_link_area_transfer_contract.py` first and run it to confirm RED.
4. Add `FSIDriverConfig` reaction-transfer fields and validation.
5. Add `src/link_area_coupling.py`.
6. Wire `FSIDriver3D` to branch only the MPM reaction transfer path.
7. Export the new coupler in `src/__init__.py`.
8. Add Step 18 config files.
9. Add Step 18 common helpers and baseline runners.
10. Run the sanity baseline.
11. Run the area policy sweep.
12. Run the 48^3 box experimental baseline.
13. Run the 48^3 procedural squid_proxy experimental baseline.
14. Run the engineering-vs-link-area comparison.
15. Run existing-mode regression.
16. Generate artifact manifest.
17. Update docs and `STEP18_LINK_AREA_TRANSFER_REPORT.md`.
18. Run full `pytest -q` and save `logs/step18_pytest.log`.
19. Regenerate artifact manifest after pytest log exists.
20. Run final `pytest -q`.
21. Run `git diff --check`.
22. Confirm `git status --short external/taichi_LBM3D` is empty.
23. Commit all Step 18 code/docs/logs/outputs/report.
24. Push to GitHub `origin/main`.
25. Report commit hash, branch, verification commands, and key baseline numbers.

## 12. Required Commands

Use this Python interpreter unless it is unavailable:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore ...
```

Run baselines:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_policy_sweep_box_32.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_box_48.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_squid_proxy_48.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_compare_engineering_vs_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_regression_existing_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_artifact_manifest.py
```

Save logs with UTF-8 encoding. In Windows PowerShell, prefer:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_sanity.py 2>&1 | Out-File -FilePath logs\step18_link_area_transfer_sanity.log -Encoding utf8
```

Run pytest and save the required log:

```powershell
Set-Content -Path logs\step18_pytest.log -Value 'pytest started' -Encoding utf8
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q 2>&1 | Out-File -FilePath logs\step18_pytest.log -Encoding utf8
```

Then run a final non-logged check:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

## 13. Hard Acceptance Checklist

All items must be true before Step 18 is complete:

```text
[ ] main is on the Step 18 final commit
[ ] src/link_area_coupling.py exists
[ ] LinkAreaMovingBoundaryCoupler3D exists
[ ] FSIDriverConfig has reaction_transfer_mode
[ ] FSIDriverConfig default reaction_transfer_mode == engineering
[ ] link_area_experimental is opt-in only
[ ] engineering moving_boundary path remains available
[ ] moving bounce-back formula unchanged
[ ] MovingBoundaryFSICoupler3D unchanged
[ ] PenaltyFSICoupler3D unchanged
[ ] LBMFluid3D.step() default behavior unchanged
[ ] experimental transfer writes MPM reaction through solid.grid_f_ext
[ ] experimental transfer does not use lbm.cell_force
[ ] area_scale is finite and bounded
[ ] sanity baseline passes
[ ] area policy sweep passes
[ ] 48^3 box experimental transfer passes
[ ] 48^3 procedural squid_proxy experimental transfer passes
[ ] engineering vs link-area comparison passes
[ ] existing-mode regression passes
[ ] rho_min > 0.95 for required stable rows
[ ] rho_max < 1.05 for required stable rows
[ ] lbm_max_v < 0.1 for required stable rows
[ ] mpm_min_J > 0 for required stable rows
[ ] cell_force_max_norm == 0 for moving_boundary rows
[ ] active_reaction_particle_count > 0 for experimental rows
[ ] no NaN
[ ] no Inf
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no squid swimming validation claims
[ ] no mesh import
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count == 0
[ ] docs/17_experimental_link_area_transfer.md exists
[ ] STEP18_LINK_AREA_TRANSFER_REPORT.md complete
[ ] tests/test_step18_link_area_transfer_contract.py exists
[ ] logs/step18_pytest.log exists
[ ] pytest -q passes
[ ] git diff --check passes
[ ] Step 18 artifacts are committed
[ ] Step 18 artifacts are pushed to GitHub origin/main
```

## 14. Failure Handling

If the experimental transfer is unstable:

1. Do not loosen acceptance thresholds silently.
2. First reduce `reaction_scale`.
3. Then reduce `mb_force_cap_norm`.
4. Then narrow `area_scale_min` / `area_scale_max`, for example to `[0.5, 1.5]`.
5. Then reduce `n_lbm_steps` only if the report explicitly states the baseline became a shorter smoke baseline and cannot be used as full acceptance.
6. Preserve the engineering moving_boundary path and comparison evidence.
7. Document every deviation in `STEP18_LINK_AREA_TRANSFER_REPORT.md`.

If `squid_proxy` fails but box passes:

```text
Step 18 is not complete.
```

Either stabilize the procedural squid_proxy experimental settings or explicitly mark Step 18 blocked. Do not claim full acceptance.

If GPU or Taichi runtime fails:

```text
Step 18 is not complete.
```

Capture the exact error and do not commit a misleading passed report.

If `external/taichi_LBM3D` is modified:

```text
Step 18 is not complete.
```

Revert only the unintended external edits if they were made by this task. Never revert unrelated user changes without explicit permission.

## 15. Completion Definition

Step 18 is complete only when:

1. All required source changes are implemented.
2. All required baseline scripts exist.
3. All required configs exist.
4. All required baselines pass at the specified sizes.
5. Existing engineering moving_boundary behavior is proven still stable.
6. `pytest -q` passes.
7. `logs/step18_pytest.log` exists and records the passing pytest result.
8. Artifact manifest exists and reports `large_file_count == 0`.
9. Documentation and report are complete and avoid forbidden overclaims.
10. `external/taichi_LBM3D` remains unchanged.
11. Step 18 code/docs/logs/outputs/report are committed.
12. The commit is pushed to GitHub `origin/main`.
13. The final response reports the commit hash and remote branch.

## 16. Decision After Step 18

If Step 18 passes, the recommended Step 19 is:

```text
Step 19: Experimental link-area transfer long-run and 64^3 feasibility
```

Do not jump directly to real squid validation or mesh-based squid swimming until the experimental transfer has long-run evidence comparable to Step 16.
