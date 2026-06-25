# MPM-LBM FSI Prototype

A Taichi-based prototype framework for 3D MPM solid and LBM fluid coupling.

Current status: engineering prototype.

This repository is a small-scale engineering prototype for comparing MPM-LBM coupling paths. It is not production ready and should not be described as a completed sharp-interface FSI solver or a real squid simulation.

## Implemented

- 3D single-phase LBM backend based on taichi_LBM3D
- 3D MPM solid backend
- unified grid/unit/timestep scaffold
- MPM-to-LBM projection
- penalty-force two-way coupling
- moving-boundary bounce-back path
- moving-boundary reaction transfer to MPM
- unified FSIDriver3D with modes: none, penalty, moving_boundary
- shared diagnostics, CSV/NPZ outputs, logs, and small validation baselines
- larger-grid engineering baselines through 48^3 and 64^3 feasibility checks
- moving-boundary reaction calibration diagnostics and recommended moving_boundary configs
- Step 16 long-run validation for calibrated 48^3 moving_boundary cases and a conservative 64^3 moving_boundary feasibility row
- Step 17 diagnostic-only direction-wise and link-area proxy accounting for moving-boundary bounce-back
- Step 18 opt-in experimental link-area reaction transfer mode for moving_boundary comparison
- Step 19 long-window and 64^3 feasibility validation for the opt-in experimental link-area transfer
- Step 20 small synthetic mesh and voxel geometry import pipeline for 32^3 imported-geometry smoke validation
- Step 21 synthetic imported geometry scale validation for 48^3 imported-geometry mode rows and 64^3 feasibility rows
- Step 22 diagnostic mesh/voxel geometry quality checks and import robustness baselines
- Step 23 quality-gated synthetic imported geometry scale validation with quality reports for every driver row
- Step 24 strict quality-gated synthetic imported geometry long-run validation for selected moving_boundary rows
- Step 25 controlled real geometry candidate intake with manifest, fingerprinting, normalization reports, deterministic sampling reproducibility, and projection-only smoke diagnostics
- Step 26 controlled real geometry projection-only and short driver feasibility with strict quality reports for every very short driver row
- Step 27 controlled real geometry 64^3 short driver feasibility for a six-row coupling subset with strict quality reports
- Step 28 controlled real geometry 64^3 transfer diagnostics comparing engineering and link_area_experimental moving_boundary transfer rows
- Step 29 controlled real geometry 64^3 short-window stability envelope for the Step 28 transfer matrix
- Step 30 controlled squid proxy region geometry contract for static squid-like region semantics
- Step 31 controlled squid proxy region projection and static driver smoke for existing coupling modes only
- Step 32 controlled squid proxy prescribed kinematics schedule contract for artifact-only mantle, cavity, and funnel proxy schedules
- Step 33 controlled squid proxy kinematics mapping to boundary-motion diagnostics for artifact-only displacement and velocity proxies
- Step 34 controlled squid proxy boundary-motion driver interface with default static behavior preserved
- Step 35 controlled squid proxy moving-wall velocity field diagnostics
- Step 36 controlled moving-wall bounce-back velocity application smoke for opt-in `solid_vel` application only
- Step 37 controlled moving-wall application short-window envelope
- Step 38 controlled tethered jet-cycle proxy diagnostics prototype
- Step 39 controlled jet-cycle proxy multi-cycle stability envelope
- Step 40 controlled jet-cycle proxy parameter sensitivity smoke over wall-velocity scale values
- Step 41 controlled jet-cycle proxy selected-parameter 64^3 feasibility for `wall_velocity_scale = 0.05`
- Step 42 controlled squid proxy prescribed geometry displacement diagnostics
- Step 43 controlled squid proxy geometry motion driver interface contract
- Step 44 controlled squid proxy diagnostic geometry update smoke
- Step 45 controlled runtime geometry projection integration smoke
- Step 46 controlled runtime geometry plus wall velocity one-step coupling smoke
- Step 47 controlled runtime geometry plus wall velocity short-step coupling envelope
- Step 48 controlled runtime geometry plus wall velocity 10-step coupling envelope
- Step 49 controlled runtime geometry plus wall velocity 20-step coupling envelope
- Step 50 controlled runtime geometry plus wall velocity one-cycle diagnostic envelope
- Step 51 controlled runtime geometry wall velocity transfer comparison diagnostics
- Step 52 controlled 48^3 engineering one-cycle feasibility diagnostics
- Step 53 controlled support-scaling active-cell semantics post-processing audit
- Step 54 repository evidence integrity repair
- Step 55 repository code layout separation and import-boundary contract
- Step 56 canonical runtime implementation migration wave 1
- Step 57 canonical driver support migration wave 2
- Step 58 canonical FSIDriver implementation migration wave 3
- Step 59 canonical FSIDriver real smoke simulation
- Step 60 controlled canonical moving-boundary duration ramp
- Step 61 controlled canonical 32^3 moving-boundary single-step probe
- Step 62 controlled canonical 32^3 moving-boundary 3-step duration probe
- Step 68 step-specific proxy migration from root `src/` to `experiments/steps/`
- Step 69 root `src/` final implementation cleanup for remaining support rows, compatibility shims, current inventory, and export-surface refresh
- Step 70 API and config freeze before activation, with public API, compatibility, schema, activation, artifact, and report-consistency guards
- Step 71 output default safety alignment and LBM tau convention decision, with safe-by-default FSIDriver file outputs and legacy tau semantics preserved
- Step 72 runtime geometry activation readiness audit, with API, schema, driver-gate, state-guard, output-policy, no-simulation, and Step71 regression guards while activation remains closed
- Step 73 wall velocity activation readiness audit, with API, schema, driver-gate, application-safety, output-policy, full activation-gate coverage, no-simulation, and Step72 regression guards while activation remains closed
- Step 74 real geometry data boundary audit, with API, descriptor schema, manifest policy, quarantine, output-policy, full activation-gate coverage, no-simulation, and Step73 regression guards while activation remains closed
- Step 75 solver-complete simulation campaign readiness gate, with Step71-Step74 evidence aggregation, activation-gate closure, inactive Step76 minimal rebaseline planning, no-simulation, output-policy, and Step74 regression guards while advanced activation remains closed
- Step 76 minimal post-gate canonical driver rebaseline, with one 32^3 moving-boundary engineering one-step `FSIDriver3D.run()` row, activation guards, output guards, and Step75 regression guards while advanced activation remains closed
- Step 77 minimal post-gate canonical driver 3-step rebaseline, with one 32^3 moving-boundary engineering three-step `FSIDriver3D.run()` row, activation guards, output guards, and Step76 regression guards while advanced activation remains closed
- Step 78 minimal post-gate canonical driver 5-step rebaseline, with one 32^3 moving-boundary engineering five-step `FSIDriver3D.run()` row, activation guards, output guards, and Step77 regression guards while advanced activation remains closed
- Step 79 runtime geometry diagnostic-only activation plan and guard, with Step80 single-feature smoke planning, Step78 regression guards, output guards, and artifact guards while no simulation is run and advanced activation remains closed
- Step 80 runtime geometry diagnostic-only canonical driver 3-step smoke, with one 32^3 moving-boundary engineering box row, geometry-motion interface reporting, zero mutation flags, output guards, and Step79 regression guards
- Step 81 wall velocity single-feature activation plan and guard, with Step82 wall-velocity-only smoke planning, Step80 regression guards, output guards, and artifact guards while no simulation is run
- Step 82 wall velocity `solid_vel` canonical driver 3-step smoke, with one 32^3 moving-boundary engineering box row, `solid_vel_experimental` application reporting, boundary-motion no-op reporting, output guards, and Step81 regression guards
- Step 83 runtime geometry diagnostic-only plus wall velocity combined activation plan and guard, with exactly one future Step84 combined smoke row planned, Step80/Step82 regression guards, output guards, and artifact guards while no simulation is run
- Step 84 runtime geometry diagnostic-only plus wall velocity `solid_vel` combined canonical driver 3-step smoke, with exactly one 32^3 moving-boundary engineering box row, geometry-motion diagnostic-only reporting, wall-velocity `solid_vel` reporting, boundary-motion reporting, output guards, and Step80/Step82/Step83 regression guards
- Step 85 squid proxy static geometry activation plan and guard, with exactly one future Step86 static `squid_proxy` 32^3 three-step smoke row planned, Step84 regression guard, Step31 reference guard, output guard, and artifact guard while no simulation is run
- Step 86 squid proxy static geometry canonical driver 3-step smoke, with exactly one 32^3/1024-particle moving-boundary engineering `squid_proxy` row, non-strict geometry quality report, Step85/Step84/Step31 guards, output guards, and artifact guard while runtime geometry, wall velocity, real geometry candidates, link-area transfer, larger grids, VTR, particle NPY, solver formula changes, tau migration, and physical-production claims remain closed
- Step 87 runtime geometry diagnostic-only plus wall velocity `solid_vel` plus squid proxy combined activation plan and guard, with exactly one future Step88 three-feature 32^3 smoke row planned, Step86/Step84/Step82/Step80 regression guards, output guard, and artifact guard while no simulation is run
- Step 88 squid proxy plus runtime geometry diagnostic-only plus wall velocity `solid_vel` combined canonical driver 3-step smoke, with exactly one 32^3/1024-particle row, non-strict squid proxy geometry quality reporting, diagnostic-only runtime geometry reporting, `solid_vel_experimental` wall-velocity reporting, Step87/Step86/Step84/Step82/Step80 guards, output guard, and artifact guard while real geometry candidates, link-area transfer, larger grids, VTR, particle NPY, solver formula changes, and physical-production claims remain closed
- Step 89 first user simulation dry run plan and guard, with exactly one future Step90 32^3/1024-particle/5-step dry-run row planned, Step88/Step87/Step86 regression guards, output guard, and artifact guard while no simulation is run and real geometry candidates, link-area transfer, larger grids, VTR, particle NPY, solver formula changes, and physical-production claims remain closed
- Step 90 first user simulation dry run, with exactly one 32^3/1024-particle/5-step `squid_proxy` row using runtime geometry diagnostic-only reporting and `solid_vel_experimental` wall-velocity reporting, Step89/Step88/Step87 regression guards, output guard, and artifact guard while real geometry candidates, link-area transfer, larger grids, VTR, particle NPY, solver formula changes, and physical-production claims remain closed
- Step 91 first user simulation 10-step dry run plan and guard, with exactly one future Step92 32^3/1024-particle/10-step dry-run row planned, Step90/Step89/Step88 regression guards, output guard, and artifact guard while no simulation is run and real geometry candidates, link-area transfer, larger grids, VTR, particle NPY, solver formula changes, and physical-production claims remain closed
- Step 92 first user simulation 10-step dry run, with exactly one 32^3/1024-particle/10-step `squid_proxy` row using runtime geometry diagnostic-only reporting and `solid_vel_experimental` wall-velocity reporting, Step91/Step90/Step89 regression guards, output guard, and artifact guard while real geometry candidates, link-area transfer, larger grids, file-based visualization output, particle NPY, solver formula changes, and physical-production claims remain closed
- Step 93 Taichi GGUI visualization enablement plan and guard, with exactly one future Step94 32^3/1024-particle/1-step GGUI visual smoke row planned, Step92/Step91/Step90 regression guards, output guard, and artifact guard while no simulation, GGUI window, screenshot, file-based visualization output, particle NPY, solver formula changes, or physical-production claims are introduced
- Step 94 Taichi GGUI visualization smoke, with exactly one 32^3/1024-particle/1-step `squid_proxy` first-user envelope row run through the canonical driver and rendered to one Taichi GGUI PNG screenshot, Step93/Step92/Step90 regression guards, output guard, and artifact guard while VTR, particle NPY, video, real geometry candidates, link-area transfer, larger grids, solver formula changes, and physical-production claims remain closed
- Step 95 Taichi GGUI 10-step first-user visualization plan and guard, with exactly one future Step96 32^3/1024-particle/10-step GGUI visual row planned, Step94/Step93/Step92 regression guards, output guard, and artifact guard while no simulation, GGUI window, screenshot, video, VTR, particle NPY, solver formula changes, or physical-production claims are introduced
- Step 96 Taichi GGUI 10-step first-user visualization run, with exactly one 32^3/1024-particle/10-step `squid_proxy` first-user envelope row run through the canonical driver and rendered to one Taichi GGUI PNG screenshot, Step95/Step94/Step92 regression guards, output guard, and artifact guard while video, VTR, particle NPY, real geometry candidates, link-area transfer, larger grids, solver formula changes, and physical-production claims remain closed
- Step 97 48^3 Taichi GGUI visualization expansion plan and guard, with exactly one future Step98 48^3/1024-particle/1-step GGUI visual smoke row planned, Step96/Step94/Step92 regression guards, output guard, and artifact guard while no simulation, GGUI window, screenshot, video, VTR, particle NPY, real geometry candidates, link-area transfer, 64^3, solver formula changes, or physical-production claims are introduced
- Step 98 48^3 Taichi GGUI visualization smoke, with exactly one 48^3/1024-particle/1-step `squid_proxy` first-user envelope row run through the canonical driver and rendered to one Taichi GGUI PNG screenshot, Step97/Step96/Step94 regression guards, output guard, and artifact guard while video, VTR, particle NPY, real geometry candidates, link-area transfer, 64^3, solver formula changes, and physical-production claims remain closed
- Step 99 48^3 5-step Taichi GGUI visualization plan and guard, with exactly one future Step100 48^3/1024-particle/5-step GGUI visual run planned, Step98/Step97/Step96 regression guards, output guard, and artifact guard while no simulation, GGUI window, screenshot, video, VTR, particle NPY, real geometry candidates, link-area transfer, 64^3, solver formula changes, or physical-production claims are introduced
- Step 100 48^3 5-step Taichi GGUI visualization run, with exactly one 48^3/1024-particle/5-step `squid_proxy` first-user envelope row run through the canonical driver and rendered to one Taichi GGUI PNG screenshot, Step99/Step98/Step96 regression guards, output guard, and artifact guard while video, VTR, particle NPY, real geometry candidates, link-area transfer, 64^3, solver formula changes, 48^3 10-step readiness, and physical-production claims remain closed
- Step 101 48^3 10-step Taichi GGUI visualization plan and guard, with exactly one future Step102 48^3/1024-particle/10-step GGUI visual run planned, Step100/Step99/Step98 regression guards, output guard, and artifact guard while no simulation, GGUI window, screenshot, video, VTR, particle NPY, real geometry candidates, link-area transfer, 64^3, solver formula changes, or physical-production claims are introduced
- Step 102 Fluent official two-way FSI benchmark intake and guard, with the Step101-planned 48^3/10-step GGUI run left unexecuted, Fluent official duct/flap source metadata recorded, private Ansys data boundaries guarded, mapping limits documented, Step101/Step100 regression guards preserved, and no Fluent run, mesh import, solver runtime change, benchmark comparison, official file commit, or validation claim introduced
- Step 103 Fluent-inspired duct-flap proxy solver comparison smoke, with one 48^3/1024-particle/5-step procedural duct-flap proxy row, GGUI screenshot output, committed solver gap reporting, private Fluent CSV boundaries, Step102/Step100 regression guards, output guards, and artifact guards while Fluent validation, solver equivalence, physical validation, real FSI validation, and production-readiness claims remain closed
- Step 104 Fluent duct-flap official problem setup repair, with explicit x-min velocity inlet and x-max pressure outlet setup, non-all-fluid duct static geometry, fixed-base MPM mask and constraint, silicone material mapping into MPM config, Step36 squid wall-velocity disconnect, proxy flap-tip displacement time series, output/artifact guards, and gap-only evidence while Fluent validation, solver equivalence, full public tutorial transient completion, exact Fluent structural model reproduction, and production-readiness claims remain closed
- Step 105 Fluent duct-flap proxy 50-step transient dimensional-gap audit, with one 48^3/1024-particle/50-step repaired-setup proxy smoke, dimensional inlet-velocity mapping report, inlet/mid/outlet flow-development diagnostics, expanded eight-gap taxonomy, output/artifact guards, and gap-only evidence while Fluent validation, solver equivalence, official steady preflow, exact monitor equivalence, solver-formula changes, and production-readiness claims remain closed
- Step 106 Fluent duct-flap proxy outlet boundary flow propagation repair, with a red-to-green x-right pressure outlet interior-neighbor velocity extrapolation fix, one 48^3 duct-only LBM outlet propagation runner, one 48^3/1024-particle/20-step FSI regression smoke, boundary semantics reporting, output/artifact guards, and gap-only evidence while Fluent validation, solver equivalence, official steady preflow, exact monitor equivalence, broader solver-formula changes, and production-readiness claims remain closed
- Step 107 Fluent public result digitization error harness, with a derived approximate Figure 29.4 displacement reference CSV, public-source metadata, pure-Python displacement error metrics against the Step106 free-tip proxy output, output/artifact guards, and comparison-only evidence while official case/image payloads, Fluent validation, direct solver equivalence, exact monitor equivalence, solver changes, and production-readiness claims remain closed
- Step 108 Fluent official-speed low-Mach subcycling smoke, with opt-in driver fields mapping the public 10 m/s inlet to `u_lbm = 0.02`, 120 LBM substeps per 0.0005 s official FSI step, 50-step duct-only and FSI proxy artifacts covering 0.025 s, Step107-style error comparison, output/artifact guards, and no Fluent validation, solver equivalence, official mesh/case, official steady preflow, exact monitor equivalence, or production-readiness claims
- Step 109 Fluent duct-flap FSI response-amplitude sensitivity matrix, with nine Step108-compatible cap/scale/material rows, four monitor variants for the final selected row, force-cap and structural diagnostics, output/artifact guards, and comparison-only evidence while Fluent validation, official monitor equivalence, official mesh/case, official dynamic-mesh reproduction, and production-readiness claims remain closed
- Step 110 Fluent public-plot error-minimized proxy candidate, with proxy preflow restart artifacts, guarded LBM restart loading, public structural-point proxy monitor alignment, composite error-scored candidate rows, curve-shape diagnostics, output/artifact guards, and comparison-only evidence while official Fluent validation and exact monitor/preflow reproduction claims remain closed
- Step 111 Fluent public-plot real solver candidate materialization, with a real 6000-substep LBM preflow restart, a real FSIDriver3D run for the Step110-selected `cap_2e-2_E_2e4` candidate over the public tutorial time window, real particle-monitor extraction, Step107 public-plot error comparison, output/artifact guards, and comparison-only evidence while official Fluent validation, exact monitor/preflow reproduction, official mesh/case/data, and production-readiness claims remain closed

## Not Implemented

- two-phase flow
- contact angle physics
- sparse storage
- real squid geometry
- real squid validation
- production mesh repair
- final strict momentum-conserving sharp-interface FSI
- production-grade solver readiness

## Step 30 Squid Proxy Region Boundary

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

Step 30 adds stable proxy region IDs for `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy`, `head_proxy`, `arms_proxy`, `left_fin_proxy`, and `right_fin_proxy`. The cavity and outlet regions are static geometry semantics only.

## Step 31 Squid Proxy Static Driver Boundary

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

Step 31 adds 32^3/48^3/64^3 projection-only region diagnostics, four 48^3 static driver smoke rows, region-driver alignment, engineering vs link_area_experimental static comparison, strict quality report aggregation, and a Step 30 regression guard.

## Step 32 Squid Proxy Kinematics Schedule Boundary

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

Step 32 adds deterministic phase samples, mantle radius scale, mantle cavity volume proxy scale, funnel aperture proxy scale, derivative diagnostics, repeatability hashes, region mapping validation, a Step 31 regression guard, and artifact budget checks. These are schedule artifacts only.

## Step 33 Squid Proxy Kinematics Mapping Boundary

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

Step 33 maps the accepted Step 32 schedule to region-level proxy diagnostics for `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`, then summarizes coverage at 32^3, 48^3, and 64^3. These diagnostics are not written into a coupled simulation state.

## Step 42 Squid Proxy Prescribed Geometry Displacement Boundary

Step 42 is controlled squid proxy prescribed geometry displacement diagnostics.
Step 42 derives displacement diagnostics only.
Step 42 does not update driver geometry.
Step 42 does not displace MPM particles in FSIDriver3D.
Step 42 does not update LBM solid_phi.
Step 42 does not update dynamic_solid.
Step 42 does not change moving bounce-back formulas.
Step 42 remains diagnostic-only.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 42 generates per-phase prescribed displacement diagnostics for `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`, then checks repeatability, schedule consistency, Step 33 motion consistency, grid coverage, cycle closure, no-driver-update guards, Step 41 regression, and artifact budget. These diagnostics are not written into a coupled simulation state.

## Step 43 Squid Proxy Geometry Motion Driver Interface Boundary

Step 43 is controlled squid proxy geometry motion driver interface.
Step 43 defines a guarded driver interface only.
Step 43 keeps geometry motion diagnostic-only.
Step 43 does not update driver geometry.
Step 43 does not displace MPM particles.
Step 43 does not update LBM solid_phi.
Step 43 does not update dynamic_solid.
Step 43 does not recompute boundary links from displaced geometry.
Step 43 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 43 adds driver config fields and a report-only initialization hook that can read the accepted Step 42 displacement artifact and write a geometry-motion interface report. The diagnostic-only path is validated against static 48^3 rows and is not written into a coupled simulation state.

## Step 44 Squid Proxy Diagnostic Geometry Update Boundary

Step 44 is controlled squid proxy diagnostic geometry update smoke.
Step 44 uses a runtime diagnostic geometry copy only.
Step 44 does not persist displaced geometry.
Step 44 does not write displaced particles.
Step 44 does not update driver geometry state.
Step 44 does not update LBM solid_phi.
Step 44 does not update dynamic_solid.
Step 44 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.

Step 44 summarizes phase-selected runtime displaced-copy diagnostics from the accepted Step 42 displacement artifact, runs projection-only smoke at 32^3 and 48^3, records a conservative optional one-step diagnostic descriptor, and proves that original geometry, region masks, solver formulas, and persistent driver state remain unchanged.

## Step 45 Runtime Geometry Projection Integration Boundary

Step 45 is controlled runtime geometry projection integration smoke.
Step 45 uses transient projection state only.
Step 45 does not persist projected state.
Step 45 does not persist displaced geometry.
Step 45 does not write displaced particles.
Step 45 does not update default driver geometry.
Step 45 does not persist LBM solid_phi updates.
Step 45 does not update dynamic_solid.
Step 45 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.

Step 45 integrates the accepted Step 44 runtime displaced copy into an isolated transient projection target for `32^3` and `48^3` diagnostics across the selected phases `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`. It records original-vs-runtime comparison, projection phase closure, Step 44 projection alignment, ultra-short smoke descriptors, state guards, and artifact-budget checks without changing default solver behavior.

## Step 46 Runtime Geometry Wall Velocity Coupling Smoke Boundary

Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.
Step 46 is opt-in and ultra-short.
Step 46 combines transient runtime geometry projection with solid_vel wall velocity application.
Step 46 does not persist displaced geometry.
Step 46 does not persist projected state.
Step 46 does not run a full-cycle moving-geometry simulation.
Step 46 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 46 records a four-row `32^3`, phase-`0.35`, one-step matrix: original static, runtime-geometry only, wall-velocity only, and runtime-geometry plus wall-velocity. It reuses the accepted Step 45 transient projection path and the accepted opt-in wall-velocity path, records quality/comparison/mass-force-bounceback diagnostics, and proves through state guards and artifact checks that no persistent geometry, default solver state, dense-field, particle, VTR, `geo_all_fluid_*.dat`, or formula update is introduced.

## Step 47 Runtime Geometry Wall Velocity Short-Step Coupling Envelope Boundary

Step 47 is controlled runtime geometry plus wall velocity short-step coupling envelope.
Step 47 is opt-in and engineering-only.
Step 47 runs a 32^3 five-step envelope.
Step 47 does not run a full-cycle moving-geometry simulation.
Step 47 does not persist displaced geometry.
Step 47 does not persist projected state.
Step 47 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 47 records a four-row `32^3`, five-step, engineering-only envelope over phases `0.0`, `0.05`, `0.1`, `0.2`, and `0.35`: original static, runtime-geometry only, wall-velocity only, and runtime-geometry plus wall-velocity. It records envelope quality, component-effect, phase-progression, mass-force-bounceback, state-guard, Step 46 regression, and artifact-budget diagnostics without changing default solver behavior.

## Step 25 Intake Boundary

Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Step 25 does not implement squid swimming.
Step 25 does not implement squid actuation.
Step 25 does not implement new FSI physics.
Step 25 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Candidate intake does not perform production mesh repair or automatic remeshing.
Raw large real geometry files and scan data are not committed.

## Step 26 Short Feasibility Boundary

Step 26 is controlled real geometry projection-only and short driver feasibility.
Step 26 is not real squid validation.
Step 26 does not implement squid actuation.
Step 26 does not implement squid swimming.
Step 26 does not implement new FSI physics.
Step 26 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 26 reuses the accepted Step 25 candidates, checks their fingerprints, creates driver-ready geometry configs, runs projection-only diagnostics at 32^3/48^3/64^3, and runs 48^3 very short driver rows for existing modes only.

## Step 27 64 Short Driver Boundary

Step 27 is controlled real geometry 64^3 short driver feasibility.
Step 27 is not real squid validation.
Step 27 does not implement squid actuation.
Step 27 does not implement squid swimming.
Step 27 does not implement new FSI physics.
Step 27 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 27 reuses the accepted Step 25 candidates and Step 26 strict driver-ready geometry configs, then runs only six 64^3 short coupling rows: penalty engineering, moving_boundary engineering, and moving_boundary link_area_experimental for both mesh and voxel candidates.

## Step 28 Transfer Diagnostics Boundary

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

Step 28 reuses the accepted Step 25 candidates and Step 26 strict driver-ready geometry configs, then runs four 64^3 moving_boundary rows: engineering and link_area_experimental transfer for both mesh and voxel candidates.

## Step 29 Stability Envelope Boundary

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

Step 29 reuses the accepted Step 28 transfer matrix, then runs four 64^3 moving_boundary 20-step rows to summarize stability, force/reaction, transfer, area-scale, and Step 28 prefix envelopes.

## Quick Start

Use the known Windows Python environment for this workspace:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Run the main Step 10 driver baselines:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
```

The committed Step 10 artifacts are the current reproducibility baseline. Step 11 adds documentation and does not require rerunning heavy simulations when those artifacts are present and tests pass.

## Core Modes

| mode | LBM path | MPM reaction | cell_force | dynamic solid |
| ---- | -------- | ------------ | ---------- | ------------- |
| none | `lbm.step()` | none | zero | no |
| penalty | `lbm.step()` | `PenaltyFSICoupler3D` | nonzero | no |
| moving_boundary | `lbm.step_moving_bounceback()` | `MovingBoundaryFSICoupler3D` by default | zero | yes |

## Repository Layout

```text
src/
  lbm_fluid.py
  mpm_solid.py
  projection.py
  coupling.py
  moving_boundary_coupling.py
  fsi_config.py
  fsi_driver.py
  diagnostics.py

baseline_tests/
configs/
docs/
logs/
outputs/
paper/
tests/
```

## Reproducibility

All step reports and baseline logs are committed for reproducibility. The main validated driver entry points are the Step 10 baselines and the `FSIDriver3D` mode matrix.

Current validation includes small 32^3 regression cases, 48^3 engineering scale baseline cases, and 64^3 short feasibility checks. These runs are useful regression and comparison baselines, not final accuracy validation and not production benchmark data.

## Performance and Artifact Policy

See:

- docs/10_performance_memory.md
- docs/11_artifact_policy.md

## Geometry Support

Step 13 adds procedural geometry initialization:

- box
- ellipsoid
- squid_proxy

The squid_proxy is procedural and is not real squid validation.

Step 20 adds a small synthetic mesh and voxel geometry import pipeline.
Step 20 is a geometry-ingestion scaffold, not real squid validation.
Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D.
The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair.

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.
Step 21 is synthetic imported geometry scale validation, not real squid validation.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 21 mesh path is not production mesh repair.

Step 24 runs strict quality-gated synthetic imported geometry long-run validation.
Step 24 uses quality_check_enabled=true and quality_check_strict=true for selected imported geometry rows.
Step 24 is not real squid validation.
Step 24 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 24 mesh path is not production mesh repair or automatic remeshing.

Supported geometry types are now:

- box
- ellipsoid
- squid_proxy
- voxel
- mesh

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Run the Step 20 imported geometry baselines:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
```

## Larger-Grid Validation

Step 14 adds 48^3 scale validation and 64^3 feasibility checks. These are engineering scale baselines, not production benchmark data or real squid validation. Step 14 does not add new FSI physics.

## Moving-Boundary Calibration

Step 15 adds `MomentumAccounting3D`, calibration helpers, reaction_scale and force_cap_norm sweeps, and recommended moving_boundary configs for 48^3 box and 48^3 procedural squid_proxy cases. Step 15 does not change the moving bounce-back formula and does not claim strict final momentum conservation.

## Long-Run Validation

Step 16 does not add new FSI physics. It uses the Step 15 calibrated moving_boundary settings for longer 48^3 box and procedural squid_proxy runs, then adds a conservative 64^3 moving_boundary feasibility row and a 64^3 none/penalty/moving_boundary mode comparison.

The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation. Strict link-area momentum-conserving coupling remains future work.

## Link-Area Momentum Accounting

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged.

The Step 17 area policies are `uniform`, `inverse_length`, and `length`. These are diagnostic proxy policies, not final surface-area reconstruction. Strict link-area momentum-conserving coupling remains future work. squid_proxy is procedural and not real squid validation.

## Experimental Link-Area Transfer

Step 18 adds an opt-in experimental link-area reaction transfer mode. The default moving_boundary reaction transfer remains engineering. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged.

The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting. Enable it only with `coupling_mode = "moving_boundary"` and `reaction_transfer_mode = "link_area_experimental"`. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## Link-Area Long-Run Validation

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged.

The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## Geometry Import Pipeline

Step 20 adds small synthetic voxel and OBJ fixtures, minimal import utilities, deterministic imported-geometry particle sampling, LBM projection diagnostics, and 32^3 driver smoke baselines for none, penalty, and moving_boundary modes. It prepares the repository for future real geometry ingestion without changing FSI physics.

Step 21 carries those small synthetic imported voxel and mesh fixtures to 48^3 mode validation and 64^3 feasibility without changing coupling formulas. See docs/20_imported_geometry_scale_validation.md.

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
See docs/21_geometry_quality_checks.md.

Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.
The default quality_check_enabled remains false.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.
See docs/22_quality_gated_imported_geometry_validation.md.

## Boundary-Motion Driver Interface

Step 34 is controlled squid proxy boundary-motion driver interface.
Step 34 defines a guarded driver interface only.
Step 34 keeps prescribed kinematics diagnostic-only.
Step 34 does not apply moving wall velocity to LBM.
Step 34 does not implement a jet model.
Step 34 does not implement squid swimming.
Step 34 does not implement new FSI physics.
The default boundary_motion_mode remains static.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
See docs/34_controlled_squid_proxy_boundary_motion_driver_interface.md.

## Moving-Wall And Jet-Cycle Proxy Diagnostics

Step 35 is controlled squid proxy moving-wall velocity field diagnostics.
Step 35 builds diagnostic wall-velocity field artifacts from the accepted squid proxy kinematics only.
Step 35 does not apply moving wall velocity to LBM populations.
Step 35 does not implement a jet model.
Step 35 does not implement squid swimming.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 36 is controlled moving-wall bounce-back velocity application smoke.
Step 36 adds an opt-in `solid_vel_experimental` path that applies a capped diagnostic velocity to `lbm.solid_vel` only.
Step 36 does not modify moving bounce-back formulas.
Step 36 does not update LBM populations directly.
Step 36 does not apply wall velocity to MPM or projection.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 37 is controlled moving-wall application short-window envelope.
Step 37 runs 48^3 short-window static and experimental moving-boundary rows to confirm the opt-in application path stays bounded.
Step 37 does not change default behavior, coupling formulas, LBM formulas, MPM formulas, or projection formulas.

Step 38 is controlled tethered jet-cycle proxy diagnostics prototype.
Step 38 checks one-cycle schedule, cavity, funnel, wall-velocity, force, and bounce-back proxy diagnostics in tethered mode.
Step 38 does not implement free-body motion.
Step 38 does not implement squid swimming.
Step 38 does not validate a real jet.

Step 39 is controlled jet-cycle proxy multi-cycle stability envelope.
Step 39 repeats tethered proxy diagnostics over two cycles using the accepted moving-wall path.
Step 39 keeps free-body motion disabled and does not change moving bounce-back formulas.

Step 40 is controlled jet-cycle proxy parameter sensitivity smoke.
Step 40 varies wall velocity scale only over `0.025`, `0.05`, and `0.075`, with `wall_velocity_cap_lbm = 0.01`.
Step 40 remains tethered and proxy-only.
Step 40 does not validate a real jet.
Step 40 does not validate jet propulsion.
Step 40 does not implement free-body motion.
Step 40 does not implement squid swimming.
Step 40 does not implement real squid validation.
Step 40 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
See docs/40_controlled_jet_cycle_proxy_parameter_sensitivity_smoke.md.

Step 41 is controlled jet-cycle proxy selected-parameter 64^3 feasibility.
Step 41 selects one accepted wall velocity scale from Step 40.
Step 41 remains tethered and proxy-only.
Step 41 does not validate a real jet.
Step 41 does not validate jet propulsion.
Step 41 does not implement free-body motion.
Step 41 does not implement squid swimming.
Step 41 does not implement real squid validation.
Step 41 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
Step 41 runs four `64^3` one-cycle rows with `wall_velocity_scale = 0.05`, `wall_velocity_cap_lbm = 0.01`, and `dynamic_solid_threshold = 0.75` in the Step 41 configs only.
See docs/41_controlled_jet_cycle_proxy_selected_parameter_64_feasibility.md.

## Runtime Geometry And Wall-Velocity Envelopes

Step 42 is controlled squid proxy prescribed geometry displacement diagnostics.
Step 42 generates prescribed displacement artifacts only and does not update driver, LBM, MPM, or projection state.

Step 43 is controlled squid proxy geometry motion driver interface contract.
Step 43 adds guarded interface fields while preserving default static geometry behavior.

Step 44 is controlled squid proxy diagnostic geometry update smoke.
Step 44 evaluates transient displaced-copy geometry diagnostics only.

Step 45 is controlled runtime geometry projection integration smoke.
Step 45 projects transient displaced-copy geometry into diagnostic projection artifacts without persistent projected state.

Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.
Step 46 combines runtime geometry projection and wall velocity application for one bounded diagnostic step.

Step 47 is controlled runtime geometry plus wall velocity short-step coupling envelope.
Step 47 runs a `32^3` five-step engineering-only envelope with runtime projection and wall velocity rows.

Step 48 is controlled runtime geometry plus wall velocity 10-step coupling envelope.
Step 48 is opt-in and engineering-only.
Step 48 runs a 32^3 ten-step envelope.
Step 48 does not run a full-cycle moving-geometry simulation.
Step 48 does not persist displaced geometry.
Step 48 does not persist projected state.
Step 48 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
See docs/48_controlled_runtime_geometry_wall_velocity_10step_coupling_envelope.md.

Step 49 is controlled runtime geometry plus wall velocity 20-step coupling envelope.
Step 49 is opt-in and engineering-only.
Step 49 runs a 32^3 twenty-step envelope.
Step 49 does not run a full-cycle moving-geometry simulation.
Step 49 does not persist displaced geometry.
Step 49 does not persist projected state.
Step 49 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
See docs/49_controlled_runtime_geometry_wall_velocity_20step_coupling_envelope.md.

Step 50 is controlled runtime geometry plus wall velocity one-cycle coupling diagnostic envelope.
Step 50 is opt-in and engineering-only.
Step 50 runs a 32^3 one-cycle diagnostic envelope.
Step 50 remains non-persistent.
Step 50 does not implement a production moving-geometry solver.
Step 50 does not validate real jet propulsion.
Step 50 does not implement squid swimming.
Step 50 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
See docs/50_controlled_runtime_geometry_wall_velocity_one_cycle_coupling_diagnostic_envelope.md.

## Step 51 Runtime Geometry Wall Velocity Transfer Comparison Boundary

Step 51 is controlled runtime geometry wall velocity transfer comparison diagnostics.
Step 51 compares engineering and opt-in link-area transfer proxy rows at 32^3 only.
Step 51 remains diagnostic-only and non-persistent.
Step 51 does not validate real jet propulsion.
Step 51 does not implement squid swimming.
Step 51 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
See docs/51_controlled_runtime_geometry_wall_velocity_transfer_comparison.md.

## Step 52 Controlled 48 Engineering One-Cycle Feasibility Boundary

Step 52 is controlled 48^3 engineering one-cycle feasibility diagnostics.
Step 52 runs static and runtime-geometry-plus-wall-velocity engineering proxy rows only.
Step 52 remains diagnostic-only and non-persistent.
Step 52 does not validate real jet propulsion.
Step 52 does not implement squid swimming.
Step 52 does not change moving bounce-back formulas.
Step 52 is not grid convergence validation.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
See docs/52_controlled_48_engineering_one_cycle_feasibility.md.

## Step 53 Support Scaling Active Cell Semantics Boundary

Step 53 is a controlled post-processing audit over accepted Step 51 and Step 52 artifacts.
Step 53 reads committed JSON artifacts only and adds no new solver rows.
Step 53 keeps runtime behavior diagnostic-only and non-persistent.
Step 53 does not validate real jets.
Step 53 does not validate jet propulsion.
Step 53 does not implement squid swimming.
Step 53 does not change moving bounce-back formulas.
Step 53 is not a grid-convergence result.
See docs/53_controlled_48_support_scaling_active_cell_semantics.md.

## Step 54 Repository Evidence Integrity Repair Boundary

Step 54 is a repository evidence integrity repair.
Step 54 pauses feature expansion and repairs evidence labels, test-strength classification, claim guards, and LBM relaxation semantics naming.
Step 54 keeps solver behavior unchanged.
Step 54 does not add a 48^3 link-area run.
Step 54 does not lengthen the cycle window.
Step 54 does not add a 64^3 case.
Step 54 does not validate real jet behavior.
Step 54 does not validate jet propulsion.
Step 54 does not implement squid swimming.
Step 54 does not prove grid convergence.
Step 54 does not claim production readiness.
See docs/54_repository_evidence_integrity_repair.md.

## Step 55 Repository Code Layout Separation Boundary

Step 55 is repository code layout separation and import-boundary contract work.
Step 55 creates `src/mpm_lbm` and `experiments/steps` package boundaries while preserving legacy imports.
Step 55 uses a copy-first compatibility strategy and audit artifacts to prevent further root `src/` mixing.
Step 55 does not change solver behavior.
Step 55 does not add a 48^3 link-area run.
Step 55 does not lengthen the cycle window.
Step 55 does not add a 64^3 case.
Step 55 does not migrate LBM tau or viscosity formulas.
Step 55 does not validate real jet behavior.
Step 55 does not validate jet propulsion.
Step 55 does not implement squid swimming.
Step 55 does not prove grid convergence.
Step 55 does not claim production readiness.
See docs/55_repository_code_layout_separation_import_boundary.md.

## Step 56 Canonical Runtime Implementation Migration Boundary

Step 56 is canonical runtime implementation migration wave 1.
Step 56 moves the first leaf batch of runtime implementations into `src/mpm_lbm/sim/...`.
Step 56 turns the corresponding legacy root modules into compatibility shims.
Step 56 keeps legacy imports working through shims.
Step 56 does not change default solver behavior.
Step 56 does not add a 48^3 link-area run.
Step 56 does not lengthen the cycle window.
Step 56 does not add a 64^3 case.
Step 56 does not migrate LBM tau or viscosity formulas.
Step 56 does not validate real jet behavior.
Step 56 does not validate jet propulsion.
Step 56 does not implement squid swimming.
Step 56 does not prove grid convergence.
Step 56 does not claim production readiness.
See docs/56_canonical_runtime_implementation_migration_wave1.md.

## Step 59 Canonical FSIDriver Real Smoke Simulation Boundary

Step 59 is canonical FSIDriver real smoke simulation work.
Step 59 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`.
Step 59 runs the required `none`, `penalty`, and `moving_boundary` engineering rows at 16^3, 512 particles, and one LBM step.
Step 59 fixes the driver geometry-output filename to `geo_all_fluid_{n_grid}.dat`.
Step 59 keeps outputs lightweight and rejects VTR output, particle NPY output, large Step 59 files, external solver edits, and real-geometry candidate edits.
Step 59 does not change solver formulas.
Step 59 does not activate runtime geometry.
Step 59 does not activate moving-wall velocity.
Step 59 does not add a 48^3 or 64^3 validation row.
Step 59 does not validate real jet behavior.
Step 59 does not validate jet propulsion.
Step 59 does not implement squid swimming.
Step 59 does not prove grid convergence.
Step 59 does not claim production readiness.
See docs/59_canonical_fsidriver_real_smoke_simulation.md.

## Step 60 Controlled Canonical Moving-Boundary Duration Ramp Boundary

Step 60 is controlled canonical real-driver duration ramp work.
Step 60 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`.
Step 60 runs required 16^3, 512-particle rows for moving-boundary engineering at 3 and 5 LBM steps, plus penalty at 5 LBM steps.
Step 60 records runtime timing as a soft warning signal.
Step 60 keeps runtime solver code unchanged.
Step 60 keeps the optional 32^3 probe config disabled by default.
Step 60 keeps outputs lightweight and rejects VTR output, particle NPY output, large Step 60 files, private absolute paths, external solver edits, and real-geometry candidate edits.
Step 60 does not activate runtime geometry.
Step 60 does not activate moving-wall velocity.
Step 60 does not add a 48^3 or 64^3 row.
Step 60 does not validate propulsion.
Step 60 does not validate real squid behavior.
Step 60 does not prove mesh convergence.
Step 60 does not claim deployment readiness.
See docs/60_controlled_canonical_moving_boundary_duration_ramp.md.

## Step 61 Controlled Canonical 32 Moving-Boundary Single-Step Boundary

Step 61 is controlled canonical 32^3 real-driver single-step probe work.
Step 61 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`.
Step 61 runs one required 32^3, 1024-particle moving-boundary engineering row for one LBM step.
Step 61 records runtime timing as a soft warning signal.
Step 61 keeps runtime solver code unchanged.
Step 61 keeps optional 32^3 penalty and 32^3 three-step configs disabled by default.
Step 61 keeps outputs lightweight and rejects VTR output, particle NPY output, large Step 61 files, private absolute paths, external solver edits, and real-geometry candidate edits.
Step 61 does not activate runtime geometry.
Step 61 does not activate moving-wall velocity.
Step 61 does not add a 48^3 or 64^3 row.
Step 61 does not add a required 3-step or 5-step row.
Step 61 does not validate propulsion.
Step 61 does not validate real squid behavior.
Step 61 does not prove grid convergence.
Step 61 does not claim deployment readiness.
See docs/61_controlled_canonical_32_moving_boundary_single_step.md.

## Step 62 Controlled Canonical 32 Moving-Boundary 3-Step Duration Boundary

Step 62 is controlled canonical 32^3 real-driver 3-step duration probe work.
Step 62 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`.
Step 62 runs one required 32^3, 1024-particle moving-boundary engineering row for three LBM steps.
Step 62 repairs the Step 61 report output-guard size mismatch and adds a report consistency guard.
Step 62 records runtime timing as a soft warning signal and a 7200-second hard-limit guard.
Step 62 keeps runtime solver code unchanged.
Step 62 keeps optional 32^3 penalty 3-step and 32^3 moving-boundary 5-step configs disabled by default.
Step 62 keeps outputs lightweight and rejects VTR output, particle NPY output, large Step 62 files, private absolute paths, external solver edits, and real-geometry candidate edits.
Step 62 does not activate runtime geometry.
Step 62 does not activate moving-wall velocity.
Step 62 does not add a 48^3 or 64^3 row.
Step 62 does not add a required 5-step row.
Step 62 does not add a required link-area row.
Step 62 does not validate propulsion.
Step 62 does not validate real squid behavior.
Step 62 does not prove grid convergence.
Step 62 does not claim deployment readiness.
See docs/62_controlled_canonical_32_moving_boundary_3step_duration.md.

## Step 75 Solver-Complete Simulation Campaign Readiness Gate Boundary

Step 75 is a gate-only solver-complete simulation campaign readiness step.
Step 75 reads committed Step71-Step74 evidence, confirms all Step70 activation
gates remain closed, and records an inactive Step76 minimal safe rebaseline
proposal.
Step 75 does not run `FSIDriver3D`.
Step 75 does not initialize or step a driver.
Step 75 does not execute projection smoke.
Step 75 does not activate runtime geometry.
Step 75 does not activate moving-wall velocity.
Step 75 does not activate real geometry.
Step 75 does not add a squid proxy, 48^3 row, or 64^3 row.
Step 75 does not write VTR or particle NPY output.
Step 75 does not change solver formulas or tau semantics.
Step 75 does not claim physical validation, real squid validation, or production readiness.
The Step 75 gate status is `ready_for_step76_rebaseline_only`, and the only
allowed next scope is Step76 minimal safe rebaseline.
See docs/75_solver_complete_simulation_campaign_readiness_gate.md.

## Step 76 Minimal Post-Gate Canonical Driver Rebaseline Boundary

Step 76 is the minimal post-gate canonical driver rebaseline authorized by
Step 75.
Step 76 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`
for exactly one required 32^3, 1024-particle, moving-boundary engineering row
with one LBM step and one MPM substep.
Step 76 keeps the optional 32^3 three-step row disabled by default.
Step 76 does not activate runtime geometry.
Step 76 does not activate moving-wall velocity.
Step 76 does not activate real geometry.
Step 76 does not activate squid proxy behavior.
Step 76 does not use link-area transfer.
Step 76 does not add a 48^3 or 64^3 row.
Step 76 does not write VTR or particle NPY output.
Step 76 does not change solver formulas or tau semantics.
Step 76 does not claim physical validation, real squid validation, grid convergence, or production readiness.
See docs/76_minimal_post_gate_canonical_driver_rebaseline.md.

## Step 77 Minimal Post-Gate Canonical Driver 3-Step Rebaseline Boundary

Step 77 extends only the Step 76 post-gate canonical driver duration from one
LBM step to three LBM steps.
Step 77 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`
for exactly one required 32^3, 1024-particle, moving-boundary engineering row
with three LBM steps and one MPM substep per LBM step.
Step 77 has no optional rows.
Step 77 does not activate runtime geometry.
Step 77 does not activate moving-wall velocity.
Step 77 does not activate real geometry.
Step 77 does not activate squid proxy behavior.
Step 77 does not use link-area transfer.
Step 77 does not add a 48^3 or 64^3 row.
Step 77 does not write VTR or particle NPY output.
Step 77 does not change solver formulas or tau semantics.
Step 77 does not claim physical validation, real squid validation, grid convergence, or production readiness.
See docs/77_minimal_post_gate_canonical_driver_3step_rebaseline.md.

## Step 78 Minimal Post-Gate Canonical Driver 5-Step Rebaseline Boundary

Step 78 extends only the Step 77 post-gate canonical driver duration from three
LBM steps to five LBM steps.
Step 78 calls `FSIDriver3D(...).run()` through `src.mpm_lbm.sim.drivers.fsi_driver`
for exactly one required 32^3, 1024-particle, moving-boundary engineering row
with five LBM steps and one MPM substep per LBM step.
Step 78 has no optional rows.
Step 78 does not add a 10-step baseline.
Step 78 does not activate runtime geometry.
Step 78 does not activate moving-wall velocity.
Step 78 does not activate real geometry.
Step 78 does not activate squid proxy behavior.
Step 78 does not use link-area transfer.
Step 78 does not add a 48^3 or 64^3 row.
Step 78 does not write VTR or particle NPY output.
Step 78 does not change solver formulas or tau semantics.
Step 78 does not claim physical validation, real squid validation, grid convergence, or production readiness.
After Step 78, the next intended direction is single-feature activation planning,
starting with runtime geometry diagnostic-only plan and guard work rather than
another pure duration baseline.
See docs/78_minimal_post_gate_canonical_driver_5step_rebaseline.md.

## Step 79 Runtime Geometry Diagnostic-Only Activation Plan And Guard Boundary

Step 79 plans and guards exactly one future runtime geometry diagnostic-only
single-feature smoke row for Step80.
Step 79 does not call `FSIDriver3D.run()`.
Step 79 does not execute a simulation.
Step 79 does not activate runtime geometry simulation.
Step 79 does not mutate geometry.
Step 79 does not activate moving-wall velocity.
Step 79 does not activate real geometry.
Step 79 does not activate squid proxy behavior.
Step 79 does not use link-area transfer.
Step 79 does not add a 48^3 or 64^3 row.
Step 79 does not add a 10-step baseline.
Step 79 does not write VTR or particle NPY output.
Step 79 does not change solver formulas or tau semantics.
Step 79 does not claim physical validation, real squid validation, grid
convergence, runtime geometry simulation success, moving geometry validation, or
production readiness.
After Step 79, the only planned Step80 row is
`canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke`, a
32^3 / 1024-particle / 3-step / moving_boundary / engineering / box row with
`geometry_motion_application_mode = diagnostic_only`.
See docs/79_runtime_geometry_diagnostic_only_activation_plan_and_guard.md.

## Step 80 Runtime Geometry Diagnostic-Only Canonical Driver Smoke Boundary

Step 80 runs exactly one required canonical driver row:
`canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke`.
The row is 32^3, 1024 particles, three LBM steps, one MPM substep per LBM step,
moving_boundary, engineering transfer, and box geometry.
Step 80 enables only runtime geometry diagnostic-only interface reporting and
writes `geometry_motion_interface_report.json`.
Step 80 does not mutate geometry.
Step 80 does not displace MPM particles.
Step 80 does not update LBM `solid_phi`.
Step 80 does not update LBM `solid_vel`.
Step 80 does not update `dynamic_solid`.
Step 80 does not recompute boundary links.
Step 80 does not change moving bounce-back formulas.
Step 80 does not enable wall velocity.
Step 80 does not enable real geometry.
Step 80 does not enable squid proxy behavior.
Step 80 does not use link-area transfer.
Step 80 does not write VTR or particle NPY output.
Step 80 does not claim physical validation, real squid validation, moving
geometry validation, grid convergence, or production readiness.
See docs/80_runtime_geometry_diagnostic_only_canonical_driver_smoke.md.

## Step 88 Squid Proxy Runtime Geometry Wall Velocity Combined Canonical Driver Smoke Boundary

Step 88 runs exactly one required canonical driver row:
`canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke`.
The row is 32^3, 1024 particles, three LBM steps, one MPM substep per LBM step,
moving_boundary, engineering transfer, and procedural `squid_proxy` geometry.
Step 88 enables only non-strict squid-proxy geometry quality reporting, runtime
geometry diagnostic-only reporting, boundary-motion reporting, and wall velocity
`solid_vel_experimental` reporting. The row uses
`target_u_lbm = [0.0, 0.0, 0.0]` as a Step88-local config choice to isolate the
wall-velocity report from default background flow.
Step 88 does not mutate geometry.
Step 88 does not displace MPM particles through runtime geometry.
Step 88 does not update LBM `solid_phi` through runtime geometry.
Step 88 does not write LBM populations through wall velocity.
Step 88 does not modify moving bounce-back formulas.
Step 88 does not enable real geometry candidates.
Step 88 does not use link-area transfer.
Step 88 does not add a 48^3 or 64^3 row.
Step 88 does not write VTR or particle NPY output.
Step 88 does not change solver formulas or tau semantics.
Step 88 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, or production readiness.
See docs/88_squid_proxy_runtime_geometry_wall_velocity_combined_canonical_driver_smoke.md.

## Step 89 First User Simulation Dry Run Plan And Guard Boundary

Step 89 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, and does not execute simulation.
Step 89 plans exactly one future Step90 row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run`.
The planned row is 32^3, 1024 particles, five LBM steps, one MPM substep per
LBM step, moving_boundary, engineering transfer, procedural `squid_proxy`
geometry, runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting.
Step 89 keeps `target_u_lbm = [0.0, 0.0, 0.0]` for the planned first user dry
run so background-flow variation is not mixed into Step90.
Step 89 does not create a driver-run directory.
Step 89 does not enable real geometry candidates.
Step 89 does not use link-area transfer.
Step 89 does not add a 48^3 or 64^3 row.
Step 89 does not write VTR or particle NPY output.
Step 89 does not change solver formulas or tau semantics.
Step 89 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, or production readiness.
See docs/89_first_user_simulation_dry_run_plan_and_guard.md.

## Step 91 First User Simulation 10-Step Dry Run Plan And Guard Boundary

Step 91 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, and does not execute simulation.
Step 91 plans exactly one future Step92 row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run`.
The planned row is 32^3, 1024 particles, ten LBM steps, one MPM substep per
LBM step, moving_boundary, engineering transfer, procedural `squid_proxy`
geometry, runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting.
The only planned expansion from Step90 to Step92 is `n_lbm_steps = 5 -> 10`.
Step 91 keeps `target_u_lbm = [0.0, 0.0, 0.0]` for the planned 10-step dry
run so background-flow variation is not mixed into Step92.
Step 91 does not create a driver-run directory.
Step 91 does not enable real geometry candidates.
Step 91 does not use link-area transfer.
Step 91 does not add a 48^3 or 64^3 row.
Step 91 does not write VTR or particle NPY output.
Step 91 does not change solver formulas or tau semantics.
Step 91 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, or production readiness.
See docs/91_first_user_simulation_10step_dry_run_plan_and_guard.md.

## Step 94 Taichi GGUI Visualization Smoke Boundary

Step 94 runs exactly one required canonical driver row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke`.
The row is 32^3, 1024 particles, one LBM step, one MPM substep per LBM step,
moving_boundary, engineering transfer, procedural `squid_proxy` geometry,
runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting. Step 94 then renders one Taichi GGUI frame
through an independent evidence renderer and writes one PNG screenshot.
Step 94 does not write VTR, particle NPY, video, raw geometry, real geometry
candidate output, dense wall velocity output, or dense displacement output.
Step 94 does not mutate geometry, change solver formulas, enable link-area
transfer, enable 48^3/64^3, or claim physical validation, real squid
validation, squid swimming, squid actuation, grid convergence, production
visualization readiness, or production simulation readiness.
See docs/94_taichi_ggui_visualization_smoke.md.

## Step 95 Taichi GGUI 10-Step First User Visualization Plan And Guard Boundary

Step95 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, does not execute simulation, does not open a GGUI window, and
does not write screenshots, video, VTR, or particle NPY output.
Step95 plans exactly one future Step96 row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run`.
The planned row combines the Step92 10-step first-user dry-run envelope with
the Step94 Taichi GGUI screenshot path. Step95 keeps real geometry candidates,
link-area transfer, 48^3, 64^3, dense output, solver formula changes, tau
migration, physical validation, real squid validation, squid swimming, squid
actuation, and production-readiness claims closed.
See docs/95_taichi_ggui_10step_first_user_visualization_plan_and_guard.md.

## Step 96 Taichi GGUI 10-Step First User Visualization Run Boundary

Step96 runs exactly one required canonical driver row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run`.
The row is 32^3, 1024 particles, 10 LBM steps, one MPM substep per LBM step,
moving_boundary, engineering transfer, procedural `squid_proxy` geometry,
runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting. Step96 then renders one Taichi GGUI frame
and writes one PNG screenshot.
Step96 does not write VTR, particle NPY, video, raw geometry, real geometry
candidate output, dense wall velocity output, sparse wall velocity output,
dense displacement output, or displaced-particle output. Step96 does not mutate
geometry, change solver formulas, enable link-area transfer, enable 48^3/64^3,
or claim physical validation, real squid validation, squid swimming, squid
actuation, grid convergence, production visualization readiness, or production
simulation readiness.
See docs/96_taichi_ggui_10step_first_user_visualization_run.md.

## Step 97 48-Cube Taichi GGUI Visualization Expansion Plan And Guard Boundary

Step97 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, does not execute simulation, does not open a GGUI window, and
does not write screenshots, video, VTR, or particle NPY output.
Step97 plans exactly one future Step98 row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke`.
The planned row changes Step96 only from 32^3 to 48^3 and from 10 LBM steps to
one LBM step, intentionally isolating 48^3 grid-expansion smoke behavior.
Step97 keeps 64^3, real geometry candidates, link-area transfer, dense output,
solver formula changes, tau migration, physical validation, real squid
validation, squid swimming, squid actuation, and production-readiness claims
closed.
See docs/97_48cube_taichi_ggui_visualization_expansion_plan_and_guard.md.

## Step 98 48-Cube Taichi GGUI Visualization Smoke Boundary

Step98 runs exactly one required canonical driver row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke`.
The row is 48^3, 1024 particles, one LBM step, one MPM substep per LBM step,
moving_boundary, engineering transfer, procedural `squid_proxy` geometry,
runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting. Step98 then renders one Taichi GGUI frame
and writes one PNG screenshot.
Step98 does not write VTR, particle NPY, video, raw geometry, real geometry
candidate output, dense wall velocity output, sparse wall velocity output,
dense displacement output, or displaced-particle output. Step98 does not mutate
geometry, change solver formulas, enable link-area transfer, enable 64^3, or
claim 48^3 10-step readiness, physical validation, real squid validation,
squid swimming, squid actuation, grid convergence, production visualization
readiness, or production simulation readiness.
See docs/98_48cube_taichi_ggui_visualization_smoke.md.

## Step 99 48-Cube 5-Step Taichi GGUI Visualization Plan And Guard Boundary

Step99 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, does not execute simulation, does not open a GGUI window, and
does not write screenshots, video, VTR, or particle NPY output.
Step99 plans exactly one future Step100 row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`.
The only planned expansion from Step98 is `n_lbm_steps = 1 -> 5`.
Step99 keeps 64^3, real geometry candidates, link-area transfer, dense output,
solver formula changes, tau migration, physical validation, real squid
validation, squid swimming, squid actuation, and production-readiness claims
closed.
See docs/99_48cube_5step_taichi_ggui_visualization_plan_and_guard.md.

## Step 100 48-Cube 5-Step Taichi GGUI Visualization Run Boundary

Step100 runs exactly one required canonical driver row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`.
The row is 48^3, 1024 particles, five LBM steps, one MPM substep per LBM step,
moving_boundary, engineering transfer, procedural `squid_proxy` geometry,
runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting. Step100 then renders one Taichi GGUI frame
and writes one PNG screenshot.
The only expansion from Step98 is `n_lbm_steps = 1 -> 5`.
Step100 does not write VTR, particle NPY, video, raw geometry, real geometry
candidate output, dense wall velocity output, sparse wall velocity output,
dense displacement output, or displaced-particle output. Step100 does not mutate
geometry, change solver formulas, enable link-area transfer, enable 64^3, or
claim 48^3 10-step readiness, physical validation, real squid validation,
squid swimming, squid actuation, grid convergence, production visualization
readiness, or production simulation readiness.
See docs/100_48cube_5step_taichi_ggui_visualization_run.md.

## Step 101 48-Cube 10-Step Taichi GGUI Visualization Plan And Guard Boundary

Step101 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, does not execute simulation, does not open a GGUI window, and
does not write screenshots, video, VTR, or particle NPY output.
Step101 plans exactly one future Step102 row:
`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run`.
The row is planned as 48^3, 1024 particles, ten LBM steps, one MPM substep per
LBM step, moving_boundary, engineering transfer, procedural `squid_proxy`
geometry, runtime geometry diagnostic-only reporting, wall velocity
`solid_vel_experimental` reporting, and Taichi GGUI screenshot output in
Step102 only.
The only expansion from Step100 is `n_lbm_steps = 5 -> 10`.
Step101 keeps 64^3, real geometry candidates, link-area transfer, dense output,
solver formula changes, tau migration, physical validation, real squid
validation, squid swimming, squid actuation, 48^3 10-step run-passed claims,
and production-readiness claims closed.
See docs/101_48cube_10step_taichi_ggui_visualization_plan_and_guard.md.

## Step 102 Fluent Official Two-Way FSI Benchmark Intake And Guard Boundary

Step102 intentionally redirects away from the Step101-planned 48^3 / 10-step
GGUI visual run before that row is executed. Step102 is benchmark intake and
guard only. It records the Fluent official two-way intrinsic FSI duct/flap
source as metadata, defines private-data and mapping policies, and preserves
Step101/Step100 regression evidence.
Step102 does not run `FSIDriver3D`, does not call `driver.run()`, does not run
Fluent, does not import Fluent mesh, does not run benchmark comparison, does
not open GGUI, and does not commit Ansys official files such as the archive,
mesh, journal, case/data files, screenshots, or copied tutorial content.
Step102 permits only qualitative and diagnostic future comparison planning.
It does not claim Fluent benchmark pass, solver equivalence, exact Fluent
matching, physical validation, real FSI validation, grid convergence, or
production readiness.
Official benchmark inputs belong under the ignored local-private path
`benchmarks/private/fluent_fsi_2way/` if the user supplies them locally.
See docs/102_fluent_official_2way_fsi_benchmark_intake_and_guard.md.

## Step 103 Fluent-Inspired Duct-Flap Proxy Solver Comparison Smoke Boundary

Step103 adds a real solver smoke row for a procedural duct-flap proxy inspired
by the public Fluent two-way FSI duct/flap tutorial metadata captured in
Step102. The canonical row is
`fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke`.
It uses the canonical driver for one 48^3, 1024-particle, five-step
moving-boundary smoke and writes a GGUI screenshot plus a committed solver gap
report.
Step103 does not import a Fluent mesh, does not commit official Fluent files,
does not require private Fluent CSV data, and does not claim Fluent
validation, solver equivalence, physical validation, real FSI validation, or
production readiness.
See docs/103_fluent_inspired_duct_flap_proxy_solver_comparison_smoke.md.

## Step 104 Fluent Duct-Flap Official Problem Setup Repair Boundary

Step104 repairs the problem setup gap found after Step103. The canonical row is
`fluent_duct_flap_setup_repair_48_5step_smoke`.
It separates inlet flow from solid initial velocity, applies
`target_u_lbm` only as the x-min inlet target, uses a pressure outlet at x-max,
writes a deterministic non-all-fluid duct static geometry artifact, maps the
public silicone material reference into MPM config, applies a fixed-base MPM
mask/constraint, disables the Step36 squid wall-velocity path, and writes a
proxy flap-tip displacement time series.
Step104 does not change LBM collision, tau, MPM update, moving-boundary, or
reaction-transfer formulas.
Step104 does not claim Fluent validation, solver equivalence, exact Fluent
intrinsic structural-model reproduction, dynamic-mesh equivalence, completion
of the full 50-step public tutorial transient, physical validation, real FSI
validation, or production readiness.
See docs/104_fluent_duct_flap_official_problem_setup_repair.md.

## Step 105 Fluent Duct-Flap Proxy 50-Step Transient Dimensional-Gap Audit Boundary

Step105 extends the Step104 repaired duct-flap setup to exactly one 48^3,
1024-particle, 50-step proxy transient row:
`fluent_duct_flap_proxy_48_50step_transient_gap_smoke`.
It records that `target_u_lbm = [0.02, 0.0, 0.0]` maps to about
`0.0833333333 m/s` under the current proxy scale, not the official `10 m/s`
inlet. It also records inlet/mid/outlet plane flow-development diagnostics and
restores the required gap taxonomy for dimensionality, conformal mesh, linear
elasticity, dynamic mesh, exact monitor, dimensional velocity mapping,
fluid-model equivalence, and missing steady preflow.
Step105 does not change LBM collision, tau, MPM update, moving-boundary,
bounce-back, coupling, or reaction-transfer formulas.
Step105 does not claim Fluent validation, solver equivalence, exact Fluent
structural-model reproduction, official steady-preflow initialization, exact
structural-point monitor equivalence, physical validation, real FSI validation,
or production readiness.
See docs/105_fluent_duct_flap_proxy_50step_transient_dimensional_gap_audit.md.

## Step 109 Fluent Duct-Flap FSI Response-Amplitude Sensitivity Matrix Boundary

Step109 runs a bounded 9-row response-amplitude sensitivity matrix for the
Step108 low-Mach duct-flap proxy. It preserves the Step108 official-speed
mapping (`u_lbm = 0.02`, 120 LBM substeps per `0.0005 s` official FSI step,
50 samples through `0.025 s`) and varies only evidence-level row configs for
moving-boundary force cap, reaction scale, and generated material-reference
geometry configs.
The selected row is `cap_1e-1_scale_10`; its peak proxy displacement is
`0.0012614636216312647 m` versus the Step108 peak `1.2332112646618043e-6 m`.
Step109 also records four monitor variants for the selected row and separate
force-cap and structural sensitivity reports.
Step109 does not change LBM collision, tau, moving bounce-back, reaction
transfer formula, MPM stress/update, external dependencies, or real geometry
data.
Step109 does not claim Fluent validation, direct solver equivalence, exact
official monitor equivalence, official dynamic mesh reproduction, official
case/data reproduction, or production readiness.
See docs/109_fluent_duct_flap_fsi_response_amplitude_sensitivity_matrix.md.

## Upstream LBM Note

The LBM backend is derived from the vendored taichi_LBM3D single-phase solver under external/taichi_LBM3D. The external source is kept unmodified in this project workflow. For license details, see the upstream repository and vendored license files if present.
