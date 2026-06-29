# Step155 Goal: Official Tutorial Solver V1

## Source Contract

Step155 follows remote `origin/main` after Step154 commit:

```text
0a1cc4e465b3a2b0360ca2c372717d67dce4e532
```

Step154 completed the official solver pre/post pipeline and produced the
canonical compiled case:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
```

Step154 key state:

```json
{
  "step": 154,
  "status": "official_solver_prepost_pipeline_ready",
  "compiled_case_ready_for_step155": true,
  "preprocessor_ready": true,
  "postprocessor_ready": true,
  "official_tutorial_constants_loaded": true,
  "solver_input_case_written": true,
  "geometry_masks_written": true,
  "boundary_masks_written": true,
  "fsi_interface_masks_written": true,
  "monitor_point_mapped": true,
  "geometry_preview_written": true,
  "step155_solver_run_allowed": true,
  "solver_run_executed": false,
  "fluent_run_executed": false,
  "step150_executed": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Step155 must consume the Step154 compiled case directly and run the repository
solver over the public official tutorial time window. Step155 is the first
post-Step154 real solver implementation step. It must not use Step148 or
Step153 helper functions as the primary runner.

## Objective

Implement `Step155 Official Tutorial Solver V1`.

Step155 must run the repository `FSIDriver3D` solver directly from:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
```

It must execute:

```text
50 FSI steps
dt = 0.0005 s
total time = 0.025 s
```

It must emit solver monitor data, force monitor data, stability diagnostics,
mass/flux diagnostics, and velocity snapshots for Step156 postprocessing.

Step155 still does not claim Fluent validation. Official comparison remains
blocked unless a private official monitor is supplied.

## Non-Goals

Step155 must not:

```text
- run Fluent
- import private Fluent mesh files
- fabricate official monitor data
- run Step150 error localization
- run Step151 targeted fix
- run Step152 apply gate
- run Step148 helper as the primary runner
- run Step153 helper as the primary runner
- run selected96
- claim Fluent validation
- claim Figure 29.3 parity
- claim official mesh reproduction
```

Step155 may instantiate `FSIDriver3D` directly. That is required. It must not
call:

```text
create_fluent_official_proxy_fsi_config
run_our_solver_fsi_case
extract_solver_monitors
run_step148_reproduction
run_step153_official_tutorial_setup_parity
```

## Required Files

Create:

```text
docs/campaigns/fluent_duct_flap/steps/155/goal.md
docs/campaigns/fluent_duct_flap/steps/155/report.md
experiments/steps/step155_official_tutorial_solver_v1.py
src/mpm_lbm/solvers/__init__.py
src/mpm_lbm/solvers/official_duct_flap_config.py
src/mpm_lbm/solvers/official_duct_flap_solver.py
src/mpm_lbm/solvers/official_duct_flap_io.py
tests/test_step155_official_tutorial_solver_v1_contract.py
```

Edit:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
```

Only the boundary report/scope-note bug is allowed in `fsi_driver.py` unless a
test proves an additional Step155 blocker.

## Required Inputs

Step155 must consume:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
outputs/step154_official_solver_prepost_pipeline/geometry_masks.npz
outputs/step154_official_solver_prepost_pipeline/boundary_masks.npz
outputs/step154_official_solver_prepost_pipeline/fsi_interface_masks.npz
```

Step155 must fail fast if:

```text
compiled_case.status != compiled_case_ready_for_step155
compiled_case.step != 154
official_tutorial_time_steps != 50
official_tutorial_dt_s != 0.0005
official_tutorial_total_time_s != 0.025
boundary_condition_spec.inlet != velocity_inlet
boundary_condition_spec.outlet != pressure_outlet
lbm_boundary_semantics_required_for_step155.legacy_all_population_reset_allowed != false
minimum_open_boundary_semantics != regularized_velocity_pressure_limited
```

## Required Runner

Add executable module:

```text
experiments/steps/step155_official_tutorial_solver_v1.py
```

Default command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step155_official_tutorial_solver_v1 `
  --case outputs\step154_official_solver_prepost_pipeline\compiled_case.json `
  --output-dir outputs\step155_official_tutorial_solver_v1 `
  --force
```

Required CLI arguments:

```text
--case
--output-dir
--force
```

Optional CLI arguments:

```text
--raw-output-dir
--n-particles
--target-u-lbm
--snapshot-interval
--monitor-interval
--taichi-arch
--cpu-max-num-threads
--allow-test-grid-override
--test-grid
--test-n-steps
```

Default values:

```json
{
  "n_particles": 1024,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "snapshot_interval": 5,
  "monitor_interval": 1,
  "taichi_arch": "cpu",
  "cpu_max_num_threads": 1,
  "allow_test_grid_override": false
}
```

The committed Step155 artifact must be generated with the real Step154 48^3
compiled case, not the test-grid override.

## Required Output Artifacts

Write:

```text
outputs/step155_official_tutorial_solver_v1/
  compiled_case_consumed.json
  generated_geometry_config.json
  solver_driver_config.json
  solver_run_manifest.json
  case_to_driver_geometry_report.json
  boundary_semantics_runtime_report.json
  unit_mapping_report.json
  solver_timeseries.csv
  solver_monitor.csv
  solver_force_monitor.csv
  stability_timeseries.csv
  mass_flux_timeseries.csv
  velocity_snapshots/
    velocity_snapshot_step000.npz
    velocity_snapshot_step005.npz
    velocity_snapshot_step010.npz
    velocity_snapshot_step015.npz
    velocity_snapshot_step020.npz
    velocity_snapshot_step025.npz
    velocity_snapshot_step030.npz
    velocity_snapshot_step035.npz
    velocity_snapshot_step040.npz
    velocity_snapshot_step045.npz
    velocity_snapshot_step050.npz
  solver_v1_summary.json
  physics_gap_report.json
  report.md
```

Raw `FSIDriver3D` outputs may go under:

```text
outputs/tmp/step155_official_tutorial_solver_v1_driver_raw/
```

Do not commit large raw arrays outside the intended compact snapshot payloads.

## Required Runtime Design

Step155 must not call `driver.run()` blindly if that prevents per-step
flux/snapshot capture.

Preferred implementation:

```python
driver = FSIDriver3D(config, out_dir=str(raw_output_dir))
driver.initialize()

collect step 0 diagnostics
write step 0 monitor/stability/flux rows
write step 0 velocity snapshot

for step in range(1, 51):
    driver.step_once()
    driver.collect_diagnostics(driver.current_lbm_step)
    write monitor row
    write force row
    write stability row
    write mass/flux row
    if step % snapshot_interval == 0 or step == 50:
        write velocity snapshot

driver.export_outputs(driver.current_lbm_step)
driver.save_timeseries()
```

The implementation may wrap existing driver functions but must own the Step155
loop so `mass_flux_timeseries.csv` and snapshots are synchronized with
Step155's accepted output cadence.

## Required Taichi Initialization

Implement local initialization in Step155:

```python
ti.init(arch=ti.cpu, cpu_max_num_threads=1)
```

Do not import `_ensure_taichi()` from Step148. If Taichi is already
initialized and re-init raises or warns, Step155 must handle this
deterministically in tests. Do not hide failed solver execution.

## Generated Geometry Config

Step155 must generate `generated_geometry_config.json` from the Step154
compiled case. It must be a valid `GeometryConfig` payload with:

```json
{
  "geometry_type": "duct_flap_proxy",
  "n_particles": 1024,
  "duct": {"x": [0.0, 1.0], "y": [0.3, 0.7], "z": [0.45, 0.55]},
  "flap": {
    "anchor_x": 0.505,
    "anchor_y": 0.3,
    "height_over_duct_height": 0.25,
    "thickness_over_duct_height": 0.075,
    "normalized_height": 0.10,
    "normalized_thickness": 0.03,
    "z": [0.45, 0.55],
    "fixed_base": true,
    "mirrored_pair": false
  },
  "material_reference": {
    "density": 1600.0,
    "youngs_modulus": 1000000.0,
    "poisson_ratio": 0.47,
    "used_for_mpm_config": true,
    "used_for_exact_structural_model": false
  },
  "dimensional_reference": {
    "duct_length_m": 0.10,
    "duct_height_m": 0.04,
    "flap_height_m": 0.01,
    "flap_thickness_m": 0.003,
    "inlet_velocity_mps": 10.0,
    "official_transient_steps": 50,
    "transient_dt_s": 0.0005
  },
  "monitor_reference": {
    "flap_tip_monitor_enabled": true,
    "monitor_is_direct_fluent_equivalent": false,
    "monitor_point_m": [0.0505, 0.0095]
  },
  "p_rho": 1600.0,
  "particles_per_axis_hint": 48,
  "quality_check_enabled": true,
  "quality_check_strict": false
}
```

Step155 must not simply point at
`configs/step104_fluent_duct_flap_geometry_1024.json`. It may use that file as
historical reference in tests, but the default Step155 run must generate
geometry config from `compiled_case.json`.

## Case-To-Driver Geometry Report

Write `case_to_driver_geometry_report.json` with:

```json
{
  "step": 155,
  "status": "case_geometry_mapped_to_driver_config",
  "compiled_case_path": "outputs/step154_official_solver_prepost_pipeline/compiled_case.json",
  "generated_geometry_config_path": "outputs/step155_official_tutorial_solver_v1/generated_geometry_config.json",
  "official_mesh_imported": false,
  "proxy_geometry_used": true,
  "step154_geometry_masks_loaded": true,
  "driver_static_lbm_geometry_includes_flap": false,
  "flap_represented_by_mpm_particles": true,
  "static_duct_geometry_compatible_with_step154_duct_context": true,
  "geometry_equivalence_claim_allowed": false,
  "validation_claim_allowed": false
}
```

Current `FSIDriver3D` static LBM geometry writes duct walls from
`duct_flap_proxy_static_geometry(...)` and represents the flap through
MPM/moving-boundary projection. Step155 must not pretend the Step154
`flap_solid_mask` is a static LBM wall.

## FSIDriverConfig Construction

Implement in `src/mpm_lbm/solvers/official_duct_flap_config.py`:

```python
load_compiled_case(case_path: Path) -> dict
validate_compiled_case_for_step155(compiled_case: dict) -> None
write_generated_geometry_config(compiled_case: dict, output_dir: Path, n_particles: int) -> Path
build_step155_fsi_driver_config(
    compiled_case: dict,
    geometry_config_path: Path,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    monitor_interval: int = 1,
) -> FSIDriverConfig
```

Required `FSIDriverConfig` values:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "duct_flap_proxy",
  "n_grid": 48,
  "n_particles": 1024,
  "n_lbm_steps": 50,
  "mpm_dt": 0.0005,
  "mpm_substeps_per_lbm_step": 1,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "initial_solid_velocity_norm": [0.0, 0.0, 0.0],
  "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
  "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
  "open_boundary_limiter_enabled": true,
  "open_boundary_rho_min": 0.8,
  "open_boundary_rho_max": 1.2,
  "open_boundary_u_max": 0.1,
  "open_boundary_noneq_cap": 0.05,
  "velocity_inlet_axis": "x",
  "velocity_inlet_side": "min",
  "pressure_outlet_side": "max",
  "physical_duct_length_m": 0.1,
  "target_inlet_velocity_mps": 10.0,
  "official_fsi_dt_s": 0.0005,
  "target_u_lbm_for_dimensional_mapping": 0.02,
  "fluid_density_kg_m3": 1.225,
  "fluid_kinematic_viscosity_m2_s": 1.5e-5,
  "lbm_viscosity_semantics": "legacy_external",
  "lbm_tau_stability_policy": "report_only",
  "reaction_transfer_mode": "engineering",
  "solid_model": "finite_deformation_mpm",
  "solid_dimensionality": "three_dimensional",
  "flow_dimensionality_mode": "three_dimensional",
  "fluent_like_monitor_enabled": true,
  "fluent_like_monitor_physical_point_m": [0.0505, 0.0095],
  "fluent_like_monitor_nearest_count": 8,
  "output_interval": 1,
  "quality_check_enabled": true,
  "quality_check_strict": false,
  "write_particles": false,
  "write_vtk": false
}
```

Do not use `physical_nu_mapping` in the Step155 default. Physical-Re parity
remains blocked unless a later tau-margin path is explicitly proven.

## Required FSIDriver Reporting Fix

Fix `src/mpm_lbm/sim/drivers/fsi_driver.py` so both semantics are treated as
unknown-population reconstruction modes:

```text
regularized_velocity_pressure
regularized_velocity_pressure_limited
```

Required behavior in `duct_boundary_condition_report.json` for limited mode:

```json
{
  "all_population_equilibrium_reset_used": false,
  "unknown_population_reconstruction_used": true,
  "open_boundary_limiter_enabled": true,
  "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
  "lbm_open_boundary_scope_note": "opt-in D3Q19 x-axis unknown-population reconstruction with limiter; not a Fluent pressure-based open-boundary equivalence claim"
}
```

Do not change solver physics in this edit unless a failing test proves the
existing code is not applying the limited boundary. This is a report
correctness fix.

## Solver Runtime Implementation

Implement in `src/mpm_lbm/solvers/official_duct_flap_solver.py`:

```python
run_official_tutorial_solver_v1(
    compiled_case_path: Path,
    output_dir: Path,
    raw_output_dir: Path | None = None,
    force: bool = False,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    snapshot_interval: int = 5,
    monitor_interval: int = 1,
) -> dict

run_driver_with_step155_capture(
    driver: FSIDriver3D,
    compiled_case: dict,
    output_dir: Path,
    snapshot_interval: int,
) -> dict
```

The solver loop must capture:

```text
- solver diagnostics at step 0 and every solver step through 50
- flap-tip monitor rows
- official-point-like monitor rows if available
- force proxy rows
- density/min/max/max velocity stability rows
- inlet flux
- outlet flux
- midplane flux
- x-plane flux profile at final step
- velocity snapshots at step 0, 5, 10, ..., 50
```

## CSV Fields

`solver_timeseries.csv` fields:

```text
step
time_s
rho_min
rho_max
lbm_max_v
fluid_mean_ux
projection_zone_fluid_mean_ux
far_field_fluid_mean_ux
solid_mean_vx_norm
mpm_min_J
mpm_max_speed
projected_mass
active_cell_count
cell_force_max_norm
hydro_force_max_norm
bb_link_count
bb_max_correction
mb_subcycle_force_sample_count
mb_subcycle_force_accum_norm_max
mb_subcycle_force_mean_norm_max
active_reaction_particle_count
max_grid_reaction_norm
```

`solver_monitor.csv` fields:

```text
time_s
step
flap_tip_total_displacement_m
flap_tip_x_displacement_m
flap_tip_y_displacement_m
flap_tip_velocity_m_per_s
official_point_like_total_displacement_m
official_point_like_x_displacement_m
official_point_like_y_displacement_m
official_point_like_z_displacement_m
official_point_like_particle_count
fluid_force_x_n
fluid_force_y_n
fluid_force_magnitude_n
```

Use the driver's flap-tip and fluent-like monitor rows where available. The
`official_point_like_*` fields are proxy monitor values and must be reported as
not direct Fluent equivalence.

`solver_force_monitor.csv` fields:

```text
time_s
step
fluid_force_x_n
fluid_force_y_n
fluid_force_magnitude_n
force_proxy_source
force_is_direct_fluent_wall_integral
```

`stability_timeseries.csv` fields:

```text
step
time_s
rho_min
rho_max
rho_finite
velocity_finite
population_finite
lbm_max_v
mpm_min_J
mpm_max_speed
density_gate_pass_step
mpm_j_gate_pass_step
finite_gate_pass_step
```

`mass_flux_timeseries.csv` fields:

```text
step
time_s
total_fluid_mass
mass_delta_rel
inlet_flux
outlet_flux
midplane_flux
flux_imbalance_rel
outlet_to_inlet_flux_ratio
midplane_to_inlet_flux_ratio
```

Flux must be computed from `rho * ux` over the Step154 boundary masks when
possible. If a mask/solver-grid mismatch occurs, fail fast.

## Velocity Snapshot Format

Each snapshot NPZ must include:

```text
velocity
rho
solid
speed
ux
uy
uz
step
time_s
compiled_case_path
validation_claim_allowed
```

Required shapes:

```text
velocity: (nx, ny, nz, 3)
rho:      (nx, ny, nz)
solid:    (nx, ny, nz)
speed:    (nx, ny, nz)
ux:       (nx, ny, nz)
uy:       (nx, ny, nz)
uz:       (nx, ny, nz)
```

All snapshots must be finite on fluid cells. If not finite, Step155 must fail
and write a failure summary.

## Runtime Reports

`solver_run_manifest.json` must record Step155, compiled case path, generated
geometry config path, solver driver config path, `driver_class = FSIDriver3D`,
`step148_helper_used = false`, `step153_helper_used = false`,
`n_steps_requested = 50`, `dt_s = 0.0005`, `target_time_end_s = 0.025`,
snapshot/monitor intervals, and `validation_claim_allowed = false`.

`boundary_semantics_runtime_report.json` must be read from the driver's actual
`duct_boundary_condition_report.json`, not only from requested config, and must
record velocity inlet active, pressure outlet active, legacy reset false,
unknown reconstruction true, limiter true, limited semantics, and no validation
claim.

`unit_mapping_report.json` must be report-only and record physical duct length,
duct height, target inlet velocity, official dt, target `u_lbm`, legacy
viscosity semantics, physical Reynolds parity blocked, tau-margin validation
still required, and no validation claim.

`physics_gap_report.json` must report:

```json
{
  "step": 155,
  "status": "physics_gaps_reported",
  "solver_pipeline_stage": "real_solver_run",
  "fluid_solver": "LBM",
  "solid_solver": "finite_deformation_mpm",
  "coupling_mode": "moving_boundary",
  "official_structural_model": "Fluent intrinsic FSI / FEM-like structural model",
  "official_dynamic_mesh_model": "linearly elastic dynamic mesh smoothing",
  "our_dynamic_mesh_equivalent": "moving-boundary/proxy coupling on fixed LBM grid",
  "official_mesh_imported": false,
  "proxy_geometry_used": true,
  "official_monitor_loaded": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false
}
```

## Summary Contract

Write `solver_v1_summary.json`.

Required success fields:

```json
{
  "step": 155,
  "status": "official_tutorial_solver_v1_run_complete",
  "solver_v1_run_executed": true,
  "compiled_case_consumed": true,
  "compiled_case_ready_for_step155": true,
  "step148_helper_used": false,
  "step153_helper_used": false,
  "driver_class": "FSIDriver3D",
  "n_steps_requested": 50,
  "n_steps_completed": 50,
  "time_end_s": 0.025,
  "official_tutorial_time_steps": 50,
  "official_tutorial_dt_s": 0.0005,
  "official_tutorial_total_time_s": 0.025,
  "time_window_matches_official_tutorial": true,
  "velocity_inlet_active": true,
  "pressure_outlet_active": true,
  "legacy_all_population_reset_used": false,
  "unknown_population_reconstruction_used": true,
  "open_boundary_limiter_enabled": true,
  "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
  "solver_monitor_rows": 51,
  "solver_force_monitor_rows": 51,
  "stability_rows": 51,
  "mass_flux_rows": 51,
  "velocity_snapshot_count": 11,
  "final_velocity_snapshot_written": true,
  "monitor_displacement_finite": true,
  "force_monitor_finite": true,
  "density_gate_pass": true,
  "finite_gate_pass": true,
  "mpm_j_gate_pass": true,
  "mass_flux_reported": true,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

On failure, write the same file with:

```json
{
  "status": "official_tutorial_solver_v1_run_failed",
  "failure_stage": "...",
  "error_type": "...",
  "error_message": "...",
  "solver_v1_run_executed": false,
  "validation_claim_allowed": false
}
```

The runner exit code must be nonzero on failure.

## Density / Stability Gates

Step155 accepted success requires:

```text
all finite numeric monitor values
all finite velocity/rho fields on fluid cells
rho_min > 0
rho_max < 5
mpm_min_J > 0
n_steps_completed == 50
time_end_s == 0.025
```

These are solver-execution sanity gates, not Fluent validation gates.

## Tests

Add `tests/test_step155_official_tutorial_solver_v1_contract.py` with at least:

1. Config builder consumes committed Step154 compiled case and produces
   `FSIDriverConfig` with 48 grid, 50 steps, `mpm_dt = 0.0005`,
   `duct_velocity_inlet_pressure_outlet`, `regularized_velocity_pressure_limited`,
   limiter enabled, `target_inlet_velocity_mps = 10.0`, and
   `official_fsi_dt_s = 0.0005`.
2. Generated geometry config contract: duct/flap/material/dimensional metadata
   are generated from compiled case and `used_for_mpm_config = true`.
3. No Step148/Step153 helper usage: Step155 source must not contain the helper
   names listed above, but may contain `FSIDriver3D`.
4. Boundary report fix: `regularized_velocity_pressure_limited` is reported as
   unknown-population reconstruction with legacy all-population reset false.
5. Committed artifact schema: required JSON/CSV/NPZ artifacts exist after the
   real Step155 run.
6. Real run summary contract: committed artifacts show complete 48^3 / 50-step
   run, 51 monitor/force/stability/flux rows, 11 snapshots, no helper usage, no
   validation claim.

If runtime cost is too high for pytest, tests may inspect committed artifacts
instead of rerunning the 50-step case. A tiny smoke may run with explicit
`--allow-test-grid-override`, but the committed artifact must be the real 48^3
/ 50-step Step155 run.

## Required Execution Command

Run real Step155:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step155_official_tutorial_solver_v1 `
  --case outputs\step154_official_solver_prepost_pipeline\compiled_case.json `
  --output-dir outputs\step155_official_tutorial_solver_v1 `
  --force
```

## Required Verification Commands

Focused test:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step155_official_tutorial_solver_v1_contract.py
```

Adjacent regression:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step153_official_tutorial_setup_parity_contract.py `
  tests\test_step154_official_solver_prepost_pipeline_contract.py `
  tests\test_step155_official_tutorial_solver_v1_contract.py
```

Compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step155_official_tutorial_solver_v1.py `
  src\mpm_lbm\solvers\official_duct_flap_config.py `
  src\mpm_lbm\solvers\official_duct_flap_solver.py `
  src\mpm_lbm\solvers\official_duct_flap_io.py `
  src\mpm_lbm\sim\drivers\fsi_driver.py
```

Also run JSON parse, CSV header, Step050 snapshot checks, and:

```powershell
git diff --check
```

## Documentation Updates

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
README.md
docs/campaigns/fluent_duct_flap/steps/155/report.md
```

Required status language:

```text
Step155 consumed the Step154 compiled case directly and ran the repository
FSIDriver3D path for the public official tutorial window of 50 steps at
dt = 0.0005 s, total time 0.025 s.

Step155 did not call Step148 or Step153 helper runners as the primary runner.
Step155 did not run Fluent. Step155 did not load or fabricate official monitor
data. Step155 did not run Step150. Step155 did not run selected96 and does not
make a validation claim.

Step156 is the next step. It must consume Step155 solver outputs and produce
the official-style velocity plots, ux/uy diagnostics, stream/quiver plot,
monitor plots, flux profiles, solver acceptance report, and official comparison
placeholder/report.
```

## Acceptance Criteria

Step155 is accepted only if `solver_v1_summary.json` records:

```json
{
  "step": 155,
  "status": "official_tutorial_solver_v1_run_complete",
  "solver_v1_run_executed": true,
  "compiled_case_consumed": true,
  "step148_helper_used": false,
  "step153_helper_used": false,
  "driver_class": "FSIDriver3D",
  "n_steps_completed": 50,
  "time_end_s": 0.025,
  "velocity_inlet_active": true,
  "pressure_outlet_active": true,
  "legacy_all_population_reset_used": false,
  "unknown_population_reconstruction_used": true,
  "open_boundary_limiter_enabled": true,
  "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
  "solver_monitor_rows": 51,
  "solver_force_monitor_rows": 51,
  "stability_rows": 51,
  "mass_flux_rows": 51,
  "velocity_snapshot_count": 11,
  "final_velocity_snapshot_written": true,
  "monitor_displacement_finite": true,
  "force_monitor_finite": true,
  "density_gate_pass": true,
  "finite_gate_pass": true,
  "mpm_j_gate_pass": true,
  "mass_flux_reported": true,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

## Next Step After Step155

After Step155 passes, Step156 must implement:

```text
Official Tutorial Postprocess And Solver Acceptance
```

Step156 must consume:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
outputs/step155_official_tutorial_solver_v1/
```

and produce:

```text
velocity_magnitude_step050.png
velocity_ux_step050.png
velocity_uy_step050.png
streamline_or_quiver_step050.png
geometry_overlay_step050.png
centerline_velocity_profile.csv
x_plane_flux_profile.csv
monitor_displacement_plot.png
force_monitor_plot.png
postprocess_summary.json
solver_acceptance_report.json
official_comparison_report.json
```

If `official_monitor.csv` is absent, Step156's official comparison report must
record:

```json
{
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false
}
```
