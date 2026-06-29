# Step156 Goal: Official Tutorial Postprocess And Solver Acceptance

## Source Contract

Step156 follows remote `origin/main` after Step155 commit:

```text
620709d5cb724d3afa77558db92d19012db19b75
```

Step155 completed the first direct solver run from the Step154 compiled case.
It consumed:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
```

and produced a 50-step `FSIDriver3D` run under:

```text
outputs/step155_official_tutorial_solver_v1/
```

Step155 key state that Step156 must preserve:

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

Step156 must be an artifact-backed postprocessing and acceptance step. It must
not re-run solver code. It must expose, not hide, the current Step155
flow-development gap: the inlet flux is large while the outlet flux remains
near zero over the 0.025 s public tutorial window.

## Objective

Implement:

```text
Step156 Official Tutorial Postprocess And Solver Acceptance
```

Step156 must complete the current pipeline:

```text
Step154 preprocess -> Step155 solve -> Step156 postprocess and acceptance report
```

It must generate official-style visualization and diagnostic artifacts from the
committed Step154/Step155 outputs, then write reports that clearly separate:

```text
postprocess completion = true
solver numerical sanity = true
flow-development gate = report-only, may be false
Fluent/Figure 29.3 validation = false
```

## Non-Goals

Step156 must not:

```text
- run Fluent
- run FSIDriver3D
- instantiate FSIDriver3D
- call driver.run()
- call step_once()
- run Step148
- run Step153
- rerun Step155
- run Step150/151/152
- fabricate official monitor data
- modify solver runtime physics
- modify Step155 outputs
- modify vendored external solvers
- run selected96
- claim Fluent validation
- claim Figure 29.3 parity
- claim official mesh reproduction
```

Step156 is postprocess-only. Solver physics and flow-development repair are
reserved for a later step.

## Required Source Files

Create:

```text
experiments/steps/step156_official_tutorial_postprocess_and_solver_acceptance.py

src/mpm_lbm/postprocessing/__init__.py
src/mpm_lbm/postprocessing/fluent_duct_flap_io.py
src/mpm_lbm/postprocessing/fluent_duct_flap_velocity_render.py
src/mpm_lbm/postprocessing/fluent_duct_flap_monitor_plots.py
src/mpm_lbm/postprocessing/fluent_duct_flap_acceptance.py
src/mpm_lbm/postprocessing/fluent_duct_flap_official_comparison.py

tests/test_step156_official_tutorial_postprocess_acceptance_contract.py
docs/campaigns/fluent_duct_flap/steps/156/report.md
```

Create committed artifacts under:

```text
outputs/step156_official_tutorial_postprocess_and_acceptance/
```

## Required Inputs

Step156 must read:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
outputs/step154_official_solver_prepost_pipeline/postprocess_spec.json
outputs/step154_official_solver_prepost_pipeline/geometry_masks.npz
outputs/step154_official_solver_prepost_pipeline/boundary_masks.npz
outputs/step154_official_solver_prepost_pipeline/fsi_interface_masks.npz

outputs/step155_official_tutorial_solver_v1/solver_v1_summary.json
outputs/step155_official_tutorial_solver_v1/solver_monitor.csv
outputs/step155_official_tutorial_solver_v1/solver_force_monitor.csv
outputs/step155_official_tutorial_solver_v1/solver_timeseries.csv
outputs/step155_official_tutorial_solver_v1/stability_timeseries.csv
outputs/step155_official_tutorial_solver_v1/mass_flux_timeseries.csv
outputs/step155_official_tutorial_solver_v1/velocity_snapshots/velocity_snapshot_step050.npz
```

Optional input:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

If the optional official monitor is absent, Step156 must still complete
postprocessing and write an honest `official_monitor_missing` comparison report.
It must not fabricate official data.

## Required Runner

Add executable module:

```text
experiments/steps/step156_official_tutorial_postprocess_and_solver_acceptance.py
```

Default command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step156_official_tutorial_postprocess_and_solver_acceptance `
  --case outputs\step154_official_solver_prepost_pipeline\compiled_case.json `
  --solver-root outputs\step155_official_tutorial_solver_v1 `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --output-dir outputs\step156_official_tutorial_postprocess_and_acceptance `
  --force
```

Required CLI arguments:

```text
--case
--solver-root
--official-monitor
--output-dir
--force
```

Optional CLI arguments:

```text
--snapshot-step
--slice-z-index
--use-monitor-z
--tail-fraction
--dpi
--no-preview-open
```

Defaults:

```json
{
  "snapshot_step": 50,
  "use_monitor_z": true,
  "tail_fraction": 0.2,
  "dpi": 160
}
```

The committed run must use Step155's real `48^3` final snapshot at step 50.

## Required Output Artifacts

Write:

```text
outputs/step156_official_tutorial_postprocess_and_acceptance/
  velocity_magnitude_step050.png
  velocity_ux_step050.png
  velocity_uy_step050.png
  streamline_or_quiver_step050.png
  geometry_overlay_step050.png
  official_style_velocity_cloud_step050.png

  centerline_velocity_profile.csv
  x_plane_flux_profile.csv
  final_snapshot_field_summary.json
  velocity_render_report.json

  monitor_displacement_plot.png
  force_monitor_plot.png
  monitor_plot_report.json

  solver_acceptance_report.json
  official_comparison_report.json
  postprocess_summary.json
  report.md
```

`official_style_velocity_cloud_step050.png` is a convenience artifact for the
visual workflow, but the exact Step154 spec names must also exist.

## Velocity Unit Mapping

Render both raw solver values and proxy physical values honestly. Use the
Step155 target mapping:

```text
target_u_lbm = 0.02
inlet_velocity_mps = 10.0
velocity_scale_mps_per_lbm = inlet_velocity_mps / target_u_lbm = 500.0
```

For plotted values:

```text
speed_mps_proxy = speed_lbm * velocity_scale_mps_per_lbm
ux_mps_proxy = ux_lbm * velocity_scale_mps_per_lbm
uy_mps_proxy = uy_lbm * velocity_scale_mps_per_lbm
uz_mps_proxy = uz_lbm * velocity_scale_mps_per_lbm
```

Every report and plot title using this conversion must label it as:

```text
proxy m/s from Step155 target_u_lbm mapping; not Fluent validation
```

Do not label this as exact physical validation.

## Slice Policy

The default plotted plane is the monitor z-index from Step154:

```text
compiled_case.monitor_spec.monitor_index[2]
```

If `--slice-z-index` is supplied, use that explicit z index.

Record the selected slice in `velocity_render_report.json` and
`postprocess_summary.json`:

```json
{
  "slice_axis": "z",
  "slice_policy": "monitor_z_index",
  "snapshot_step": 50,
  "snapshot_time_s": 0.025
}
```

## Velocity Render Requirements

Implement in:

```text
src/mpm_lbm/postprocessing/fluent_duct_flap_velocity_render.py
```

Required function names:

```python
load_velocity_snapshot(snapshot_path: Path) -> dict
load_step154_masks(compiled_case: dict) -> dict[str, dict[str, np.ndarray]]
build_velocity_field_summary(snapshot: dict, masks: dict, compiled_case: dict) -> dict
write_velocity_magnitude_plot(snapshot: dict, masks: dict, compiled_case: dict, output_path: Path, slice_index: int) -> dict
write_velocity_component_plot(snapshot: dict, masks: dict, compiled_case: dict, output_path: Path, component: str, slice_index: int) -> dict
write_streamline_or_quiver_plot(snapshot: dict, masks: dict, compiled_case: dict, output_path: Path, slice_index: int) -> dict
write_geometry_overlay_plot(snapshot: dict, masks: dict, compiled_case: dict, output_path: Path, slice_index: int) -> dict
write_centerline_velocity_profile(snapshot: dict, masks: dict, compiled_case: dict, output_path: Path, slice_index: int) -> dict
write_x_plane_flux_profile(snapshot: dict, masks: dict, compiled_case: dict, output_path: Path) -> dict
```

Matplotlib requirements:

```text
- use matplotlib with Agg backend
- do not use seaborn
- do not require GUI
- do not hard-code OS-specific absolute paths
- every PNG must be nonempty
```

`velocity_magnitude_step050.png` must show:

```text
- velocity magnitude on the selected z slice
- masked solid/flap region or overlay
- monitor point marker
- inlet/outlet markers or labels
- colorbar labelled "Velocity magnitude [m/s proxy]"
- title includes "Step155 step 50, t = 0.025 s"
```

`velocity_ux_step050.png` must show:

```text
- ux component on the selected z slice
- signed visualization
- colorbar labelled "ux [m/s proxy]"
- title includes "ux diagnostic; not Fluent validation"
```

`velocity_uy_step050.png` must show:

```text
- uy component on the selected z slice
- colorbar labelled "uy [m/s proxy]"
- title includes "uy diagnostic; not Fluent validation"
```

`streamline_or_quiver_step050.png` must show:

```text
- ux/uy vectors or streamlines on the selected z slice
- masked solid/flap region
- monitor point
- title includes "not Fluent validation"
```

`geometry_overlay_step050.png` must show:

```text
- duct fluid region
- duct wall/solid region
- flap/interface region
- monitor cell
- inlet/outlet masks
```

`official_style_velocity_cloud_step050.png` must show:

```text
- velocity magnitude field
- official-like aspect ratio
- geometry outline
- colorbar
- clear title that says "proxy solver result; not Fluent validation"
```

Do not imply Figure 29.3 parity.

## Centerline Velocity Profile

Write:

```text
centerline_velocity_profile.csv
```

Required fields:

```text
x_index
x_norm
x_m
y_index
y_norm
z_index
z_norm
rho
ux_lbm
uy_lbm
uz_lbm
speed_lbm
ux_mps_proxy
uy_mps_proxy
uz_mps_proxy
speed_mps_proxy
solid
fluid_mask
```

Policy:

```text
y = nearest duct centerline index
z = selected slice index
x = all x indices
y_center_norm = 0.5 * (duct_y_min + duct_y_max)
```

Use nearest cell center.

## X-Plane Flux Profile

Write:

```text
x_plane_flux_profile.csv
```

Required fields:

```text
x_index
x_norm
x_m
fluid_cell_count_static_mask
fluid_cell_count_dynamic_solver
mass_flux_lbm
mean_ux_lbm
mean_speed_lbm
max_speed_lbm
mass_flux_mps_proxy_sum
outlet_plane
inlet_plane
midplane
```

Compute for every x plane:

```text
mass_flux_lbm = sum(rho * ux over dynamic fluid cells on that x plane)
mean_ux_lbm = mean(ux over dynamic fluid cells on that x plane)
```

Use runtime dynamic fluid cells from `solid == 0`, and include static Step154
mask counts for comparison.

## Monitor Plot Requirements

Implement in:

```text
src/mpm_lbm/postprocessing/fluent_duct_flap_monitor_plots.py
```

Required function names:

```python
load_csv_rows(path: Path) -> list[dict]
write_monitor_displacement_plot(solver_monitor_csv: Path, output_path: Path) -> dict
write_force_monitor_plot(solver_force_monitor_csv: Path, output_path: Path) -> dict
summarize_monitor_rows(solver_monitor_csv: Path, solver_force_csv: Path) -> dict
```

`monitor_displacement_plot.png` must plot over time:

```text
flap_tip_total_displacement_m
official_point_like_total_displacement_m
```

If one series is missing, plot the available series and report the missing one.
The title must include:

```text
Step155 proxy monitor displacement; not official Fluent monitor
```

`force_monitor_plot.png` must plot over time:

```text
fluid_force_magnitude_n
```

The title must include:

```text
force proxy; not direct Fluent wall integral
```

## Solver Acceptance Requirements

Implement in:

```text
src/mpm_lbm/postprocessing/fluent_duct_flap_acceptance.py
```

Required function names:

```python
load_step155_summary(solver_root: Path) -> dict
summarize_mass_flux(mass_flux_csv: Path, tail_fraction: float = 0.2) -> dict
summarize_stability(stability_csv: Path) -> dict
build_solver_acceptance_report(step155_summary: dict, mass_flux_summary: dict, stability_summary: dict, output_path: Path) -> dict
```

Write `solver_acceptance_report.json` with these required fields:

```json
{
  "step": 156,
  "status": "solver_acceptance_report_written",
  "source_step155_status": "official_tutorial_solver_v1_run_complete",
  "postprocess_acceptance_pass": true,
  "solver_numerical_sanity_pass": true,
  "step_window_pass": true,
  "density_gate_pass": true,
  "finite_gate_pass": true,
  "mpm_j_gate_pass": true,
  "flow_development_gate_pass": false,
  "flow_development_gate_policy": "report_only_for_step156",
  "flow_development_not_required_for_postprocess_completion": true,
  "mass_flux_rows": 51,
  "tail_fraction": 0.2,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

The exact numeric mass-flux fields must be computed from
`mass_flux_timeseries.csv`:

```text
inlet_flux_tail_mean
outlet_flux_tail_mean
midplane_flux_tail_mean
flux_imbalance_rel_tail_mean
outlet_to_inlet_flux_ratio_tail_mean
midplane_to_inlet_flux_ratio_tail_mean
```

Suggested report-only flow-development gate:

```text
abs(outlet_to_inlet_flux_ratio_tail_mean) >= 0.5
and abs(flux_imbalance_rel_tail_mean) <= 0.5
```

The current Step155 output is expected to fail this gate. That is acceptable if
it is reported honestly.

## Official Comparison Requirements

Implement in:

```text
src/mpm_lbm/postprocessing/fluent_duct_flap_official_comparison.py
```

Required function names:

```python
load_optional_official_monitor(path: Path) -> dict
build_official_comparison_report(official_monitor_path: Path, solver_monitor_csv: Path, output_path: Path) -> dict
```

If the official monitor is missing, write:

```json
{
  "step": 156,
  "status": "official_monitor_missing",
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "comparison_scope": "solver_postprocess_only",
  "next_action": "provide_private_official_monitor_or_run_step150_intake",
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false
}
```

If official monitor data exists, Step156 may compute finite error metrics such
as:

```text
rmse_m
max_abs_error_m
solver_series_used
official_series_used
```

Even with official data, keep `validation_claim_allowed = false` unless a later
explicit validation-threshold step changes the contract.

## Postprocess Summary

Write:

```text
postprocess_summary.json
```

Required fields:

```json
{
  "step": 156,
  "status": "official_tutorial_postprocess_complete",
  "preprocess_complete": true,
  "solver_complete": true,
  "postprocess_complete": true,
  "compiled_case_consumed": true,
  "step155_solver_root_consumed": true,
  "final_snapshot_loaded": true,
  "velocity_cloud_written": true,
  "velocity_magnitude_written": true,
  "velocity_ux_written": true,
  "velocity_uy_written": true,
  "streamline_or_quiver_written": true,
  "geometry_overlay_written": true,
  "monitor_plots_written": true,
  "centerline_profile_written": true,
  "x_plane_flux_profile_written": true,
  "solver_acceptance_report_written": true,
  "official_comparison_report_written": true,
  "solver_numerical_sanity_pass": true,
  "flow_development_gate_reported": true,
  "flow_development_gate_pass": false,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "solver_pipeline_complete": true,
  "official_validation_requires_monitor": true,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

If Step155 mass-flux data fails the flow-development gate, this summary must
set `flow_development_gate_pass = false` while keeping:

```json
{
  "postprocess_complete": true,
  "solver_pipeline_complete": true
}
```

## Main Runner Flow

The Step156 runner must:

```text
1. Load compiled_case.json.
2. Load Step154 postprocess_spec.json and masks.
3. Load Step155 solver_v1_summary.json.
4. Verify Step155 completed 50 steps and final snapshot exists.
5. Load velocity_snapshot_step050.npz.
6. Generate velocity magnitude, ux, uy, stream/quiver, geometry overlay, and official-style cloud PNGs.
7. Generate centerline_velocity_profile.csv.
8. Generate x_plane_flux_profile.csv.
9. Generate monitor displacement plot.
10. Generate force monitor plot.
11. Generate solver_acceptance_report.json.
12. Generate official_comparison_report.json.
13. Generate postprocess_summary.json.
14. Generate report.md.
15. Print postprocess_summary.json to stdout.
16. Exit nonzero if required inputs are missing or output generation fails.
```

Do not rerun solver.

## Report Requirements

Write both:

```text
outputs/step156_official_tutorial_postprocess_and_acceptance/report.md
docs/campaigns/fluent_duct_flap/steps/156/report.md
```

Required language:

```text
Step156 consumed the Step154 compiled case and Step155 solver outputs and
generated official-style postprocessing artifacts: velocity magnitude, ux, uy,
stream/quiver, geometry overlay, centerline profile, x-plane flux profile,
monitor plots, solver acceptance report, and official comparison report.

Step156 did not run the solver. Step156 did not run Fluent. Step156 did not
load or fabricate official monitor data when the private monitor was absent.
Step156 did not run Step150 and does not make a validation claim.

The current Step155 run passes numerical sanity gates, but flow-development
acceptance is report-only and may fail because outlet flux is still near zero
relative to inlet flux over the 0.025 s tutorial window.

A later step must address solver physics / flow-development gaps before any
Figure 29.3 parity or Fluent validation claim can be made.
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
Step156 is now the current official tutorial postprocessing and solver
acceptance step. It consumed Step154 compiled-case artifacts and Step155 solver
outputs, generated official-style velocity plots and diagnostics, wrote monitor
plots, centerline and x-plane flux profiles, solver acceptance report, and
official comparison report.

Step156 did not run Fluent, did not rerun the solver, did not load or fabricate
official monitor data, did not run Step150, did not run selected96, and does
not make a validation claim.

Step156 completes the preprocess -> solve -> postprocess pipeline, but it does
not close validation. If the official monitor is still absent, official error
metrics remain unavailable. If flow-development gates fail, the next step must
diagnose solver flow/outlet/geometry development rather than claiming
Figure 29.3 parity.
```

## Test Requirements

Add:

```text
tests/test_step156_official_tutorial_postprocess_acceptance_contract.py
```

Tests must cover:

```text
1. runner writes required PNG/CSV/JSON/report artifacts to a temporary output directory
2. runner source does not contain solver/Fluent/Step148/Step153/Step150 execution strings
3. Step155 final snapshot shape and render contract are valid
4. centerline and x-plane CSV schemas are present
5. monitor plots and monitor summary report 51 rows and proxy-force semantics
6. solver acceptance report distinguishes postprocess pass from flow-development gate
7. missing official monitor writes official_monitor_missing without validation claim
8. synthetic official monitor helper returns finite metrics but still no validation claim
9. committed Step156 artifact schema matches acceptance criteria
```

The source guard must reject these strings in the Step156 runner:

```text
FSIDriver3D(
driver.run(
step_once(
run_official_tutorial_solver_v1
run_step148
run_step153
step150_official_monitor_intake
fluent.exe
subprocess
```

## Required Execution Command

Run real Step156:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step156_official_tutorial_postprocess_and_solver_acceptance `
  --case outputs\step154_official_solver_prepost_pipeline\compiled_case.json `
  --solver-root outputs\step155_official_tutorial_solver_v1 `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --output-dir outputs\step156_official_tutorial_postprocess_and_acceptance `
  --force
```

## Required Verification Commands

Run focused test:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step156_official_tutorial_postprocess_acceptance_contract.py
```

Run adjacent regression:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step154_official_solver_prepost_pipeline_contract.py `
  tests\test_step155_official_tutorial_solver_v1_contract.py `
  tests\test_step156_official_tutorial_postprocess_acceptance_contract.py
```

Run compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step156_official_tutorial_postprocess_and_solver_acceptance.py `
  src\mpm_lbm\postprocessing\fluent_duct_flap_velocity_render.py `
  src\mpm_lbm\postprocessing\fluent_duct_flap_monitor_plots.py `
  src\mpm_lbm\postprocessing\fluent_duct_flap_acceptance.py `
  src\mpm_lbm\postprocessing\fluent_duct_flap_official_comparison.py `
  src\mpm_lbm\postprocessing\fluent_duct_flap_io.py
```

Run JSON parse, CSV parse, PNG nonzero-size checks, and:

```powershell
git diff --check
```

## Acceptance Criteria

Step156 is accepted only if `postprocess_summary.json` includes:

```json
{
  "step": 156,
  "status": "official_tutorial_postprocess_complete",
  "preprocess_complete": true,
  "solver_complete": true,
  "postprocess_complete": true,
  "compiled_case_consumed": true,
  "step155_solver_root_consumed": true,
  "final_snapshot_loaded": true,
  "velocity_cloud_written": true,
  "velocity_magnitude_written": true,
  "velocity_ux_written": true,
  "velocity_uy_written": true,
  "streamline_or_quiver_written": true,
  "geometry_overlay_written": true,
  "centerline_profile_written": true,
  "x_plane_flux_profile_written": true,
  "monitor_plots_written": true,
  "solver_acceptance_report_written": true,
  "official_comparison_report_written": true,
  "postprocess_acceptance_pass": true,
  "solver_numerical_sanity_pass": true,
  "flow_development_gate_reported": true,
  "solver_pipeline_complete": true,
  "official_validation_requires_monitor": true,
  "official_monitor_loaded": false,
  "official_error_metrics_available": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

`flow_development_gate_pass` may be false. Step156 must report it honestly and
still complete postprocessing.

## Next Step After Step156

If `flow_development_gate_pass = false`, the likely next step is:

```text
Step157 Flow Development / Outlet Propagation Diagnosis
```

It must diagnose why Step155 has strong inlet/midplane flow but almost no
outlet flux over the official 0.025 s window.

If an official monitor is later provided and flow development becomes
acceptable, Step157 may instead become:

```text
Step157 Official Monitor Error Localization
```

With the current Step155 result, the expected next step is flow/outlet
development diagnosis, not validation.
