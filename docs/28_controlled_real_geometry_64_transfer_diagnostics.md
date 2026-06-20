# Step 28 Controlled Real Geometry 64 Transfer Diagnostics

Step 28 is controlled real geometry 64^3 transfer diagnostics.
Step 28 compares engineering and link_area_experimental transfer diagnostically.
Step 28 is not real squid validation.
Step 28 does not implement squid actuation.
Step 28 does not implement squid swimming.
Step 28 does not implement new FSI physics.
Step 28 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Driver Matrix

Step 28 reuses the accepted Step 25 real-geometry smoke candidates and the Step 26 strict driver-ready geometry configs. It runs four 64^3 moving_boundary rows only:

| candidate_id | geometry_type | coupling_mode | reaction_transfer_mode | n_lbm_steps |
| --- | --- | --- | --- | --- |
| real_candidate_smoke_mesh | mesh | moving_boundary | engineering | 10 |
| real_candidate_smoke_mesh | mesh | moving_boundary | link_area_experimental | 10 |
| real_candidate_smoke_voxel | voxel | moving_boundary | engineering | 10 |
| real_candidate_smoke_voxel | voxel | moving_boundary | link_area_experimental | 10 |

Each row uses strict geometry quality checks, `output_interval = 1`, no VTK output, and no particle output.

## Diagnostics

The committed Step 28 baselines are diagnostic artifacts:

- candidate fingerprint guard against the accepted Step 25 manifest;
- 64^3 paired transfer driver results;
- engineering vs link_area_experimental comparison deltas;
- force and reaction time-series summary;
- link-area area-scale envelope summary;
- Step 27 step-5 prefix regression;
- Step 27 regression guard;
- quality report aggregation;
- artifact manifest and budget check.

The link-area envelope reports the currently exposed final area scale plus the configured initialization baseline. It is a bounded diagnostic summary, not a claim that one transfer mode is more physically correct.

## Artifact Policy

Step 28 commits small CSV, JSON, NPZ, Markdown, config, log, and report artifacts only. It does not commit raw large real geometry, scan data, VTK outputs, or particle NPY outputs.
