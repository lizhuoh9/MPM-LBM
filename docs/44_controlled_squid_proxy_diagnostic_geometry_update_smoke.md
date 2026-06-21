# Step 44 Controlled Squid Proxy Diagnostic Geometry Update Smoke

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

Step 44 reads the accepted Step 42 displacement diagnostics through the guarded Step 43 interface boundary, selects five representative phases, and summarizes a transient displaced copy for `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`. The copy is used for compact diagnostics and projection-only smoke rows at `32^3` and `48^3`.

The diagnostic copy is not stored as a dense geometry artifact. The Step 44 outputs are small CSV/JSON summaries and logs under `outputs/step44_*` and `logs/step44_*`.

## Validation Surface

- `configs/step44_diagnostic_geometry_update.json` defines the runtime-copy diagnostic contract.
- `src/diagnostic_geometry_update_config.py` validates the Step 44 config and all disabled mutation/write flags.
- `src/diagnostic_geometry_update.py` builds runtime displaced-copy summaries without writing full point arrays.
- `src/diagnostic_geometry_projection.py` runs projection-only occupancy diagnostics from the transient copy.
- `src/diagnostic_geometry_state_guard.py` checks original geometry and region-mask hashes plus forbidden-output counters.
- `baseline_tests/run_step44_*.py` produces the committed Step 44 evidence artifacts.
- `tests/test_step44_diagnostic_geometry_update_smoke_contract.py` verifies the artifact contract.

## Explicit Boundary

The optional one-step smoke is a diagnostic descriptor that uses projection-only evidence for original and phase-0.35 runtime-copy rows. It is not a broader coupled-motion validation. The production driver path remains unchanged by Step 44.

Step 45 may build on this by adding a controlled runtime geometry projection integration smoke, still without broad coupled-cycle claims.
