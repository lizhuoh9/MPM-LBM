# Step 32 Controlled Squid Proxy Prescribed Kinematics Schedule

Step 32 is controlled squid proxy prescribed kinematics schedule.
Step 32 defines kinematics schedules only.
Step 32 does not integrate kinematics into FSIDriver3D.
Step 32 does not apply moving wall velocity.
Step 32 does not implement mantle contraction in the driver.
Step 32 does not implement funnel actuation in the driver.
Step 32 does not implement squid swimming.
Step 32 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Purpose

Step 32 turns the accepted Step 30 and Step 31 static squid proxy regions into a deterministic schedule contract. The schedule is a postprocessing artifact and a future diagnostic input, not an execution path in the driver.

The committed schedule defines:

- mantle radius scale over one closed cycle;
- mantle cavity volume proxy scale over the same cycle;
- funnel aperture proxy scale over a configured open window;
- first-derivative diagnostics with respect to phase;
- repeatability hashes for the full schedule and each sub-schedule;
- region mapping compatibility against the accepted Step 30 region IDs.

## Schedule Contract

The schedule lives in `configs/step32_squid_proxy_kinematics_schedule.json`:

| field | value |
| --- | --- |
| `schedule_id` | `step32_squid_proxy_prescribed_cycle` |
| `cycle_period_steps` | 40 |
| `sample_count` | 81 |
| `contraction_start_phase` | 0.0 |
| `contraction_end_phase` | 0.35 |
| `refill_start_phase` | 0.35 |
| `refill_end_phase` | 1.0 |
| `mantle_radius_scale_min` | 0.85 |
| `cavity_volume_scale_min` | 0.60 |
| `funnel_aperture_scale_rest` | 0.35 |
| `funnel_aperture_scale_max` | 1.0 |

The endpoint phase samples are inclusive, so phase `0.0` and phase `1.0` both return the rest state. This makes the cycle directly repeatable for diagnostics.

## Source Modules

- `src/squid_kinematics_config.py` defines the immutable schedule config and validation rows.
- `src/squid_kinematics_schedule.py` defines phase samples, smoothstep/window helpers, scale schedules, derivative diagnostics, summaries, and CSV/JSON writing.
- `src/squid_kinematics_quality.py` checks finite values, configured bounds, monotonic phase, endpoint repeatability, derivative finiteness, contraction/refill rate direction, and disabled execution flags.
- `src/squid_kinematics_region_mapping.py` verifies that the future kinematic targets still map to `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy` while every Step 30 region remains inactive for actuation.

These modules are CPU/NumPy artifact utilities. They do not import the driver, LBM stepper, MPM stepper, projector, penalty coupler, moving-boundary coupler, or link-area coupler.

## Artifacts

Step 32 commits small CSV, JSON, Markdown, and log artifacts only:

- `outputs/step32_schedule_config_validation/`
- `outputs/step32_kinematics_schedule/`
- `outputs/step32_schedule_quality/`
- `outputs/step32_schedule_repeatability/`
- `outputs/step32_region_mapping_validation/`
- `outputs/step32_schedule_envelope_summary/`
- `outputs/step32_step31_regression_guard/`
- `outputs/step32_artifact_manifest/`

No Step 32 `.vtr` outputs or particle `.npy` outputs are committed.

## Accepted Evidence

The accepted Step 32 artifacts show:

- schedule config validation: 19 of 19 rows pass;
- generated schedule: 81 rows, phase range `[0.0, 1.0]`, endpoint repeatability pass;
- observed scale ranges: mantle `[0.85, 1.0]`, cavity `[0.6, 1.0]`, funnel `[0.35, 1.0]`;
- quality checks: finite, bounds, monotonic phase, endpoint repeatability, derivative finite, contraction/refill direction, and disabled flags all pass;
- repeatability: schedule, mantle, cavity, and funnel hashes repeat;
- region mapping: all 7 Step 30 required regions remain present and inactive for actuation;
- artifact manifest: no large files, no Step 32 VTR files, no Step 32 particle arrays, and Step 32 total artifact size below 3 MB.

## Boundaries

The mantle radius scale, cavity volume scale, and funnel aperture scale are prescribed schedule diagnostics. They are not applied to LBM boundary links, MPM particles, or a coupled simulation state in Step 32.

No FSIDriver3D, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## Decision For Step 33

Step 33 should be `Controlled Squid Proxy Kinematics Mapping To Boundary-Motion Diagnostics`. It may map the accepted Step 32 schedule to region displacement and velocity proxies for diagnostics only. It must not integrate moving wall velocity into LBM, must not add a jet path, and must not claim swimming behavior. Real driver integration should wait for Step 34 or later.
