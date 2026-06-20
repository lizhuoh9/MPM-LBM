# Step 34 Goal: Controlled Squid Proxy Boundary-Motion Driver Interface Contract

## Objective

Implement Step 34 as a controlled, quality-gated driver-side boundary-motion interface for the squid proxy workflow. The interface must make prescribed kinematic boundary-motion inputs visible to `FSIDriver3D` as validated diagnostics and reports, while preserving the existing static solver behavior and leaving all LBM, MPM, projection, moving bounce-back, and coupler formulas unchanged.

Step 34 is not an actuation or propulsion feature. It is a no-op interface contract that proves the driver can load, validate, and report a guarded prescribed-kinematic boundary-motion schema without applying that motion to the fluid or solid state.

## Required Scope Statements

- Step 34 is controlled squid proxy boundary-motion driver interface.
- Step 34 defines a guarded driver interface only.
- Step 34 keeps prescribed kinematics diagnostic-only.
- Step 34 does not apply moving wall velocity to LBM.
- Step 34 does not implement a jet model.
- Step 34 does not implement squid swimming.
- Step 34 does not implement new FSI physics.
- The default boundary_motion_mode remains static.
- The default quality_check_enabled remains false.
- The default quality_check_strict remains false.
- The default reaction_transfer_mode remains engineering.
- The moving bounce-back formula is unchanged.
- PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Non-Goals

- Do not apply moving-wall velocity to LBM populations.
- Do not modify the moving bounce-back formula.
- Do not write prescribed kinematic velocity into LBM fields.
- Do not implement jet generation, mantle actuation, funnel actuation, free-body swimming, internal-fluid cavity dynamics, or real-squid validation.
- Do not add new FSI physics, new coupling formulas, production mesh repair, two-phase physics, contact-angle behavior, sparse storage, or edits under `external/taichi_LBM3D`.
- Do not claim solver readiness, production readiness, final physical validation, or completed strict momentum-conserving FSI.

## Config Contract

Extend `src/fsi_config.py` with:

- `VALID_BOUNDARY_MOTION_MODES = ("static", "prescribed_kinematic")`
- `boundary_motion_mode: str = "static"`
- `boundary_motion_config_path: Optional[str] = None`
- `boundary_motion_report_enabled: bool = False`

Validation requirements:

- `boundary_motion_mode` must be one of the valid modes.
- Static mode must remain the default and must require no config path.
- Prescribed-kinematic mode must require a boundary-motion config path.
- The default quality and transfer fields must remain unchanged.

## Boundary-Motion Config Contract

Add `src/boundary_motion_config.py` with an immutable config object for the Step 34 interface. It must load from JSON, emit a serializable dictionary, and validate the diagnostic-only contract.

Required config semantics:

- It references the Step 32 schedule config and Step 33 motion mapping config.
- `diagnostic_only` must be true.
- Driver, LBM wall velocity, jet, actuation, LBM population, MPM grid, projector, and coupling integration flags must all be false.
- It must validate required source paths and expected row counts.
- Failed validation must stop the diagnostic interface before any report is treated as passing.

## Boundary-Motion Interface Contract

Add `src/boundary_motion_interface.py` as the no-op interface layer.

The module may:

- Load and validate the Step 34 boundary-motion config.
- Read Step 32 schedule rows through the existing schedule API.
- Read Step 33 motion mapping rows through the existing motion-mapping API.
- Write a report summarizing mode, source paths, guarded flags, row counts, finite checks, and no-op status.

The module must not:

- Mutate `LBMFluid3D`, `MPMSolid3D`, `MPMToLBMProjector3D`, or any FSI coupler.
- Apply wall velocity, solid velocity, forces, populations, grid state, or projection state.
- Change solver state beyond writing the explicit JSON report requested by config.

## Driver Hook Contract

Modify `src/fsi_driver.py` with a minimal no-op hook:

- Add `self.boundary_motion_interface_report = None`.
- During initialization, if report generation is enabled, load the boundary-motion interface config, validate that all execution flags are disabled, and write `boundary_motion_interface_report.json` under the driver output directory.
- Static mode must not write a report unless explicitly enabled.
- Prescribed-kinematic mode must produce a report only when the interface validates as diagnostic-only.
- The hook must not change any coupling path, LBM step path, MPM substep path, projection path, or moving-bounceback path.

## Config Files To Add

- `configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `configs/step34_squid_proxy_static_48_none.json`
- `configs/step34_squid_proxy_static_48_penalty.json`
- `configs/step34_squid_proxy_static_48_moving_boundary.json`
- `configs/step34_squid_proxy_static_48_link_area.json`
- `configs/step34_squid_proxy_prescribed_interface_48_moving_boundary.json`
- `configs/step34_squid_proxy_prescribed_interface_48_link_area.json`

All Step 34 driver configs must use:

- `geometry_type = "squid_proxy"`
- `geometry_config_path = "configs/step30_squid_proxy_geometry.json"`
- `n_grid = 48`
- `n_particles = 4096`
- `n_lbm_steps = 5`
- `mpm_substeps_per_lbm_step = 5`
- `output_interval = 1`
- strict quality checks enabled for these controlled Step 34 runs
- VTK and particle exports disabled

Static rows must set `boundary_motion_mode = "static"`, `boundary_motion_config_path = null`, and `boundary_motion_report_enabled = false`.

Prescribed-interface rows must set `boundary_motion_mode = "prescribed_kinematic"`, reference the Step 34 boundary-motion config, and enable the interface report.

## Baseline Runner Contract

Add Step 34 baseline runners that produce committed, small, deterministic artifacts:

- `baseline_tests/step34_common.py`
- `baseline_tests/run_step34_boundary_motion_config_validation.py`
- `baseline_tests/run_step34_boundary_motion_interface_report.py`
- `baseline_tests/run_step34_static_driver_regression.py`
- `baseline_tests/run_step34_prescribed_interface_noop_smoke.py`
- `baseline_tests/run_step34_step31_static_comparison.py`
- `baseline_tests/run_step34_noop_state_guard.py`
- `baseline_tests/run_step34_quality_report_aggregation.py`
- `baseline_tests/run_step34_step33_regression_guard.py`
- `baseline_tests/run_step34_artifact_manifest.py`

The runners must verify:

- Boundary-motion config validation passes.
- The generated interface report is diagnostic-only.
- Schedule row count remains 81.
- Motion mapping row count remains 243.
- Tracked region count remains 3.
- Static Step 34 driver rows remain stable.
- Prescribed-interface Step 34 moving-boundary rows are no-op relative to static Step 34 moving-boundary rows for the checked diagnostics.
- Step 31 and Step 33 accepted artifacts remain intact.
- Strict geometry quality reports pass.
- No `.vtr`, particle `.npy`, large raw geometry, scan data, private absolute paths, or oversized Step 34 outputs are introduced.

## Test Contract

Add `tests/test_step34_boundary_motion_driver_interface_contract.py` with contract coverage for:

- Required files and output artifacts.
- `FSIDriverConfig` defaults and validation.
- Boundary-motion config validation.
- Boundary-motion interface report schema and no-op flags.
- Static driver regression rows.
- Prescribed-interface no-op smoke rows.
- Step 31 static comparison guard.
- No-op state guard.
- Quality aggregation.
- Step 33 regression guard.
- Scope documentation and forbidden overclaim guard.
- Artifact budget.
- Report acceptance checklist.
- External dependency cleanliness.

## Documentation And Report Contract

Add:

- `docs/34_controlled_squid_proxy_boundary_motion_driver_interface.md`
- `STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md`

The report must contain these sections:

1. Goal
2. Files Created And Updated
3. Explicit Non-Goals
4. Boundary-Motion Config Validation
5. Boundary-Motion Interface Report
6. Static Driver Regression
7. Prescribed Interface No-Op Smoke
8. Step 31 Static Comparison
9. No-Op State Guard
10. Quality Report Aggregation
11. Step 33 Regression Guard
12. Artifact Manifest Summary
13. Verification Commands
14. GitHub Sync Information
15. Acceptance Checklist
16. Decision For Step 35

The Step 35 decision must point to a controlled moving-wall velocity field diagnostic contract that still does not update LBM populations.

## Verification Contract

Run and capture logs for:

- `python -m py_compile src/fsi_config.py src/fsi_driver.py src/boundary_motion_config.py src/boundary_motion_interface.py`
- all Step 34 baseline runners
- trusted full `pytest -q`
- Step 34 contract pytest
- `git diff --check`
- staged whitespace check before commit
- external/data status checks
- push to `origin/main`

Commit message:

`test: add step34 boundary motion driver interface contract`
