# Step104 Fluent Duct-Flap Official Problem Setup Repair Report

Allowed claim:

```text
Fluent duct-flap problem setup repair is wired for a short proxy smoke, and the remaining Fluent-equivalence gaps are explicitly reported.
```

This report does not claim Fluent equivalence, Fluent validation, physical
validation, real FSI validation, completion of the full 50-step public tutorial
transient, or production readiness.

## Implementation Summary

- Added explicit `initial_solid_velocity_norm` to `FSIDriverConfig`; default is
  zero.
- Stopped using `target_u_lbm` as initial solid velocity. In Step104 it is used
  only as the x-min LBM inlet target.
- Added `duct_velocity_inlet_pressure_outlet` driver setup with x-min velocity
  inlet and x-max pressure outlet LBM config/reporting.
- Added deterministic duct static geometry writing as
  `geo_duct_flap_proxy_48.dat`; Step104 no longer uses `geo_all_fluid_48.dat`.
- Added duct-flap fixed-base and free-tip masks from the sampler.
- Added MPM fixed-particle constraints and fixed-base diagnostics.
- Mapped the Step104 silicone material reference into MPM config:
  `p_rho = 1600.0`, `young_modulus = 1000000.0`, `poisson_ratio = 0.47`.
- Disabled Step36 squid wall velocity for the Step104 row.
- Added proxy flap-tip displacement time series output.
- Added Step104 setup runner, output guard, artifact manifest, docs, tests, and
  committed evidence.

No LBM collision, tau, MPM update, moving-boundary, coupling, or
reaction-transfer formulas were changed.

## Solver Smoke Result

Artifact: `outputs/step104_fluent_duct_flap_setup_repair/setup_repair_report.json`

- row: `fluent_duct_flap_setup_repair_48_5step_smoke`
- canonical driver: `src.mpm_lbm.sim.drivers.fsi_driver`
- geometry type: `duct_flap_proxy`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- completed LBM steps: `5`
- diagnostics rows: `6`
- `has_nan = false`
- `has_inf = false`
- stable: `true`
- `target_u_lbm_applied_to_solid_initial_velocity = false`
- `target_u_lbm_applied_to_inlet = true`
- `all_fluid_geometry_used = false`
- `step36_squid_wall_velocity_config_used = false`

## Boundary And Geometry Result

Artifacts:

- `outputs/step104_fluent_duct_flap_setup_repair/duct_boundary_condition_report.json`
- `outputs/step104_fluent_duct_flap_setup_repair/duct_static_geometry_report.json`

Recorded values:

- `lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet`
- `bc_x_left = 2`
- `bc_x_right = 1`
- velocity inlet cell count: `80`
- pressure outlet cell count: `80`
- duct wall cell count: `106752`
- fluid cell count: `3840`
- solid cell count: `106752`
- static geometry file: `geo_duct_flap_proxy_48.dat`

## Fixed Base And Monitor Result

- fixed-base particle count: `319`
- fixed-base max displacement norm: `0.0`
- fixed-base max velocity norm: `0.0`
- free-tip proxy particle count: `256`
- proxy flap-tip displacement CSV exists with rows for steps `0` through `5`
- direct quantitative Fluent equivalence remains disallowed

## Guard Results

- Step104 output guard: passed
- Step104 artifact manifest: passed
- official/proprietary Fluent file count: `0`
- private Fluent CSV committed count: `0`
- Step36 wall-velocity reference count in Step104 configs/outputs/logs: `0`
- `.vtr` count: `0`
- particle `.npy` count: `0`
- video count: `0`
- protected external edit count: `0`
- protected real-geometry candidate edit count: `0`

## Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\sim\drivers\fsi_config.py src\mpm_lbm\sim\drivers\fsi_driver.py src\mpm_lbm\sim\geometry\config.py src\mpm_lbm\sim\geometry\sampler.py src\mpm_lbm\sim\geometry\duct_flap_proxy.py src\mpm_lbm\sim\mpm\solid.py src\mpm_lbm\evidence\step104_common.py src\mpm_lbm\evidence\step104_fluent_duct_flap_setup_gap_report.py src\mpm_lbm\evidence\step104_fluent_duct_flap_setup_repair_runner.py src\mpm_lbm\evidence\step104_output_guard.py baseline_tests\step104_common.py baseline_tests\run_step104_fluent_duct_flap_setup_repair.py baseline_tests\run_step104_output_guard.py baseline_tests\run_step104_artifact_manifest.py tests\test_step104_fluent_duct_flap_setup_repair_contract.py tests\test_step104_output_guard_contract.py
```

Result: passed.

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step104_fluent_duct_flap_setup_repair.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step104_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step104_artifact_manifest.py
```

Result: all passed.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step104_fluent_duct_flap_setup_repair_contract.py tests\test_step104_output_guard_contract.py
```

Result: `7 passed in 1.37s`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Result: `1153 passed in 173.22s`.

```powershell
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
```

Result: `1153 passed, 1 warning in 70.88s`.
The warning is a Taichi dependency deprecation warning for
`locale.getdefaultlocale` on the Anaconda interpreter.

```powershell
pytest -q
```

Result: `1153 passed, 1 warning in 70.51s`.
This is the entrypoint used by the ECC pre-push hook.

## Final Guard Snapshot

- setup repair pass: `true`
- setup repair elapsed seconds: `66.74156330000551`
- output guard pass: `true`
- output guard row count: `24`
- output guard total size: `0.34502220153808594 MB`
- artifact manifest pass: `true`
- Step104 file count: `40`
- Step104 total artifact size: see
  `outputs/step104_artifact_manifest/artifact_summary.csv`
