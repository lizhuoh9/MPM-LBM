# Step 30 Controlled Squid Proxy Region Geometry

Step 30 is controlled squid proxy region geometry.
Step 30 defines squid-like region semantics only.
Step 30 is not real squid validation.
Step 30 does not implement squid actuation.
Step 30 does not implement squid swimming.
Step 30 does not implement mantle contraction.
Step 30 does not implement funnel actuation.
Step 30 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Purpose

Step 30 adds a static semantic descriptor for the existing procedural `squid_proxy` geometry. The descriptor gives stable IDs and diagnostics to squid-like proxy regions before any future driver work tries to reason about region-specific projection or prescribed motion.

The required regions are:

| region_id | role | semantics |
| --- | --- | --- |
| `mantle_outer` | `solid_region` | existing mantle ellipsoid proxy |
| `mantle_cavity_proxy` | `cavity_proxy` | smaller static ellipsoid inside the mantle proxy |
| `funnel_outlet_proxy` | `outlet_proxy` | small static outlet semantic proxy near the mantle boundary |
| `head_proxy` | `solid_region` | existing head ellipsoid proxy |
| `arms_proxy` | `appendage_proxy` | existing coarse arm capsule union |
| `left_fin_proxy` | `fin_proxy` | existing left fin proxy |
| `right_fin_proxy` | `fin_proxy` | existing right fin proxy |

The descriptor also fixes:

- `body_axis = +y`;
- `reference_length = 1.0`;
- `body_frame_origin = [0.5, 0.5, 0.5]`;
- documented allowed overlap pairs for static semantic proxy regions.

## Files

Step 30 adds:

- `src/squid_region_config.py` for immutable region schema and validation;
- `src/squid_proxy_regions.py` for deterministic proxy masks and summaries;
- `src/squid_region_quality.py` for region quality and overlap diagnostics;
- `src/squid_region_projection.py` for projection-only region accumulation;
- `configs/step30_squid_proxy_geometry.json`;
- `configs/step30_squid_proxy_region_config.json`;
- `baseline_tests/run_step30_*.py` runners;
- `tests/test_step30_squid_proxy_region_geometry_contract.py`.

## Diagnostics

Committed Step 30 diagnostics are small CSV, JSON, and log artifacts:

- region schema validation;
- deterministic region mask sampling;
- region quality;
- region overlap diagnostics;
- 32^3 and 48^3 projection-only smoke;
- Step 29 regression guard;
- artifact manifest.

Projection-only smoke does not run `FSIDriver3D`, LBM stepping, MPM stepping, moving-boundary coupling, or link-area transfer. It only accumulates deterministic region point clouds into grid-index diagnostics.

## Boundaries

The mantle cavity proxy is a geometry semantic. It is not a real internal fluid cavity. The funnel outlet proxy is a static geometry semantic. It is not a moving aperture and not a jet model.

No FSI, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## Step 31 Direction

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

Step 31 adds region-aware projection aggregation at 32^3, 48^3, and 64^3, plus a four-row static `FSIDriver3D` smoke matrix for existing modes. Prescribed mantle or funnel kinematics remain out of scope for Step 31.

## Step 32 Direction

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

Step 32 defines deterministic mantle radius, mantle cavity volume proxy, and funnel aperture proxy schedules as artifacts only. Driver integration remains a later step.
