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
- Step 79: runtime geometry diagnostic-only activation plan and guard
- Step 80: runtime geometry diagnostic-only canonical driver 3-step smoke
- Step 81: wall velocity single-feature activation plan and guard
- Step 82: wall velocity `solid_vel` canonical driver 3-step smoke
- Step 83: runtime geometry diagnostic-only plus wall velocity combined activation plan and guard
- Step 84: runtime geometry diagnostic-only plus wall velocity `solid_vel` combined canonical driver 3-step smoke
- Step 85: squid proxy static geometry activation plan and guard
- Step 86: squid proxy static geometry canonical driver 3-step smoke
- Step 87: runtime geometry diagnostic-only plus wall velocity `solid_vel` plus squid proxy combined activation plan and guard
- Step 88: squid proxy plus runtime geometry diagnostic-only plus wall velocity `solid_vel` combined canonical driver 3-step smoke
- Step 89: first user simulation dry run plan and guard
- Step 90: first user simulation dry run
- Step 91: first user simulation 10-step dry run plan and guard
- Step 95: Taichi GGUI 10-step first-user visualization plan and guard
- Step 96: Taichi GGUI 10-step first-user visualization run

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

Step 79 adds runtime geometry diagnostic-only activation planning and guard
evidence for exactly one future Step80 row. Step79 does not run `FSIDriver3D`,
execute a simulation, apply runtime geometry to solver state, mutate geometry,
change solver formulas, enable wall velocity, enable real geometry, enable
squid proxy behavior, enable link-area transfer, add larger grids, or write VTR
or particle NPY output. The only Step79 claim is that runtime geometry
diagnostic-only single-feature activation is planned and guarded for Step80.

Step 80 runs that single planned runtime geometry diagnostic-only canonical
driver row for three LBM steps at 32^3 with 1024 particles. The row writes
`geometry_motion_interface_report.json`, confirms diagnostic-only no-op
semantics with zero mutation flags, and keeps wall velocity, real geometry,
squid proxy behavior, link-area transfer, larger grids, VTR output, and particle
NPY output disabled. Step80 does not claim moving-geometry physics, real squid
validation, physical validation, grid convergence, or production readiness.

Step 81 adds wall velocity single-feature activation planning and guard evidence
for exactly one future Step82 row. Step81 does not run `FSIDriver3D`, execute a
simulation, activate wall velocity in runtime, enable runtime geometry, combine
runtime geometry with wall velocity, enable real geometry, enable squid proxy
behavior, enable link-area transfer, add larger grids, or write VTR or particle
NPY output. The only Step81 claim is that wall velocity `solid_vel` activation
is planned and guarded for Step82.

Step 82 executes exactly the wall-velocity-only canonical driver row planned by
Step81 for three LBM steps at 32^3 with 1024 particles. The row enables only
`wall_velocity_application_mode = solid_vel_experimental`, targets only LBM
`solid_vel`, writes `wall_velocity_application_report.json` and
`boundary_motion_interface_report.json`, and keeps runtime geometry, combined
runtime geometry plus wall velocity, real geometry, squid proxy behavior,
link-area transfer, larger grids, VTR output, and particle NPY output disabled.
The Step82 driver config uses `target_u_lbm = [0.0, 0.0, 0.0]` to isolate the
wall-velocity cap smoke from the default background flow. Step82 does not claim
moving-wall physics validation, real squid validation, grid convergence, or
production readiness.

Step 83 adds plan-and-guard evidence for one future Step84 combined row that
pairs runtime geometry diagnostic-only reporting with wall velocity
`solid_vel_experimental` reporting. Step83 does not run `FSIDriver3D`, execute a
simulation, activate the combined path, enable real geometry, enable squid proxy
behavior, enable link-area transfer, add larger grids, write VTR or particle NPY
output, change solver formulas, migrate tau semantics, or claim physical
validation or production readiness.

Step84 executes exactly the combined row planned by Step83 for three LBM steps
at 32^3 with 1024 particles. The row enables runtime geometry diagnostic-only
interface reporting and wall velocity `solid_vel_experimental` reporting in the
same canonical driver run, with boundary-motion reporting enabled and
`target_u_lbm = [0.0, 0.0, 0.0]` as a row-local config choice. Step84 keeps
geometry mutation, MPM particle displacement through runtime geometry, LBM
`solid_phi` updates through runtime geometry, direct LBM population writes
through wall velocity, moving bounce-back formula changes, direct MPM/projector
wall-velocity updates, real geometry, squid proxy behavior, link-area transfer,
larger grids, VTR output, and particle NPY output disabled. Step84 does not
claim physical validation, real squid validation, grid convergence, or
production readiness.

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

Step85 adds a plan-and-guard layer for one future Step86 static `squid_proxy`
canonical driver smoke row at 32^3 with 1024 particles and three LBM steps.
Step85 does not run `FSIDriver3D`, execute a simulation, enable runtime
geometry, enable wall velocity, combine runtime geometry with wall velocity,
enable real geometry, use link-area transfer, add larger grids, write VTR or
particle NPY output, change solver formulas, migrate tau semantics, or claim
physical validation, real squid validation, squid swimming, or production
readiness. It only records that squid-proxy static geometry is planned and
guarded for Step86.

Step86 executes exactly that planned static `squid_proxy` canonical driver row
for three LBM steps at 32^3 with 1024 particles. The row uses
`moving_boundary` engineering coupling, reads
`configs/step85_squid_proxy_geometry_1024.json`, writes a non-strict geometry
quality report, and keeps runtime geometry, wall velocity, combined runtime
geometry plus wall velocity, real geometry candidates, link-area transfer,
48^3, 64^3, VTR output, particle NPY output, solver formula changes, tau
migration, physical validation, real squid validation, squid swimming, and
production-readiness claims closed. Step86 may claim only that squid_proxy
static geometry canonical driver 3-step smoke passed.

Step87 adds plan-and-guard evidence for one future Step88 row that combines
procedural static `squid_proxy` geometry, runtime geometry diagnostic-only
reporting, and wall velocity `solid_vel_experimental` reporting. Step87 does
not run `FSIDriver3D`, execute simulation, activate the three-feature combined
row, enable real geometry candidates, use link-area transfer, add larger grids,
write VTR or particle NPY output, change solver formulas, migrate tau
semantics, or claim physical validation, real squid validation, squid swimming,
squid actuation, or production readiness.

Step88 executes exactly that three-feature canonical driver smoke row for three
LBM steps at 32^3 with 1024 particles. The row combines procedural
`squid_proxy` geometry, runtime geometry diagnostic-only reporting,
boundary-motion reporting, and wall velocity `solid_vel_experimental`
reporting, with `target_u_lbm = [0.0, 0.0, 0.0]` as a row-local config choice.
Step88 keeps real geometry candidates, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, solver formula changes, tau migration, physical
validation, real squid validation, squid swimming, squid actuation, and
production-readiness claims closed.

Step89 adds plan-and-guard evidence for exactly one future Step90 first user
simulation dry-run row. Step89 does not run `FSIDriver3D`, call `driver.run()`,
execute simulation, or activate the dry run. The planned Step90 row is
32^3/1024 particles/five LBM steps with procedural `squid_proxy` geometry,
runtime geometry diagnostic-only reporting, wall velocity
`solid_vel_experimental` reporting, and `target_u_lbm = [0.0, 0.0, 0.0]`.
Step89 keeps real geometry candidates, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, solver formula changes, tau migration, physical
validation, real squid validation, squid swimming, squid actuation, and
production-readiness claims closed.

Step90 executes exactly that planned first user simulation dry-run row for five
LBM steps at 32^3 with 1024 particles. The row combines procedural
`squid_proxy` geometry, runtime geometry diagnostic-only reporting,
boundary-motion reporting, and wall velocity `solid_vel_experimental`
reporting, with `target_u_lbm = [0.0, 0.0, 0.0]` as the row-local config
choice. Step90 keeps real geometry candidates, link-area transfer, 48^3, 64^3,
VTR output, particle NPY output, solver formula changes, tau migration,
physical validation, real squid validation, squid swimming, squid actuation,
and production-readiness claims closed.

Step91 adds plan-and-guard evidence for exactly one future Step92 ten-step
first user simulation dry-run row. Step91 does not run `FSIDriver3D`, call
`driver.run()`, execute simulation, or activate the 10-step dry run. The
planned Step92 row keeps the Step90 envelope fixed at 32^3/1024 particles,
procedural `squid_proxy` geometry, runtime geometry diagnostic-only reporting,
wall velocity `solid_vel_experimental` reporting, and
`target_u_lbm = [0.0, 0.0, 0.0]`, with only the duration expanded from five to
ten LBM steps. Step91 keeps real geometry candidates, link-area transfer,
48^3, 64^3, VTR output, particle NPY output, solver formula changes, tau
migration, physical validation, real squid validation, squid swimming, squid
actuation, and production-readiness claims closed.

Step92 executes exactly that planned first user simulation dry-run row for ten
LBM steps at 32^3 with 1024 particles. The row combines procedural
`squid_proxy` geometry, runtime geometry diagnostic-only reporting,
boundary-motion reporting, and wall velocity `solid_vel_experimental`
reporting, with `target_u_lbm = [0.0, 0.0, 0.0]` as the row-local config
choice. Step92 keeps real geometry candidates, link-area transfer, 48^3, 64^3,
file-based visualization output, particle NPY output, solver formula changes,
tau migration, physical validation, real squid validation, squid swimming,
squid actuation, and production-readiness claims closed.

Step93 corrects the previous Step93 planning direction and adds plan-and-guard
evidence for exactly one future Step94 Taichi GGUI visualization smoke row.
Step93 does not run `FSIDriver3D`, call `driver.run()`, execute simulation,
open a GGUI window, write screenshots, write file-based visualization output,
or write particle NPY output. The planned Step94 row keeps the Step92 envelope
at 32^3/1024 particles with procedural `squid_proxy` geometry, runtime geometry
diagnostic-only reporting, wall velocity `solid_vel_experimental` reporting,
and `target_u_lbm = [0.0, 0.0, 0.0]`, but reduces duration to one LBM step for
GGUI visualization-path isolation only.

Step94 executes exactly that planned Taichi GGUI visualization smoke row. The
canonical driver completes one LBM step at 32^3 with 1024 procedural
`squid_proxy` particles, runtime geometry diagnostic-only reporting, boundary
motion reporting, and wall velocity `solid_vel_experimental` reporting. The
independent GGUI evidence renderer creates a Taichi window, scene, and camera,
renders deterministic procedural squid-proxy visualization proxy points plus
domain and wall-velocity proxies, and writes exactly one PNG screenshot. Step94
keeps VTR, particle NPY, video, real geometry candidates, link-area transfer,
48^3, 64^3, solver formula changes, physical validation, real squid validation,
squid swimming, squid actuation, and production-readiness claims closed.

Step95 adds plan-and-guard evidence for exactly one future Step96 Taichi GGUI
10-step first-user visualization row. Step95 does not run `FSIDriver3D`, call
`driver.run()`, execute simulation, open a GGUI window, write screenshots, write
video, write VTR, or write particle NPY output. The planned Step96 row combines
the Step92 10-step first-user dry-run envelope with the Step94 Taichi GGUI
screenshot path. Step95 keeps real geometry candidates, link-area transfer,
48^3, 64^3, dense output, solver formula changes, physical validation, real
squid validation, squid swimming, squid actuation, and production-readiness
claims closed.

Step96 executes exactly that planned 10-step Taichi GGUI first-user
visualization row at 32^3 with 1024 procedural `squid_proxy` particles. The
canonical driver completes 10 LBM steps with runtime geometry diagnostic-only
reporting, boundary-motion reporting, and wall velocity
`solid_vel_experimental` reporting, then the GGUI evidence path writes exactly
one PNG screenshot. Step96 keeps video, VTR, particle NPY output, real geometry
candidates, link-area transfer, 48^3, 64^3, solver formula changes, physical
validation, real squid validation, squid swimming, squid actuation, and
production-readiness claims closed.

Step97 adds plan-and-guard evidence for exactly one future Step98 48^3 Taichi
GGUI visualization smoke row. Step97 does not run `FSIDriver3D`, call
`driver.run()`, execute simulation, open a GGUI window, write screenshots,
write video, write VTR, or write particle NPY output. The planned Step98 row
keeps the accepted first-user `squid_proxy` runtime-geometry and
wall-velocity envelope, changes Step96 from 32^3 to 48^3, and reduces duration
from 10 LBM steps to one LBM step for grid-expansion smoke isolation. Step97
keeps 64^3, real geometry candidates, link-area transfer, dense output, solver
formula changes, physical validation, real squid validation, squid swimming,
squid actuation, and production-readiness claims closed.
