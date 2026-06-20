# Step 34 Controlled Squid Proxy Boundary-Motion Driver Interface

Step 34 is controlled squid proxy boundary-motion driver interface.
Step 34 defines a guarded driver interface only.
Step 34 keeps prescribed kinematics diagnostic-only.
Step 34 does not apply moving wall velocity to LBM.
Step 34 does not implement a jet model.
Step 34 does not implement squid swimming.
Step 34 does not implement new FSI physics.
The default boundary_motion_mode remains static.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Purpose

Step 34 introduces a small driver-side interface contract that lets `FSIDriver3D` load and report a prescribed-kinematic boundary-motion schema without applying it to LBM, MPM, projection, or coupling state.

The new `FSIDriverConfig` fields are:

- `boundary_motion_mode`, default `static`
- `boundary_motion_config_path`, default `None`
- `boundary_motion_report_enabled`, default `False`

The only non-static mode in this step is `prescribed_kinematic`, and it must point to `configs/step34_boundary_motion_interface_prescribed_kinematic.json`.

## Interface Config

The Step 34 interface config references accepted Step 32 and Step 33 artifacts:

| field | value |
| --- | --- |
| `schedule_config_path` | `configs/step32_squid_proxy_kinematics_schedule.json` |
| `motion_mapping_config_path` | `configs/step33_squid_proxy_motion_mapping.json` |
| `schedule_output_path` | `outputs/step32_kinematics_schedule/kinematics_schedule.json` |
| `motion_mapping_output_path` | `outputs/step33_motion_mapping/motion_mapping.json` |
| `expected_schedule_row_count` | 81 |
| `expected_motion_row_count` | 243 |
| `expected_tracked_region_count` | 3 |

All execution flags are false. The config validation artifact checks driver integration, LBM wall velocity, LBM population update, MPM grid velocity, projector integration, coupling integration, moving-bounceback update, jet model, and actuation flags.

## Driver Hook

`FSIDriver3D.initialize()` now calls a report-only boundary-motion hook after output directory creation and driver config serialization. The hook writes `boundary_motion_interface_report.json` only when `boundary_motion_report_enabled` is true.

Static Step 34 driver rows do not write this report. Prescribed-interface rows write the report and then continue through the same existing moving_boundary stepping paths.

The Step 34 driver change is limited to config validation and report writing. It does not alter `_step_none`, `_step_penalty`, `_step_moving_boundary`, the LBM stepper, the MPM substep loop, the projector, or any FSI coupler formula.

## Accepted Evidence

The accepted Step 34 artifacts show:

- boundary-motion config validation: 21 of 21 checks pass;
- standalone interface report: 81 schedule rows, 243 motion rows, 3 tracked regions, and `no_op_pass = true`;
- static driver regression: 4 rows pass with strict geometry quality gates;
- prescribed interface no-op smoke: 2 moving_boundary rows pass and write reports;
- no-op state guard: max static-vs-prescribed float delta is below `1.0e-6`, with zero integer mismatches;
- Step 31 static comparison: all 4 rows pass within the short-run tolerance;
- Step 33 regression guard: all accepted Step 33 schedule and motion diagnostics remain intact;
- artifact manifest: no Step 34 `.vtr` outputs, no Step 34 particle `.npy` outputs, no large files, and Step 34 total artifact size below 10 MB.

## Boundaries

The prescribed kinematics remain diagnostics. They are not written to fluid populations, moving links, MPM particles, MPM grid velocities, projector state, or coupler state.

Step 35 may introduce a controlled moving-wall velocity field diagnostic contract. That next step should still avoid LBM population updates until a later explicitly validated contract.
