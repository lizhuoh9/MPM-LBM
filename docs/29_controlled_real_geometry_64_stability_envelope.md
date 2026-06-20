# Step 29 Controlled Real Geometry 64 Stability Envelope

Step 29 is controlled real geometry 64^3 short-window stability envelope.
Step 29 extends Step 28 transfer diagnostics conservatively.
Step 29 is not real squid validation.
Step 29 does not implement squid actuation.
Step 29 does not implement squid swimming.
Step 29 does not implement new FSI physics.
Step 29 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Driver Matrix

Step 29 reuses the accepted Step 25 real-geometry smoke candidates, Step 26 strict driver-ready geometry configs, and Step 28 transfer matrix. It runs four 64^3 moving_boundary rows only:

| candidate_id | geometry_type | coupling_mode | reaction_transfer_mode | n_lbm_steps |
| --- | --- | --- | --- | --- |
| real_candidate_smoke_mesh | mesh | moving_boundary | engineering | 20 |
| real_candidate_smoke_mesh | mesh | moving_boundary | link_area_experimental | 20 |
| real_candidate_smoke_voxel | voxel | moving_boundary | engineering | 20 |
| real_candidate_smoke_voxel | voxel | moving_boundary | link_area_experimental | 20 |

Each row uses strict geometry quality checks, `output_interval = 1`, no VTK output, and no particle output.

## Diagnostics

The committed Step 29 baselines are diagnostic artifacts:

- candidate fingerprint guard against the accepted Step 25 manifest;
- 64^3 20-step stability driver results;
- stability envelope summary from time-series diagnostics;
- engineering vs link_area_experimental envelope deltas;
- force and reaction envelope summary;
- link-area area-scale envelope summary;
- Step 28 step-10 prefix regression;
- Step 28 regression guard;
- quality report aggregation;
- artifact manifest and budget check.

Step 29 is a short-window stability envelope. It does not add squid motion, production mesh repair, or new solver behavior.

## Decision For Step 30

Step 30 should be controlled squid proxy region geometry. It should define squid-like region semantics only: mantle outer, mantle cavity proxy, funnel outlet proxy, head proxy, arms proxy, optional fin proxies, body axis, reference length, body-frame origin, and deterministic region diagnostics.

Step 30 is not real squid validation. Step 30 should not implement squid actuation, swimming, mantle contraction, funnel actuation, or new FSI physics.

## Artifact Policy

Step 29 commits small CSV, JSON, NPZ, Markdown, config, log, and report artifacts only. It does not commit raw large real geometry, scan data, VTK outputs, or particle NPY outputs.
