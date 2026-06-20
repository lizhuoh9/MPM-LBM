# Step 33 Controlled Squid Proxy Kinematics Mapping

Step 33 is controlled squid proxy kinematics mapping to boundary-motion diagnostics.
Step 33 maps schedules to displacement and velocity proxies only.
Step 33 does not integrate kinematics into FSIDriver3D.
Step 33 does not apply moving wall velocity to LBM.
Step 33 does not implement a jet model.
Step 33 does not implement squid swimming.
Step 33 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Purpose

Step 33 maps the accepted Step 32 schedule rows to region-level motion proxy diagnostics for the accepted Step 30 squid proxy regions. It is a diagnostic bridge between time schedules and region semantics, not a driver execution path.

The committed mapping tracks:

- `mantle_outer` with a radial displacement and velocity proxy;
- `mantle_cavity_proxy` with volume scale and volume-rate proxy diagnostics;
- `funnel_outlet_proxy` with aperture scale and aperture-rate proxy diagnostics.

## Motion Mapping

The Step 33 config lives in `configs/step33_squid_proxy_motion_mapping.json`:

| field | value |
| --- | --- |
| `mapping_id` | `step33_squid_proxy_boundary_motion_diagnostics` |
| `schedule_config_path` | `configs/step32_squid_proxy_kinematics_schedule.json` |
| `region_config_path` | `configs/step30_squid_proxy_region_config.json` |
| `geometry_config_path` | `configs/step30_squid_proxy_geometry.json` |
| `sample_count` | 32768 |
| `grid_sizes` | `[32, 48, 64]` |
| `tracked_regions` | `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy` |

All execution flags remain disabled: driver integration, LBM wall velocity, jet model, and actuation are false.

## Source Modules

- `src/squid_motion_mapping_config.py` defines immutable config and validation rows.
- `src/squid_motion_mapping.py` loads Step 32 schedule inputs, samples Step 30 regions, and emits aggregate motion rows.
- `src/squid_motion_quality.py` validates finite, bounded, region-complete motion diagnostics and disabled execution flags.
- `src/squid_motion_projection_diagnostics.py` summarizes diagnostic grid coverage at 32^3, 48^3, and 64^3.

These modules are CPU/NumPy diagnostic utilities. They do not import the driver, LBM stepper, MPM stepper, projector, penalty coupler, moving-boundary coupler, or link-area coupler.

## Artifacts

Step 33 commits small CSV, JSON, Markdown, and log artifacts only:

- `outputs/step33_motion_mapping_config_validation/`
- `outputs/step33_motion_mapping/`
- `outputs/step33_motion_quality/`
- `outputs/step33_motion_repeatability/`
- `outputs/step33_motion_grid_diagnostics/`
- `outputs/step33_schedule_motion_consistency/`
- `outputs/step33_step32_regression_guard/`
- `outputs/step33_artifact_manifest/`

No Step 33 `.vtr` outputs or particle `.npy` outputs are committed.

## Accepted Evidence

The accepted Step 33 artifacts show:

- motion mapping config validation: 20 of 20 rows pass;
- generated motion mapping: 243 rows from 81 schedule samples times 3 tracked regions;
- motion quality: finite, bounds, mantle, cavity, funnel, and disabled-flag checks all pass;
- repeatability: full motion, mantle motion, cavity motion, and funnel motion hashes repeat;
- grid diagnostics: 9 rows across 32^3, 48^3, and 64^3 with positive active-cell coverage;
- schedule-motion consistency: all 9 consistency checks pass against Step 32 schedule values;
- artifact manifest: no large files, no Step 33 VTR files, no Step 33 particle arrays, and Step 33 total artifact size below 5 MB.

## Boundaries

The displacement and velocity values are proxy diagnostics. They are not written to fluid boundary links, MPM particles, or coupled simulation state in Step 33.

No FSIDriver3D, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## Decision For Step 34

Step 34 should be `Controlled Squid Proxy Boundary-Motion Driver Interface Contract`. It may define a guarded driver interface schema such as `boundary_motion_mode = "static" | "prescribed_kinematic"` and verify default no-op behavior. Actual LBM boundary-motion application should wait until Step 35 or later.
