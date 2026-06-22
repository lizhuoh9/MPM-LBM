# Real Geometry Data Boundary

The real geometry support surface is available for controlled intake policy
checks, but it is not activated for solver runtime use.

Step74 verifies that the canonical API can be imported, candidate descriptor
rules reject unsafe identity and commit-policy claims, manifest helpers redact
absolute paths, and output artifacts stay small and local to Step74 audit
directories.

`run_candidate_projection_smoke()` remains present in
`src/mpm_lbm/sim/geometry/intake.py`, but Step74 does not call it. Projection
smoke execution requires a later explicitly authorized post-gate step.

`experiments/steps/real_geometry_feasibility/feasibility.py` remains quarantined
experiment code. It is not part of the runtime solver API, and Step74 does not
execute its driver helpers.
