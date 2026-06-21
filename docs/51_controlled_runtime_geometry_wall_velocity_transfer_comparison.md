# Step 51 Controlled Runtime Geometry Wall Velocity Transfer Comparison

Step 51 is controlled one-cycle runtime geometry plus wall velocity transfer comparison.
Step 51 compares engineering and link_area_experimental diagnostically.
Step 51 remains 32^3 and one-cycle.
Step 51 remains non-persistent.
Step 51 does not validate real jet propulsion.
Step 51 does not implement squid swimming.
Step 51 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Scope

This step extends the accepted Step 50 one-cycle diagnostic envelope from four
engineering-only rows to eight rows: four engineering rows and four
link_area_experimental rows. Both transfer modes use the same 32^3 grid, the
same forty LBM steps, the same five MPM substeps per LBM step, the same phase
sequence, and the same non-persistent runtime geometry plus wall velocity
diagnostic pipeline.

The link-area transfer path is bounded by `link_area_scale_min = 0.25` and
`link_area_scale_max = 2.0`. The comparison is finite, bounded, and diagnostic.
It is not a production solver activation or a physical validation result.

## Artifacts

Step 51 writes small CSV, JSON, NPZ, and log artifacts under `outputs/step51_*`
and `logs/step51_*`. It does not write VTR, particle NPY, displaced-particle,
dense-displacement, scan-data, or raw real-geometry artifacts.

## Decision Boundary

Passing Step 51 means the accepted Step 50 one-cycle envelope can be compared
against a separately bounded link_area_experimental transfer diagnostic. A later
step may choose one transfer mode for a selected 48^3 feasibility probe, but it
should not expand grid size, transfer matrix size, and cycle count at the same
time.
