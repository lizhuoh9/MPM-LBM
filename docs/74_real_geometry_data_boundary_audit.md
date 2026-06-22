# Step74 Real Geometry Data Boundary Audit

Step74 adds an audit-only real geometry data boundary layer. It checks canonical
real geometry imports, synthetic descriptor constraints, manifest/fingerprint
policy, quarantine status for the historical feasibility experiment, output
policy, all 10 Step70 activation gates, no-simulation constraints, and Step73
regression evidence.

Step74 does not execute `FSIDriver3D`, `driver.initialize()`, `driver.step_once()`,
`driver.run()`, or `run_candidate_projection_smoke()`. It does not add real
geometry data, does not edit `data/real_geometry_candidates`, and does not edit
`external/taichi_LBM3D`.

The accepted claim is:

```text
real_geometry_boundary_audit_ready_for_later_data_decision_only
```

All activation gates remain closed. Real geometry activation remains false.
