# Step157 Goal: Official Subcycled Flow Development Repair

## Source Contract

Step157 follows remote `origin/main` after Step156 commit:

```text
30f85f8d8d192771e2577b862fa35810029ad1bc
```

Step156 completed the preprocess -> solve -> postprocess pipeline and produced
velocity plots, monitor plots, centerline/x-plane flux profiles, solver
acceptance, and official comparison status. Step156 also exposed that flow
development failed:

```json
{
  "step": 156,
  "status": "official_tutorial_postprocess_complete",
  "postprocess_complete": true,
  "solver_pipeline_complete": true,
  "postprocess_acceptance_pass": true,
  "solver_numerical_sanity_pass": true,
  "flow_development_gate_reported": true,
  "flow_development_gate_pass": false,
  "inlet_flux_tail_mean": 1.64673269197663,
  "outlet_flux_tail_mean": -8.246116412041075e-05,
  "outlet_to_inlet_flux_ratio_tail_mean": -5.006163707054121e-05,
  "flux_imbalance_rel_tail_mean": -1.0000500616370704,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

This means the next step is no longer a plotting or official-monitor step. The
highest-priority repair hypothesis is a time-scale/subcycling mismatch in the
Step155 solver run.

Step155 ran:

```text
50 official steps
dt = 0.0005 s
total official monitor time = 0.025 s
```

but the Step155 driver config used:

```text
fsi_exchange_mode = one_lbm_step_per_fsi_step
lbm_substeps_per_fsi_step = 1
```

For the Step154/Step155 dimensional velocity mapping, one LBM step per official
FSI step is not enough.

## Objective

Implement:

```text
Step157 Official Subcycled Flow Development Repair
```

Step157 must diagnose the Step155/Step156 flow-development failure as a
time-scale/subcycling mismatch candidate, then run the same Step154 official
tutorial proxy case with LBM subcycling inside each official FSI step.

For the current `48^3` grid:

```text
duct_length_m = 0.1
n_grid = 48
dx_m = 0.1 / 48 = 0.0020833333333333333

target_u_lbm = 0.02
target_inlet_velocity_mps = 10.0

lbm_dt_phys_s = target_u_lbm * dx_m / target_inlet_velocity_mps
              = 4.166666666666667e-6

official_fsi_dt_s = 0.0005

lbm_substeps_per_fsi_step = official_fsi_dt_s / lbm_dt_phys_s
                          = 120
```

Step157 must run:

```text
50 official FSI steps
120 LBM substeps per official FSI step
6000 total LBM substeps
official time end = 0.025 s
```

Step157 is a solver-repair evidence step. It must not claim Fluent validation
or Figure 29.3 parity.

## Non-Goals

Step157 must not:

```text
- run Fluent
- import private Fluent mesh files
- fabricate official monitor data
- run Step150/151/152
- run selected96
- claim Fluent validation
- claim Figure 29.3 parity
- claim official mesh reproduction
- change official tutorial geometry constants
- hide flow-development failure if subcycling is insufficient
```

Step157 may instantiate `FSIDriver3D` directly. It may reuse generic solver and
postprocessing helpers, but it must not call prior experiment runners as the
primary execution path.

Forbidden experiment-runner calls:

```text
run_step148_reproduction
run_step153_official_tutorial_setup_parity
run_official_tutorial_solver_v1
run_step156_postprocess
step150_official_monitor_intake
fluent.exe
subprocess
```

Allowed lower-level surfaces:

```text
FSIDriver3D
FSIDriverConfig
Step154 compiled case readers
generic CSV/JSON/NPZ writers
generic velocity-render/profile helpers that do not rerun the solver
```

## Required New Files

Create:

```text
docs/campaigns/fluent_duct_flap/steps/157/goal.md
docs/campaigns/fluent_duct_flap/steps/157/report.md

experiments/steps/step157_official_subcycled_flow_development_repair.py

src/mpm_lbm/solvers/official_subcycled_flow_config.py
src/mpm_lbm/solvers/official_subcycled_flow_solver.py
src/mpm_lbm/solvers/official_subcycled_flow_diagnostics.py

tests/test_step157_official_subcycled_flow_development_contract.py
```

You may edit existing generic modules only if required for reuse:

```text
src/mpm_lbm/solvers/official_duct_flap_config.py
src/mpm_lbm/solvers/official_duct_flap_io.py
src/mpm_lbm/postprocessing/fluent_duct_flap_velocity_render.py
src/mpm_lbm/postprocessing/fluent_duct_flap_acceptance.py
```

Do not edit low-level LBM/MPM physics unless a Step157 test proves a real
solver bug. Step157's primary repair is FSI/LBM subcycling, not a new boundary
model.

## Required Inputs

Step157 must read:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
outputs/step154_official_solver_prepost_pipeline/geometry_masks.npz
outputs/step154_official_solver_prepost_pipeline/boundary_masks.npz
outputs/step154_official_solver_prepost_pipeline/fsi_interface_masks.npz

outputs/step155_official_tutorial_solver_v1/solver_v1_summary.json
outputs/step155_official_tutorial_solver_v1/mass_flux_timeseries.csv
outputs/step155_official_tutorial_solver_v1/velocity_snapshots/velocity_snapshot_step050.npz

outputs/step156_official_tutorial_postprocess_and_acceptance/postprocess_summary.json
outputs/step156_official_tutorial_postprocess_and_acceptance/solver_acceptance_report.json
outputs/step156_official_tutorial_postprocess_and_acceptance/x_plane_flux_profile.csv
```

Optional:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

The optional official monitor must not be required for Step157.

## Required Runner

Add executable module:

```text
experiments/steps/step157_official_subcycled_flow_development_repair.py
```

Default command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step157_official_subcycled_flow_development_repair `
  --case outputs\step154_official_solver_prepost_pipeline\compiled_case.json `
  --step155-root outputs\step155_official_tutorial_solver_v1 `
  --step156-root outputs\step156_official_tutorial_postprocess_and_acceptance `
  --output-dir outputs\step157_official_subcycled_flow_development_repair `
  --force
```

Required CLI arguments:

```text
--case
--step155-root
--step156-root
--output-dir
--force
```

Optional CLI arguments:

```text
--raw-output-dir
--n-particles
--target-u-lbm
--official-steps
--official-dt-s
--lbm-substeps-per-fsi-step
--snapshot-official-steps
--monitor-interval
--tail-fraction
--taichi-arch
--cpu-max-num-threads
--max-wall-seconds
--allow-test-grid-override
--test-grid
--test-official-steps
--test-lbm-substeps-per-fsi-step
```

Defaults:

```json
{
  "n_particles": 1024,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "official_steps": 50,
  "official_dt_s": 0.0005,
  "lbm_substeps_per_fsi_step": 120,
  "snapshot_official_steps": [0, 5, 10, 20, 30, 40, 50],
  "monitor_interval": 1,
  "tail_fraction": 0.2,
  "taichi_arch": "cpu",
  "cpu_max_num_threads": 1,
  "max_wall_seconds": null,
  "allow_test_grid_override": false
}
```

The committed Step157 default artifact must be generated from the real Step154
`48^3` compiled case unless the full run fails. If the full run fails, commit an
honest failure artifact and do not mark the repair as successful.

## Required Output Artifacts

Write:

```text
outputs/step157_official_subcycled_flow_development_repair/
  step157_time_scale_diagnosis.json
  step157_subcycle_config_report.json
  generated_geometry_config.json
  solver_driver_config.json
  solver_run_manifest.json

  subcycled_solver_timeseries.csv
  subcycled_solver_monitor.csv
  subcycled_solver_force_monitor.csv
  subcycled_stability_timeseries.csv
  subcycled_mass_flux_timeseries.csv

  velocity_snapshots/
    velocity_snapshot_step000.npz
    velocity_snapshot_step005.npz
    velocity_snapshot_step010.npz
    velocity_snapshot_step020.npz
    velocity_snapshot_step030.npz
    velocity_snapshot_step040.npz
    velocity_snapshot_step050.npz

  x_plane_flux_profile_step050.csv
  official_style_velocity_cloud_step050.png
  velocity_magnitude_step050.png
  velocity_ux_step050.png
  velocity_uy_step050.png

  flow_development_comparison_report.json
  solver_acceptance_report.json
  official_comparison_status_report.json
  step157_summary.json
  report.md
```

Raw driver outputs may go under:

```text
outputs/tmp/step157_official_subcycled_flow_development_driver_raw/
```

Do not commit large raw transient arrays outside compact snapshots and
CSV/JSON/PNG artifacts.

## Time-Scale Diagnosis Requirement

Implement in:

```text
src/mpm_lbm/solvers/official_subcycled_flow_diagnostics.py
```

Required function names:

```python
compute_required_lbm_substeps(compiled_case: dict, target_u_lbm: tuple[float, float, float]) -> dict
diagnose_step155_time_scale(step155_summary: dict, step156_acceptance: dict, compiled_case: dict) -> dict
summarize_step156_flux_failure(step156_x_flux_csv: Path, step156_acceptance: dict) -> dict
build_flow_development_comparison_report(step156_acceptance: dict, subcycled_mass_flux_csv: Path, output_path: Path, tail_fraction: float = 0.2) -> dict
```

Write `step157_time_scale_diagnosis.json` with computed fields:

```json
{
  "step": 157,
  "status": "time_scale_mismatch_diagnosed",
  "source_step155_status": "official_tutorial_solver_v1_run_complete",
  "source_step156_status": "official_tutorial_postprocess_complete",
  "duct_length_m": 0.1,
  "n_grid": 48,
  "dx_phys_m": 0.0020833333333333333,
  "target_u_lbm": 0.02,
  "target_inlet_velocity_mps": 10.0,
  "lbm_dt_phys_s": 4.166666666666667e-6,
  "official_fsi_dt_s": 0.0005,
  "required_lbm_substeps_per_fsi_step": 120,
  "required_total_lbm_substeps_for_50_official_steps": 6000,
  "step155_lbm_substeps_per_fsi_step": 1,
  "step155_total_lbm_substeps": 50,
  "step155_subcycling_deficit_factor": 120,
  "step156_flow_development_gate_pass": false,
  "validation_claim_allowed": false
}
```

Numeric values must be computed from Step154/155/156 artifacts, except expected
official constants.

## Subcycled Configuration Requirement

Implement in:

```text
src/mpm_lbm/solvers/official_subcycled_flow_config.py
```

Required function names:

```python
load_compiled_case_for_step157(case_path: Path) -> dict
validate_step157_inputs(compiled_case: dict, step155_summary: dict, step156_summary: dict) -> None
build_step157_subcycled_geometry_config(compiled_case: dict, output_dir: Path, n_particles: int) -> Path
build_step157_subcycled_fsi_config(compiled_case: dict, geometry_config_path: Path, n_particles: int = 1024, target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0), lbm_substeps_per_fsi_step: int | None = None) -> FSIDriverConfig
```

The resulting `FSIDriverConfig` must include:

```text
coupling_mode = moving_boundary
geometry_type = duct_flap_proxy
n_grid = 48
n_particles = 1024
n_lbm_steps = 50
mpm_dt = 0.0005
mpm_substeps_per_lbm_step = 1
fsi_exchange_mode = lbm_subcycled_per_fsi_step
lbm_substeps_per_fsi_step = 120
lbm_dt_phys_override_s = 4.166666666666667e-6
target_u_lbm = [0.02, 0.0, 0.0]
target_u_lbm_for_dimensional_mapping = 0.02
target_inlet_velocity_mps = 10.0
physical_duct_length_m = 0.1
official_fsi_dt_s = 0.0005
lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet
lbm_open_boundary_semantics = regularized_velocity_pressure_limited
open_boundary_limiter_enabled = true
open_boundary_rho_min = 0.8
open_boundary_rho_max = 1.2
open_boundary_u_max = 0.1
open_boundary_noneq_cap = 0.05
velocity_inlet_axis = x
velocity_inlet_side = min
pressure_outlet_side = max
fluid_density_kg_m3 = 1.225
fluid_kinematic_viscosity_m2_s = 1.5e-5
lbm_viscosity_semantics = legacy_external
lbm_tau_stability_policy = report_only
reaction_transfer_mode = engineering
solid_model = finite_deformation_mpm
solid_dimensionality = three_dimensional
flow_dimensionality_mode = three_dimensional
fluent_like_monitor_enabled = true
fluent_like_monitor_physical_point_m = [0.0505, 0.0095]
fluent_like_monitor_nearest_count = 8
output_interval = 1
quality_check_enabled = true
quality_check_strict = false
write_particles = false
write_vtk = false
```

Step157 default must keep:

```text
lbm_viscosity_semantics = legacy_external
```

Physical-Re parity remains false. Do not use `physical_nu_mapping` as the
default because physical-viscosity mapping remains a tau-margin risk.

Write `step157_subcycle_config_report.json` with:

```json
{
  "step": 157,
  "status": "subcycled_fsi_config_built",
  "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
  "lbm_substeps_per_fsi_step": 120,
  "lbm_dt_phys_override_s": 4.166666666666667e-6,
  "official_fsi_dt_s": 0.0005,
  "official_dt_reconstructed_from_lbm_substeps": 0.0005,
  "target_velocity_mapping_reconstructs_10_mps": true,
  "legacy_external_viscosity_used": true,
  "physical_reynolds_parity_claim_allowed": false,
  "validation_claim_allowed": false
}
```

## Solver Runtime Requirement

Implement in:

```text
src/mpm_lbm/solvers/official_subcycled_flow_solver.py
```

Required function:

```python
run_step157_subcycled_flow_repair(
    compiled_case_path: Path,
    step155_root: Path,
    step156_root: Path,
    output_dir: Path,
    raw_output_dir: Path | None = None,
    force: bool = False,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    lbm_substeps_per_fsi_step: int | None = None,
    snapshot_official_steps: tuple[int, ...] = (0, 5, 10, 20, 30, 40, 50),
    tail_fraction: float = 0.2,
    max_wall_seconds: float | None = None,
) -> dict
```

The solver loop must use `FSIDriver3D` directly and must not call the Step155
experiment runner.

Preferred loop:

```python
driver = FSIDriver3D(config, out_dir=str(raw_dir))
driver.initialize()

for official_step in range(0, 51):
    if official_step > 0:
        driver.step_once()
    collect diagnostics, monitor, force, stability, mass flux
    if official_step in snapshot_official_steps:
        write velocity snapshot
```

`driver.step_once()` must internally run 120 LBM substeps because
`fsi_exchange_mode = lbm_subcycled_per_fsi_step`.

Rows are sampled at official FSI step indices:

```text
0, 1, 2, ..., 50
```

Each row time must be:

```text
time_s = official_step * 0.0005
```

The runtime summary must include:

```text
n_official_steps_completed = 50
total_lbm_substeps_completed = 6000
```

## CSV Requirements

Write:

```text
subcycled_solver_timeseries.csv
subcycled_solver_monitor.csv
subcycled_solver_force_monitor.csv
subcycled_stability_timeseries.csv
subcycled_mass_flux_timeseries.csv
```

Use Step155-compatible fields where applicable, and add:

```text
official_step
time_s
lbm_substeps_per_fsi_step
total_lbm_substeps
fsi_exchange_mode
```

For `subcycled_mass_flux_timeseries.csv`, required fields:

```text
official_step
time_s
total_lbm_substeps
total_fluid_mass
mass_delta_rel
inlet_flux
outlet_flux
midplane_flux
flux_imbalance_rel
outlet_to_inlet_flux_ratio
midplane_to_inlet_flux_ratio
```

## Velocity Snapshot Requirements

Write snapshots under:

```text
velocity_snapshots/
```

Required snapshot files:

```text
velocity_snapshot_step000.npz
velocity_snapshot_step005.npz
velocity_snapshot_step010.npz
velocity_snapshot_step020.npz
velocity_snapshot_step030.npz
velocity_snapshot_step040.npz
velocity_snapshot_step050.npz
```

Each snapshot must include:

```text
velocity
rho
solid
speed
ux
uy
uz
official_step
time_s
total_lbm_substeps
lbm_substeps_per_fsi_step
compiled_case_path
validation_claim_allowed
```

The final step050 snapshot must be finite on fluid cells.

## Flow Development Comparison Requirement

Write:

```text
flow_development_comparison_report.json
```

Required structure:

```json
{
  "step": 157,
  "status": "flow_development_comparison_written",
  "baseline_step155_step156": {
    "flow_development_gate_pass": false
  },
  "subcycled_step157": {
    "flow_development_gate_pass": false
  },
  "outlet_flux_ratio_improved": true,
  "flux_imbalance_improved": true,
  "subcycling_repair_success": false,
  "subcycling_repair_success_policy": "flow gate requires abs(outlet_to_inlet_flux_ratio_tail_mean) >= 0.5 and abs(flux_imbalance_rel_tail_mean) <= 0.5",
  "validation_claim_allowed": false
}
```

Do not force `subcycling_repair_success = true`. Report the actual flow gate
honestly.

## Solver Acceptance Requirement

Write:

```text
solver_acceptance_report.json
```

Required fields:

```json
{
  "step": 157,
  "status": "subcycled_solver_acceptance_report_written",
  "subcycled_solver_run_executed": true,
  "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
  "lbm_substeps_per_fsi_step": 120,
  "n_official_steps_completed": 50,
  "official_time_end_s": 0.025,
  "total_lbm_substeps_completed": 6000,
  "density_gate_pass": true,
  "finite_gate_pass": true,
  "mpm_j_gate_pass": true,
  "monitor_displacement_finite": true,
  "force_monitor_finite": true,
  "mass_flux_reported": true,
  "flow_development_gate_pass": false,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

If the subcycled run fails due to nonfinite fields or runtime exception, write a
failure report with:

```json
{
  "status": "subcycled_solver_acceptance_failed",
  "subcycled_solver_run_executed": false,
  "failure_stage": "...",
  "error_type": "...",
  "error_message": "...",
  "validation_claim_allowed": false
}
```

and exit nonzero.

## Official Comparison Status

Write:

```text
official_comparison_status_report.json
```

If the official monitor is missing:

```json
{
  "step": 157,
  "status": "official_monitor_missing",
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "comparison_scope": "subcycled_solver_repair_only",
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false
}
```

Do not run Step150 in Step157.

## Step157 Summary

Write:

```text
step157_summary.json
```

Required fields:

```json
{
  "step": 157,
  "time_scale_mismatch_diagnosed": true,
  "compiled_case_consumed": true,
  "step155_baseline_consumed": true,
  "step156_acceptance_consumed": true,
  "subcycled_solver_run_executed": true,
  "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
  "lbm_substeps_per_fsi_step": 120,
  "lbm_dt_phys_override_s": 4.166666666666667e-6,
  "n_official_steps_completed": 50,
  "official_time_end_s": 0.025,
  "total_lbm_substeps_completed": 6000,
  "density_gate_pass": true,
  "finite_gate_pass": true,
  "mpm_j_gate_pass": true,
  "source_step156_flow_development_gate_pass": false,
  "step157_flow_development_gate_reported": true,
  "step157_flow_development_gate_pass": false,
  "outlet_flux_ratio_improved": true,
  "flux_imbalance_improved": true,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

If the flow gate still fails, set:

```json
{
  "status": "subcycled_flow_development_repair_attempt_complete_but_flow_gate_failed",
  "step158_recommended_next": "open_boundary_or_geometry_obstruction_diagnosis"
}
```

If the flow gate passes, set:

```json
{
  "status": "subcycled_flow_development_repair_complete",
  "step158_recommended_next": "postprocess_subcycled_solver_and_compare_if_official_monitor_available"
}
```

## Report Requirements

Write both:

```text
outputs/step157_official_subcycled_flow_development_repair/report.md
docs/campaigns/fluent_duct_flap/steps/157/report.md
```

Required language:

```text
Step157 diagnosed the Step155/Step156 flow-development failure as a
time-scale/subcycling mismatch candidate. Step155 used one LBM step per
official FSI step, while the Step154/Step155 dimensional velocity mapping
requires 120 LBM substeps per 0.0005 s official FSI step on the 48^3 grid.

Step157 ran the official tutorial proxy case with
fsi_exchange_mode = lbm_subcycled_per_fsi_step,
lbm_substeps_per_fsi_step = 120,
lbm_dt_phys_override_s = 4.166666666666667e-6 s,
for 50 official steps and 6000 total LBM substeps.

Step157 did not run Fluent, did not load or fabricate official monitor data,
did not run Step150, did not run selected96, and does not make a validation
claim.
```

If the flow gate fails, report:

```text
Subcycling alone did not close the flow-development gate. The next step must
diagnose open-boundary behavior, outlet propagation, or geometry/mask mismatch.
```

If the flow gate passes, report:

```text
Subcycling repaired the flow-development gate for the proxy solver. The next
step may postprocess the subcycled result and prepare official-monitor
comparison, but validation remains blocked until official reference data and
explicit thresholds are available.
```

## Documentation Updates

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
README.md
```

Required status language:

```text
Step157 is now the current subcycled flow-development repair step. It consumed
the Step154 compiled case, Step155 one-LBM-step solver output, and Step156
postprocessing/acceptance reports. It diagnosed the Step155 flow-development
failure as a time-scale/subcycling mismatch candidate and ran the same proxy
official tutorial case with 120 LBM substeps per 0.0005 s official FSI step.

Step157 did not run Fluent, did not load or fabricate official monitor data,
did not run Step150, did not run selected96, and does not make a validation
claim.

Validation and Figure 29.3 parity remain blocked.
```

## Test Requirements

Add:

```text
tests/test_step157_official_subcycled_flow_development_contract.py
```

Tests must cover:

```text
1. substep calculation from Step154 compiled case
2. Step157 subcycled FSIDriverConfig builder fields
3. Step157 runner source excludes prior experiment runners, Fluent, Step150, and subprocess
4. committed time-scale diagnosis schema
5. committed real-run artifact schema
6. Step157 summary contract
7. flow-development comparison fields and honest success policy
8. final snapshot schema and finite velocity/rho on fluid cells
```

Do not require `subcycling_repair_success = true` unless the real run actually
passes the flow-development gate. The tests must check honest reporting, not
force a fake success.

## Required Verification Commands

Run focused test:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step157_official_subcycled_flow_development_contract.py
```

Run adjacent regression:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step155_official_tutorial_solver_v1_contract.py `
  tests\test_step156_official_tutorial_postprocess_acceptance_contract.py `
  tests\test_step157_official_subcycled_flow_development_contract.py
```

Run compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step157_official_subcycled_flow_development_repair.py `
  src\mpm_lbm\solvers\official_subcycled_flow_config.py `
  src\mpm_lbm\solvers\official_subcycled_flow_solver.py `
  src\mpm_lbm\solvers\official_subcycled_flow_diagnostics.py
```

Run JSON parse, CSV parse, snapshot, and diff hygiene:

```powershell
git diff --check
```

## Acceptance Criteria

Step157 is accepted if it produces an honest subcycled solver evidence package:

```json
{
  "step": 157,
  "time_scale_mismatch_diagnosed": true,
  "compiled_case_consumed": true,
  "step155_baseline_consumed": true,
  "step156_acceptance_consumed": true,
  "subcycled_solver_run_executed": true,
  "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
  "lbm_substeps_per_fsi_step": 120,
  "lbm_dt_phys_override_s": 4.166666666666667e-6,
  "n_official_steps_completed": 50,
  "official_time_end_s": 0.025,
  "total_lbm_substeps_completed": 6000,
  "density_gate_pass": true,
  "finite_gate_pass": true,
  "mpm_j_gate_pass": true,
  "mass_flux_reported": true,
  "source_step156_flow_development_gate_pass": false,
  "step157_flow_development_gate_reported": true,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

`step157_flow_development_gate_pass` may be true or false. It must be reported
honestly.

## Next Step After Step157

If Step157 passes the flow-development gate:

```text
Step158 Official Subcycled Result Postprocess And Monitor Intake
```

If Step157 still fails the flow-development gate:

```text
Step158 Open Boundary / Outlet Propagation Root-Cause Repair
```

With the current Step156 result, Step157 tests the strongest repair hypothesis
first: insufficient LBM subcycling.
