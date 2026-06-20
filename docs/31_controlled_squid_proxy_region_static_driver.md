# Step 31 Controlled Squid Proxy Region Static Driver

Step 31 is controlled squid proxy region projection and static driver smoke.
Step 31 uses static squid proxy region semantics only.
Step 31 is not real squid validation.
Step 31 does not implement squid actuation.
Step 31 does not implement squid swimming.
Step 31 does not implement mantle contraction.
Step 31 does not implement funnel actuation.
Step 31 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Purpose

Step 31 carries the accepted Step 30 static region schema into two conservative checks:

- projection-only region diagnostics at 32^3, 48^3, and 64^3;
- a 48^3 `FSIDriver3D` static smoke matrix for existing modes only.

The static driver smoke uses the existing procedural `squid_proxy`, existing MPM-to-LBM projection, existing none/penalty/moving_boundary modes, and the opt-in existing `link_area_experimental` transfer. It does not add prescribed mantle motion, funnel motion, body motion, or a jet model.

## Driver Matrix

The four committed Step 31 driver rows are:

| candidate_id | n_grid | coupling_mode | reaction_transfer_mode | n_lbm_steps | mpm_substeps_per_lbm_step |
| --- | --- | --- | --- | --- | --- |
| `squid_proxy_region` | 48 | `none` | `engineering` | 5 | 5 |
| `squid_proxy_region` | 48 | `penalty` | `engineering` | 5 | 5 |
| `squid_proxy_region` | 48 | `moving_boundary` | `engineering` | 5 | 5 |
| `squid_proxy_region` | 48 | `moving_boundary` | `link_area_experimental` | 5 | 5 |

Each row enables strict geometry quality checks and disables VTK and particle output.

## Region Context

`src/squid_region_driver_diagnostics.py` treats Step 30 region projection as semantic context beside driver diagnostics. It does not require region masses to sum to driver projected mass because Step 30 intentionally documents overlapping static semantic regions.

The committed alignment artifact writes the note:

```text
region projection is semantic context, not a mass partition
```

## Quality Semantics

The procedural `squid_proxy` can appear as multiple connected components in coarse diagnostic voxelization because appendage and fin proxy components are static semantic parts. Step 31 records this explicitly in quality reports with:

```text
allow_disconnected_components = true
component_semantics = static squid proxy appendage and fin components may be disconnected in coarse diagnostic voxelization
```

This is a quality-report interpretation for procedural diagnostics only. It does not change the MPM sampler, LBM projection formula, moving bounce-back formula, penalty coupling, engineering moving-boundary reaction transfer, or link-area transfer formula.

## Artifacts

Committed Step 31 artifacts are small CSV, JSON, NPZ, and log files:

- `outputs/step31_region_projection_scale/`
- `outputs/step31_static_driver_smoke/`
- `outputs/step31_region_driver_alignment/`
- `outputs/step31_engineering_vs_link_area_static_comparison/`
- `outputs/step31_quality_report_aggregation/`
- `outputs/step31_step30_regression_guard/`
- `outputs/step31_artifact_manifest/`

No Step 31 `.vtr` outputs or particle `.npy` outputs are committed.

## Decision For Step 32

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

Step 32 defines mantle radius schedule, mantle cavity volume proxy schedule, funnel aperture proxy schedule, cycle period, phase/ramp semantics, derivative diagnostics, repeatability hashes, region mapping compatibility, and artifact budget checks. These are schedule artifacts only.

## Decision For Step 33

Step 33 should be `Controlled Squid Proxy Kinematics Mapping To Boundary-Motion Diagnostics`. It may map the accepted Step 32 schedule to region displacement and velocity proxies for diagnostics only. Real driver integration should wait for Step 34 or later.

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
