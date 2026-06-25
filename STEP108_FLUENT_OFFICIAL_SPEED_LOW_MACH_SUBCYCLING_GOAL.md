# Step108 Fluent Official-Speed Low-Mach Subcycling Goal

This goal starts from `origin/main` Step107 commit `7d30b9de52edcddfbe6006c5bcc60cc20960b980`. Step107 is accepted as a comparison-infrastructure step: it added a public-plot digitized Fluent reference, metadata, an error harness, output guard, tests, and artifacts without changing solver behavior.

Step108 must now make the first official-speed low-Mach attempt. It must map the public Fluent tutorial inlet speed `10 m/s` to a stable LBM lattice speed `u_lbm = 0.02`, cover the official transient time window `0.025 s`, and immediately compare the resulting solver displacement curve with the Step107 public-reference error harness.

## Public Tutorial Scope

Use only the public Ansys Fluent two-way FSI tutorial facts already exposed by the public tutorial page:

- duct length: `0.10 m`
- duct height: `0.04 m`
- flap height: `0.01 m`
- flap thickness: `0.003 m`
- inlet speed: `10 m/s`
- outlet: pressure outlet
- structural model: linear elasticity
- silicone-rubber material reference: density `1600`, Young's modulus `1e6`, Poisson ratio `0.47`
- structural monitor name: `structural-point-flap`
- structural monitor location: `x=0.0505`, `y=0.0095`
- report quantity: vertex-average total displacement
- transient window: `50` steps, `0.0005 s` per step, ending at `0.025 s`

Do not commit official Fluent case, mesh, journal, data, image, or private CSV payloads. Step108 may cite the public tutorial URL and may use the Step107 approximate public-plot digitized curve.

## One-Sentence Goal

Map the official `10 m/s` inlet to low-Mach `u_lbm = 0.02` through `120` LBM substeps per official FSI step, run a proxy transient covering `0.0000 s` through `0.0250 s`, and compute Step107-style displacement error metrics without claiming Fluent validation or equivalence.

## Why Subcycling Is Required

The Step108 dimensional mapping is:

```text
duct_length_m = 0.1
n_grid = 48
official_fsi_dt_s = 0.0005
target_inlet_velocity_mps = 10.0
dx_phys_m = duct_length_m / n_grid = 0.0020833333333333333
```

If the official FSI time step were used as one LBM step:

```text
u_lbm = U * dt / dx = 10 * 0.0005 / 0.0020833333333333333 = 2.4
```

That lattice velocity is unusable. Step108 must instead enforce:

```text
target_u_lbm = 0.02
lbm_dt_phys_s = target_u_lbm * dx_phys_m / target_inlet_velocity_mps
                  = 4.166666666666667e-6
lbm_substeps_per_fsi_step = official_fsi_dt_s / lbm_dt_phys_s = 120
mapped_inlet_velocity_mps = target_u_lbm * dx_phys_m / lbm_dt_phys_s = 10.0
```

This is a dimensional mapping and smoke-run step. It is not a Fluent validation step.

## Allowed Statement

The final Step108 report may claim only:

```text
The official 10 m/s inlet speed was mapped to a low-Mach LBM target through subcycling, and a 0.025 s proxy transient produced a solver curve that was compared against the Step107 public Fluent plot reference.
```

## Forbidden Statements

The final Step108 report, docs, logs, configs, and artifacts must not claim:

```text
Fluent validation passed
Fluent equivalence achieved
official Fluent mesh reproduced
official steady-preflow reproduced
official structural-point monitor equivalence achieved
production ready
```

## Solver Change Envelope

Allowed production-code edits are limited to the driver configuration and driver orchestration needed for opt-in low-Mach subcycling:

- `src/mpm_lbm/sim/drivers/fsi_config.py`
- `src/mpm_lbm/sim/drivers/sim_config.py`
- `src/mpm_lbm/sim/drivers/fsi_driver.py`

The default existing path must stay unchanged:

```text
fsi_exchange_mode = one_lbm_step_per_fsi_step
lbm_substeps_per_fsi_step = 1
lbm_dt_phys_override_s = null
official_fsi_dt_s = null
```

The Step108 opt-in path must be:

```text
fsi_exchange_mode = lbm_subcycled_per_fsi_step
lbm_substeps_per_fsi_step = 120
lbm_dt_phys_override_s = 4.166666666666667e-6
official_fsi_dt_s = 0.0005
target_inlet_velocity_mps = 10.0
target_u_lbm_for_dimensional_mapping = 0.02
physical_duct_length_m = 0.1
```

Forbidden production-code edits:

- do not change `src/mpm_lbm/sim/lbm/fluid.py` collision, tau, inlet/outlet formula, or bounce-back formula
- do not change `src/mpm_lbm/sim/coupling/*`
- do not change `src/mpm_lbm/sim/mpm/solid.py` stress/update logic
- do not change `external/taichi_LBM3D/**`
- do not change `data/real_geometry_candidates/**`
- do not tune reaction scale to fit the public plot

## Required Config Fields

Add opt-in fields to `FSIDriverConfig`:

```python
physical_duct_length_m: float = 1.0
target_inlet_velocity_mps: Optional[float] = None
official_fsi_dt_s: Optional[float] = None
target_u_lbm_for_dimensional_mapping: Optional[float] = None
lbm_substeps_per_fsi_step: int = 1
lbm_dt_phys_override_s: Optional[float] = None
fsi_exchange_mode: str = "one_lbm_step_per_fsi_step"
```

Required validation:

```text
fsi_exchange_mode in {"one_lbm_step_per_fsi_step", "lbm_subcycled_per_fsi_step"}
lbm_substeps_per_fsi_step > 0
physical_duct_length_m > 0
lbm_dt_phys_override_s > 0 when subcycling is enabled
official_fsi_dt_s > 0 when subcycling is enabled
target_inlet_velocity_mps > 0 when subcycling is enabled
target_u_lbm_for_dimensional_mapping > 0 when subcycling is enabled
official_fsi_dt_s == lbm_substeps_per_fsi_step * lbm_dt_phys_override_s within tolerance
target_u_lbm[0] == target_u_lbm_for_dimensional_mapping within tolerance
mapped_inlet_velocity_mps == target_inlet_velocity_mps within tolerance
```

Add `lbm_dt_phys_override_s: Optional[float] = None` to `UnifiedSimConfig`. Its `lbm_dt_phys` property must return the override when present and must preserve the old `mpm_substeps_per_lbm_step * mpm_dt` behavior otherwise.

## Required Driver Behavior

Keep `FSIDriver3D.step_once()` behavior unchanged for `one_lbm_step_per_fsi_step`.

For `lbm_subcycled_per_fsi_step`, one official driver step must:

```text
project current solid state to LBM once
for each LBM substep:
    update dynamic solid
    reinitialize new fluid cells
    run one LBM moving-boundary step
transfer moving-boundary reaction at the official step boundary
run the configured MPM update once per official step
collect diagnostics and flap-tip monitor rows on the official time grid
```

The first Step108 implementation may use the last substep's moving-boundary reaction at the official step boundary. It must not change coupling formulas, MPM stress, tau, or bounce-back formulas.

`FSIDriver3D.collect_flap_tip_monitor()` must write Step108 official-time rows:

```text
time_s = step * official_fsi_dt_s
rows = 51 for steps 0..50
time_end_s = 0.025
```

## Required Files

Goal, docs, and report:

- `STEP108_FLUENT_OFFICIAL_SPEED_LOW_MACH_SUBCYCLING_GOAL.md`
- `STEP108_FLUENT_OFFICIAL_SPEED_LOW_MACH_SUBCYCLING_REPORT.md`
- `docs/108_fluent_official_speed_low_mach_subcycling.md`

Configs:

- `configs/step108_low_mach_subcycling_policy.json`
- `configs/step108_duct_only_low_mach_subcycling_48_50official_steps.json`
- `configs/step108_fluent_duct_flap_low_mach_subcycling_48_50step_candidate.json`
- `configs/step108_output_guard_policy.json`
- `configs/step108_artifact_manifest_policy.json`

Source:

- `src/mpm_lbm/evidence/step108_common.py`
- `src/mpm_lbm/evidence/step108_dimensional_mapping.py`
- `src/mpm_lbm/evidence/step108_duct_only_low_mach_subcycling_runner.py`
- `src/mpm_lbm/evidence/step108_low_mach_fsi_candidate_runner.py`
- `src/mpm_lbm/evidence/step108_error_comparison.py`
- `src/mpm_lbm/evidence/step108_output_guard.py`

Baseline runners:

- `baseline_tests/run_step108_dimensional_mapping.py`
- `baseline_tests/run_step108_duct_only_low_mach_subcycling.py`
- `baseline_tests/run_step108_low_mach_fsi_candidate.py`
- `baseline_tests/run_step108_error_comparison.py`
- `baseline_tests/run_step108_output_guard.py`
- `baseline_tests/run_step108_artifact_manifest.py`

Focused tests:

- `tests/test_step108_low_mach_subcycling_contract.py`
- `tests/test_step108_error_comparison_contract.py`
- `tests/test_step108_output_guard_contract.py`

README must receive one concise Step108 bullet in the implemented-step list.

## Required Outputs

Dimensional mapping:

- `outputs/step108_dimensional_mapping/low_mach_subcycling_mapping_report.json`
- `outputs/step108_dimensional_mapping/low_mach_subcycling_mapping_report.csv`
- `outputs/step108_dimensional_mapping/low_mach_subcycling_mapping_report.md`

Duct-only precheck:

- `outputs/step108_duct_only_low_mach_subcycling/flow_plane_timeseries.csv`
- `outputs/step108_duct_only_low_mach_subcycling/flow_plane_report.json`
- `outputs/step108_duct_only_low_mach_subcycling/flow_plane_report.csv`
- `outputs/step108_duct_only_low_mach_subcycling/flow_plane_report.md`
- `outputs/step108_duct_only_low_mach_subcycling/duct_static_geometry_report.json`

FSI candidate:

- `outputs/step108_low_mach_fsi_candidate/flap_tip_displacement_timeseries.csv`
- `outputs/step108_low_mach_fsi_candidate/diagnostics_timeseries.csv`
- `outputs/step108_low_mach_fsi_candidate/low_mach_fsi_report.json`
- `outputs/step108_low_mach_fsi_candidate/low_mach_fsi_report.csv`
- `outputs/step108_low_mach_fsi_candidate/low_mach_fsi_report.md`
- `outputs/step108_low_mach_fsi_candidate/duct_boundary_condition_report.json`
- `outputs/step108_low_mach_fsi_candidate/duct_static_geometry_report.json`

Error comparison:

- `outputs/step108_error_comparison/error_report.json`
- `outputs/step108_error_comparison/error_report.csv`
- `outputs/step108_error_comparison/error_report.md`
- `outputs/step108_error_comparison/error_summary.csv`

Guards:

- `outputs/step108_output_guard/output_guard_report.json`
- `outputs/step108_output_guard/output_guard_report.csv`
- `outputs/step108_artifact_manifest/artifact_manifest.json`
- `outputs/step108_artifact_manifest/artifact_manifest.csv`

Logs:

- `logs/step108_dimensional_mapping.log`
- `logs/step108_duct_only_low_mach_subcycling.log`
- `logs/step108_low_mach_fsi_candidate.log`
- `logs/step108_error_comparison.log`
- `logs/step108_output_guard.log`
- `logs/step108_artifact_manifest.log`

## Duct-Only Precheck Contract

The duct-only precheck must use:

```text
n_grid = 48
official_steps = 50
lbm_substeps_per_fsi_step = 120
total_lbm_substeps = 6000
target_u_lbm = [0.02, 0.0, 0.0]
```

Acceptance:

```text
inlet_mean_ux approximately 0.02
mid_mean_ux > 1e-4
outlet_mean_ux > 1e-4
rho_min > 0.90
rho_max < 1.20
has_nan = false
has_inf = false
low_mach_mapping_enabled = true
```

If the full `50` official-step duct-only run is too slow, a clearly labeled `5` official-step smoke may be produced while keeping the `50` official-step config and goal. The target is still to run the `50` official-step artifact.

## FSI Candidate Contract

`configs/step108_fluent_duct_flap_low_mach_subcycling_48_50step_candidate.json` must use:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "duct_flap_proxy",
  "geometry_config_path": "configs/step104_fluent_duct_flap_geometry_1024.json",
  "n_grid": 48,
  "n_particles": 1024,
  "n_lbm_steps": 50,
  "mpm_dt": 0.0005,
  "mpm_substeps_per_lbm_step": 1,
  "official_fsi_dt_s": 0.0005,
  "physical_duct_length_m": 0.1,
  "target_inlet_velocity_mps": 10.0,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "target_u_lbm_for_dimensional_mapping": 0.02,
  "lbm_substeps_per_fsi_step": 120,
  "lbm_dt_phys_override_s": 4.166666666666667e-6,
  "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
  "initial_solid_velocity_norm": [0.0, 0.0, 0.0],
  "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
  "velocity_inlet_axis": "x",
  "velocity_inlet_side": "min",
  "pressure_outlet_side": "max",
  "wall_velocity_application_mode": "disabled",
  "wall_velocity_application_config_path": null,
  "reaction_transfer_mode": "engineering",
  "write_vtk": false,
  "write_particles": false,
  "output_interval": 1
}
```

Acceptance:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
completed_official_fsi_steps = 50
completed_lbm_substeps = 6000
flap_tip_timeseries_row_count = 51
solver time_start_s = 0.0
solver time_end_s = 0.025
fixed_base_max_displacement_norm <= 1e-7
fixed_base_max_velocity_norm <= 1e-7
step36_squid_wall_velocity_config_used = false
has_nan = false
has_inf = false
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
```

## Error Comparison Contract

Step108 must reuse the Step107 public reference and pure-Python error metric code:

```text
reference_curve_path = benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv
solver_curve_path = outputs/step108_low_mach_fsi_candidate/flap_tip_displacement_timeseries.csv
solver_time_column = time_s
solver_displacement_column = flap_tip_total_displacement_m
monitor_used = free_tip_proxy_mean
monitor_equivalence = false
```

Acceptance:

```text
reference_loaded = true
solver_curve_loaded = true
sample_count = 51
all_metrics_finite = true
solver_curve_time_end_s = 0.025
normalized_rms_error computed and finite
peak_solver_m computed and finite
shape_correlation in [-1, 1]
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
```

Soft goals are reported, not hard-gated:

```text
Step108 peak_solver_m > Step107 peak_solver_m
Step108 normalized_rms_error < Step107 normalized_rms_error
Step108 shape_correlation > Step107 shape_correlation
```

If soft goals fail, the report must say so plainly and must not fake a pass. That outcome means the speed scale was repaired but structural/preflow/monitor/force-transfer issues still dominate and should move to Step109/Step110.

## Output Guard Contract

Step108 output guard must check:

```text
official case file count = 0
official mesh file count = 0
official journal file count = 0
official case/data H5 count = 0
official image count = 0
private Fluent CSV count = 0
validation claim count = 0
direct equivalence claim count = 0
protected external edit count = 0
protected real geometry candidate edit count = 0
artifact budget pass = true
```

The guard must ignore its own output directory and artifact-manifest output directory.

## RED/GREEN Workflow

RED first:

```text
test_step108_mapping_reports_10mps_with_ulbm_0p02
test_step108_requires_lbm_substeps_per_fsi_step_120
test_step108_solver_curve_covers_0p025s_without_endpoint_hold
test_step108_error_report_uses_step107_reference_and_step108_solver_curve
test_step108_output_guard_blocks_validation_claims_and_official_payloads
```

The initial failure should be missing Step108 configs, missing mapping fields, missing subcycling artifacts, and missing Step108 error report.

GREEN:

```text
add opt-in config fields
add low-Mach dt override
add driver subcycling path
add dimensional mapping report
add duct-only runner
add FSI candidate runner
add Step108 error comparison wrapper
add Step108 output guard and artifact manifest
```

REFACTOR:

```text
default old path unchanged
low_mach_subcycling path opt-in only
Step104-Step107 existing artifacts/tests do not drift
```

## Hard Completion Gates

Step108 is complete only when all are true:

```text
low_mach_mapping_enabled = true
target_inlet_velocity_mps = 10.0
target_u_lbm_x = 0.02
lbm_dt_phys_s = 4.166666666666667e-6
lbm_substeps_per_fsi_step = 120
official_fsi_dt_s = 0.0005
mapped_inlet_velocity_mps in [9.99, 10.01]
duct-only low-Mach run finite
FSI candidate completed 50 official steps
FSI candidate completed 6000 LBM substeps
solver displacement timeseries has 51 rows
solver time_end_s = 0.025
fixed base displacement <= 1e-7
fixed base velocity <= 1e-7
Step36 wall velocity disabled
no NaN/Inf
error metrics finite
official case/mesh/journal/data/image committed count = 0
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
focused Step108 tests pass
full test suite passes under the trusted Taichi interpreter
Anaconda pytest and default pytest are attempted and reported honestly
git diff --check passes
```

## Required Verification Commands

Use the trusted interpreter first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\drivers\sim_config.py `
  src\mpm_lbm\sim\drivers\fsi_driver.py `
  src\mpm_lbm\evidence\step108_common.py `
  src\mpm_lbm\evidence\step108_dimensional_mapping.py `
  src\mpm_lbm\evidence\step108_duct_only_low_mach_subcycling_runner.py `
  src\mpm_lbm\evidence\step108_low_mach_fsi_candidate_runner.py `
  src\mpm_lbm\evidence\step108_error_comparison.py `
  src\mpm_lbm\evidence\step108_output_guard.py `
  baseline_tests\run_step108_dimensional_mapping.py `
  baseline_tests\run_step108_duct_only_low_mach_subcycling.py `
  baseline_tests\run_step108_low_mach_fsi_candidate.py `
  baseline_tests\run_step108_error_comparison.py `
  baseline_tests\run_step108_output_guard.py `
  baseline_tests\run_step108_artifact_manifest.py `
  tests\test_step108_low_mach_subcycling_contract.py `
  tests\test_step108_error_comparison_contract.py `
  tests\test_step108_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' baseline_tests\run_step108_dimensional_mapping.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step108_duct_only_low_mach_subcycling.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step108_low_mach_fsi_candidate.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step108_error_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step108_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step108_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step108_low_mach_subcycling_contract.py `
  tests\test_step108_error_comparison_contract.py `
  tests\test_step108_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
pytest -q
git diff --check
```

## Final Report Requirements

`STEP108_FLUENT_OFFICIAL_SPEED_LOW_MACH_SUBCYCLING_REPORT.md` must state:

- the exact Step108 allowed claim
- that Step108 does not validate Fluent and does not reproduce the official mesh/case/steady preflow
- the mapping values and subcycling count
- the duct-only finite-run result
- the FSI candidate completion status and row count
- the Step108 error metrics
- whether each soft goal improved over Step107
- all verification commands and their pass/fail status
- final commit hash and remote branch after push

## Push Requirement

When Step108 implementation and verification are complete, commit all relevant code, configs, docs, reports, logs, and generated artifacts, then push `main` to the configured GitHub remote. The final response must report:

- commit hash
- branch pushed
- key artifacts
- focused/full verification status
- remaining physical limitation if soft goals fail
