# Step 59 Canonical FSIDriver Real Smoke Simulation Report

## Summary

Step 59 adds the first real smoke simulations through the canonical `FSIDriver3D` implementation after the Step 58 migration.

The smoke matrix imports:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
```

and calls `driver.run()` for each required row. This is not an import-only, constructor-only, proxy-only, or artifact-only check.

Step 59 also fixes the stale geometry-output filename in the canonical driver so `FSIDriverConfig(n_grid=N)` writes `geo_all_fluid_N.dat`.

## Required Smoke Rows

| Row | Coupling mode | Grid | Particles | LBM steps | MPM substeps per LBM step | Result |
| --- | --- | --- | --- | --- | --- | --- |
| `canonical_driver_none_16_1step` | `none` | 16^3 | 512 | 1 | 1 | pass |
| `canonical_driver_penalty_16_1step` | `penalty` | 16^3 | 512 | 1 | 1 | pass |
| `canonical_driver_moving_boundary_engineering_16_1step` | `moving_boundary` | 16^3 | 512 | 1 | 1 | pass |

The required rows use `geometry_type = box`, disabled VTK output, disabled particle output, disabled quality checks, static boundary motion, disabled wall-velocity application, static geometry motion, and disabled geometry-motion application.

## Smoke Evidence

The committed smoke matrix reports:

| Row | `driver.run()` called | Completed LBM steps | Diagnostics rows | `geo_path_name` | Stable | NaN | Inf |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `canonical_driver_none_16_1step` | true | 1 | 2 | `geo_all_fluid_16.dat` | true | false | false |
| `canonical_driver_penalty_16_1step` | true | 1 | 2 | `geo_all_fluid_16.dat` | true | false | false |
| `canonical_driver_moving_boundary_engineering_16_1step` | true | 1 | 2 | `geo_all_fluid_16.dat` | true | false | false |

The smoke quality audit confirms all three required rows are present, use the canonical module, call the real driver run path, and avoid legacy root-driver implementation ownership.

## Geo Path Naming Fix

The canonical driver now builds the geometry output path with:

```python
self.geo_path = os.path.join(self.out_dir, f"geo_all_fluid_{self.config.n_grid}.dat")
```

The Step 59 naming audit verifies:

| `n_grid` | Expected filename | Constructor created output files |
| --- | --- | --- |
| 16 | `geo_all_fluid_16.dat` | false |
| 32 | `geo_all_fluid_32.dat` | false |
| 48 | `geo_all_fluid_48.dat` | false |

This is an output naming correction only. It does not change solver formulas or physics.

## Evidence Artifacts

- `outputs/step59_driver_runs/canonical_driver_none_16_1step/`
- `outputs/step59_driver_runs/canonical_driver_penalty_16_1step/`
- `outputs/step59_driver_runs/canonical_driver_moving_boundary_engineering_16_1step/`
- `outputs/step59_canonical_driver_smoke_matrix/smoke_matrix.json`
- `outputs/step59_canonical_driver_smoke_quality/smoke_quality.json`
- `outputs/step59_geo_path_naming_audit/geo_path_naming_audit.json`
- `outputs/step59_output_guard/output_guard.json`
- `outputs/step59_step58_regression_guard/step58_regression_guard.json`
- `outputs/step59_artifact_manifest/artifact_summary.json`
- `logs/step59_*.log`

Each driver run directory is restricted to lightweight smoke artifacts:

- `driver_config.json`
- `geo_all_fluid_16.dat`
- `diagnostics_timeseries.csv`
- `diagnostics_timeseries.npz`

## Boundary

Step 59 does not add larger runs, 48^3 or 64^3 validation, runtime geometry activation, moving-wall velocity activation, link-area production validation, jet validation, squid swimming, real squid geometry validation, grid convergence, tau migration, or production-readiness claims.

Step 59 does not migrate the real boundary-motion, geometry-motion, wall-velocity, runtime-geometry, diagnostic-geometry, geometry-displacement, squid-proxy, real-geometry candidate, or external solver implementations. Step 58 compatibility shims and temporary bridge boundaries remain protected.

## Validation

The Step 59 validation commands are:

```powershell
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step59_geo_path_naming_audit.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step59_canonical_driver_smoke_matrix.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step59_canonical_driver_smoke_quality.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step59_output_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step59_step58_regression_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step59_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q tests/test_step59_canonical_driver_real_smoke_contract.py tests/test_step59_geo_path_naming_contract.py tests/test_step59_output_guard_contract.py tests/test_step59_step58_regression_contract.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q
D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
```

## Acceptance Checklist

- [x] Required Step 59 goal is recorded in `STEP59_CANONICAL_FSIDRIVER_REAL_SMOKE_SIMULATION_GOAL.md`.
- [x] `FSIDriver3D(...).run()` executes through `src.mpm_lbm.sim.drivers.fsi_driver`.
- [x] The required `none`, `penalty`, and `moving_boundary` engineering smoke rows pass.
- [x] The driver run artifacts remain lightweight and contain no `.vtr` files or particle `.npy` files.
- [x] `geo_all_fluid_{n_grid}.dat` naming is enforced for 16, 32, and 48 constructor probes.
- [x] Step 58 shim and bridge boundaries remain protected.
- [x] `external/taichi_LBM3D` and `data/real_geometry_candidates` remain unmodified.
