# Project Status

Current status: engineering prototype.

Step 11 is documentation and reproducibility work. It converts the Step 1-10 prototype into a readable package without adding solver code or new FSI physics.

## Completed Milestones

- Step 1: environment and baselines
- Step 2: refactored LBMFluid3D
- Step 3: MPMSolid3D
- Step 4: unified units, grid, timestep
- Step 5: MPM-to-LBM projection
- Step 6: penalty coupling MVP
- Step 7: penalty validation and stability window
- Step 8: moving bounce-back scaffold
- Step 9: moving-boundary reaction coupling
- Step 10: unified FSI driver
- Step 54: repository evidence integrity repair
- Step 55: repository code layout separation and import-boundary contract
- Step 56: canonical runtime implementation migration wave 1
- Step 57: canonical driver support migration wave 2
- Step 58: canonical FSIDriver implementation migration wave 3
- Step 59: canonical FSIDriver real smoke simulation
- Step 60: controlled canonical moving-boundary duration ramp
- Step 61: controlled canonical 32^3 moving-boundary single-step probe
- Step 62: controlled canonical 32^3 moving-boundary 3-step duration probe
- Step 70: API and config freeze before activation
- Step 71: output default safety alignment and LBM tau convention decision
- Step 72: runtime geometry activation readiness audit
- Step 73: wall velocity activation readiness audit
- Step 74: real geometry data boundary audit
- Step 75: solver-complete simulation campaign readiness gate
- Step 76: minimal post-gate canonical driver rebaseline
- Step 77: minimal post-gate canonical driver 3-step rebaseline
- Step 78: minimal post-gate canonical driver 5-step rebaseline

## Current Validated Modes

- none
- penalty
- moving_boundary

The current mode matrix is validated through committed Step 10 logs and outputs. The validation scale is small-scale 32^3 / 4096-particle engineering baselines.

Step 59 additionally verifies that the canonical `FSIDriver3D` implementation can execute real one-step smoke runs for the `none`, `penalty`, and `moving_boundary` engineering modes at 16^3 with 512 particles. This is a post-migration canonical-driver smoke check, not a larger validation campaign.

Step 60 additionally verifies a short controlled canonical real-driver duration ramp at 16^3 with 512 particles: moving-boundary engineering rows at 3 and 5 LBM steps, plus a penalty row at 5 LBM steps. This remains a finite/bounded smoke extension, not a broader validation campaign.

Step 61 additionally verifies a controlled canonical 32^3 real-driver single-step probe for the moving-boundary engineering mode with 1024 particles. This remains a finite/bounded feasibility smoke, not 32^3 validation or grid convergence.

Step 62 additionally verifies a controlled canonical 32^3 real-driver 3-step duration probe for the moving-boundary engineering mode with 1024 particles, repairs the Step 61 report output-guard size mismatch, and adds a report consistency guard. This remains a finite/bounded duration feasibility smoke, not propulsion validation, real squid validation, grid convergence, or deployment readiness.

Step 71 changes `FSIDriverConfig` file-output defaults so VTR and particle NPY
outputs require explicit opt-in. It also records the tau convention decision:
`niu` remains the legacy external solver relaxation parameter for now, and the
standard lattice viscosity formula is available but not default. Step 71 does
not validate physical viscosity or change the LBM tau formula used by the
solver.

Step 72 adds an audit-only runtime geometry activation readiness layer. It
checks canonical runtime geometry imports, schema stability, driver config gates,
state guard invariants, output policy, no-simulation constraints, and Step71
regression evidence. It does not run `FSIDriver3D`, activate runtime geometry,
activate wall velocity, or claim physical validation.

Step 73 adds an audit-only wall velocity activation readiness layer. It checks
canonical wall velocity imports, schema stability, driver config gates,
application safety, output policy, all 10 Step70 activation gates, no-simulation
constraints, and Step72 regression evidence. It does not run `FSIDriver3D`,
activate wall velocity, update LBM populations, modify bounce-back formulas, or
claim physical validation.

Step 74 adds an audit-only real geometry data boundary layer. It checks
canonical real geometry imports, synthetic descriptor constraints, manifest and
fingerprint policy, quarantine status for `experiments/steps/real_geometry_feasibility`,
output policy, all 10 Step70 activation gates, no-simulation constraints, and
Step73 regression evidence. It does not run `FSIDriver3D`, execute projection
smoke, add real geometry data, edit `data/real_geometry_candidates`, or claim
physical validation.

Step 75 adds a gate-only solver-complete simulation campaign readiness layer.
It aggregates committed Step71-Step74 evidence, confirms all Step70 activation
gates remain closed, and records that the next allowed work is Step76 minimal
safe rebaseline only. The inactive Step76 proposal starts with one
32^3/one-step moving-boundary engineering rebaseline row with runtime geometry,
wall velocity, real geometry, squid proxy, VTR output, and particle NPY output
all disabled. Step75 does not run `FSIDriver3D`, execute projection smoke,
change solver formulas, migrate tau semantics, add 48^3 or 64^3 rows, claim
physical validation, or claim production readiness.

Step 76 runs the minimal post-gate canonical driver rebaseline authorized by
Step75: one 32^3, 1024-particle, moving-boundary engineering row for one LBM
step and one MPM substep. Runtime geometry, wall velocity, real geometry, squid
proxy, link-area transfer, 48^3, 64^3, VTR output, and particle NPY output all
remain disabled. Step76 is a minimal rebaseline only and does not claim physical
validation, real squid validation, grid convergence, or production readiness.

Step 77 extends only that post-gate canonical driver rebaseline duration to
three LBM steps at the same 32^3, 1024-particle, moving-boundary engineering
configuration. Runtime geometry, wall velocity, real geometry, squid proxy,
link-area transfer, 48^3, 64^3, VTR output, and particle NPY output all remain
disabled. Step77 is still a bounded rebaseline only and does not claim physical
validation, real squid validation, grid convergence, or production readiness.

Step 78 extends only that post-gate canonical driver rebaseline duration to
five LBM steps at the same 32^3, 1024-particle, moving-boundary engineering
configuration. Runtime geometry, wall velocity, real geometry, squid proxy,
link-area transfer, 48^3, 64^3, 10-step baseline, VTR output, and particle NPY
output all remain disabled. Step78 is still a bounded rebaseline only and does
not claim physical validation, real squid validation, grid convergence, or
production readiness. After Step78, the intended next direction is
single-feature activation planning, not another pure duration baseline.

## What Exists

- Single-phase D3Q19 MRT LBM fluid wrapper
- 3D MPM solid solver
- Shared normalized cubic domain
- MPM-to-LBM projection of `solid_phi`, `solid_mass`, and `solid_vel`
- Penalty-force coupling MVP
- Moving-boundary bounce-back MVP with reaction transfer
- Unified `FSIDriver3D`
- Shared diagnostics and output files

## Current Limitations

- Single-phase fluid only
- Dense grid only
- No real squid geometry
- No two-phase flow or contact angle physics
- Moving-boundary reaction uses engineering scale
- Not strict final momentum-conserving sharp-interface FSI
- Small validation windows, not large production runs

## Status Summary

The repository is ready for documentation review, reproducibility review, and conservative next-step planning. It is not production ready and does not yet validate a real squid case.

The latest repository-structure work has moved the first runtime implementation wave, the driver-support implementation wave, and the `FSIDriver3D` implementation into canonical `src/mpm_lbm/...` modules while preserving legacy root imports as compatibility shims. This is code ownership migration, not new physics validation. Step 58 adds temporary canonical bridge surfaces for optional motion and wall-velocity imports only; their real implementations remain legacy-owned until a later migration step.

Step 59 proves the canonical driver can run the existing small `none`, `penalty`, and `moving_boundary` engineering smoke rows through `driver.run()`, and fixes grid-sized geometry-output naming. It does not activate runtime geometry or moving-wall velocity, add 48^3 or 64^3 validation, validate jet propulsion, validate real squid behavior, prove grid convergence, or claim production readiness.

Step 60 proves the canonical driver can extend the existing moving-boundary engineering path to 3 and 5 LBM steps at 16^3 while keeping outputs lightweight, runtime code unchanged, and Step 59 evidence green. It does not activate runtime geometry or wall velocity, add larger-grid rows, validate propulsion, validate real squid behavior, prove mesh convergence, or claim deployment readiness.

Step 61 proves the canonical driver can run the existing moving-boundary engineering path for one 32^3 single-step probe while keeping outputs lightweight, runtime code unchanged, and Step 60 evidence green. It does not activate runtime geometry or wall velocity, add required multi-step 32^3 rows, validate propulsion, validate real squid behavior, prove grid convergence, or claim deployment readiness.

Step 71 keeps activation closed while aligning output defaults with the Step70
output policy. VTR and particle persistence are now safe-by-default off in
`FSIDriverConfig`; existing configs can still opt in explicitly. Tau semantics
remain legacy by default and require a future baseline rerun campaign before
any standard lattice tau migration.
