# Step135 Interior Reflection and Bulk-Dynamics Diagnosis Report

## Decision

Step135 produced bounded real 48^3 / 250-step LBM-only diagnostic evidence for
`planeflux_interior_diag48`.

Final Step135 state:

- 6 / 6 diagnostic rows completed 250 / 250.
- All rows stayed finite.
- All rows had `first_failure_step = null` and `first_failure_reason = null`.
- 0 / 6 rows passed the relaxed reporting gate set.
- No Step135 500-step promotion was run.
- No selected 96^3 run is allowed.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.

The evidence supports an interior / startup-transient diagnosis, not an
outlet-local readout-artifact diagnosis and not boundary selection.

## Code Surface

Step135 added a diagnostic-only phase:

```text
planeflux_interior_diag48
```

The phase uses:

```text
row_role = interior_reflection_diagnostic_48
```

The role is not in the selected-candidate semantics set and cannot enable
selected 96^3. The role is included in solver-state hashing so stale Step134
rows cannot be accepted as Step135 diagnostics even when the baseline physical
parameters match.

Step135 also added compact x-profile diagnostics:

- `x_profile_flux_samples`
- `x_profile_ux_mean_samples`
- `x_profile_rho_mean_samples`
- `x_profile_flux_tail_values_by_x`
- `x_profile_flux_tail_slope_by_x`
- `x_profile_flux_tail_cv_by_x`
- `x_profile_flux_last_to_mean_ratio_by_x`
- `x_profile_flux_phase_lag_proxy`
- `collapse_first_x`
- `collapse_first_step`

For 48^3 rows the sampled stations are:

```text
0, 6, 12, 18, 24, 30, 36, 42, 45, 46, 47
```

The implementation clamps and deduplicates these stations for tiny smoke
domains.

Step135 added a runner-level inlet ramp surface:

```text
open_boundary_inlet_ramp_steps = 0
open_boundary_inlet_ramp_profile = linear
effective_inlet_u_lbm = inlet_u_lbm * min(1.0, step / open_boundary_inlet_ramp_steps)
```

The default is off. The ramp fields are written to metadata, summaries, flow
diagnostics, manifests, and solver-state hashes. The LBM x-left velocity target
is now stored in a Taichi vector field so the ramp is read by boundary kernels
at each step instead of being a compile-time Python constant.

## Artifacts

Tiny smoke artifact:

```text
outputs/step135_interior_reflection_diagnostics/tiny_smoke/tiny_step135_interior_reflection_smoke
```

48^3 artifact root:

```text
outputs/step135_interior_reflection_diagnostics/planeflux_interior_diag48
```

Important artifact files:

```text
outputs/step135_interior_reflection_diagnostics/tiny_smoke/campaign_manifest.json
outputs/step135_interior_reflection_diagnostics/tiny_smoke/tiny_step135_interior_reflection_smoke/finite_stability_report.json
outputs/step135_interior_reflection_diagnostics/planeflux_interior_diag48/campaign_manifest.json
outputs/step135_interior_reflection_diagnostics/planeflux_interior_diag48/step121_summary.json
outputs/step135_interior_reflection_diagnostics/planeflux_interior_diag48/step121_best_boundary_selection.json
outputs/step135_interior_reflection_diagnostics/planeflux_interior_diag48/duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp0_niu0p10_out5_250step_interior_diag/flow_development_diagnostics_summary.json
```

Both campaign manifests and all row finite reports record:

```text
code_commit_at_run = e194b896ea2153da3dc906272fd4cfd84124dec4
```

## Commands

Tiny smoke:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_interior_diag48 `
  --output-dir outputs\step135_interior_reflection_diagnostics\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume
```

48^3 diagnostic run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_interior_diag48 `
  --output-dir outputs\step135_interior_reflection_diagnostics\planeflux_interior_diag48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

## Results

All rows completed 250 / 250 and had `selected96_claim_allowed = false`.

| row | mass abs | flux mean | flux max | out/in | mid/in | outlet cv | last/mean | x36 cv | x42 cv | x46 cv | x47 cv | collapse first |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline ramp0 niu0.10 | 0.014007 | 0.271172 | 0.646369 | 1.192471 | 0.801729 | 0.254438 | 0.297752 | 0.393378 | 0.310583 | 0.258692 | 0.254438 | x=24 step=220 |
| ramp50 niu0.10 | 0.012941 | 0.300229 | 0.381482 | 1.439450 | 1.197004 | 0.083142 | 0.838666 | 0.155360 | 0.106078 | 0.085112 | 0.083142 | x=18 step=245 |
| ramp100 niu0.10 | 0.008564 | 0.365445 | 0.414809 | 1.581575 | 1.463973 | 0.062496 | 0.878883 | 0.105286 | 0.077223 | 0.064176 | 0.062496 | none |
| niu0.08 | 0.014311 | 0.271697 | 0.665610 | 1.190597 | 0.788855 | 0.257185 | 0.281959 | 0.411874 | 0.324023 | 0.262001 | 0.257185 | x=24 step=220 |
| niu0.12 | 0.013732 | 0.270032 | 0.625513 | 1.194295 | 0.813058 | 0.251105 | 0.314859 | 0.377374 | 0.298818 | 0.254902 | 0.251105 | x=24 step=220 |
| convective comparator | 0.022051 | 0.214805 | 0.446259 | 1.308885 | 1.300581 | 0.175563 | 1.381282 | 0.287928 | 0.119135 | 0.162596 | 0.175563 | x=12 step=235 |

No row passed the relaxed reporting gate set. The closest stationarity row was
the ramp100 regularized row: it passed mass acceptance, outlet CV, and
last-to-mean stationarity, but failed ratio and flux-imbalance gates
(`out/in = 1.5815747922655192`, `mid/in = 1.4639728217023902`,
`flux_imbalance_rel_tail_mean = 0.36544508198725295`,
`flux_imbalance_rel_tail_max = 0.4148086159154826`).

## Interpretation

The baseline high-frequency x-profile does not support an outlet-local
measurement artifact. The first compact collapse label appears at interior
station `x = 24` at step 220, while downstream stations `x = 36`, `42`, `46`,
and `47` all show large tail variation. This is a bulk-profile transient moving
through the domain, not a one-cell `nx - 1` readout failure.

The inlet ramp materially changes the failure mode:

- ramp50 delays the collapse label to step 245 and reduces outlet CV to
  `0.08314201013981277`, but still fails mass acceptance, flux imbalance, and
  outlet/midplane ratios.
- ramp100 removes the collapse label under the Step135 0.70 compact-sample
  proxy and improves mass to `0.008563736649658519`, but it overdrives the
  profile ratios and flux imbalance.

The niu sensitivity rows do not materially change the baseline diagnosis.
`lbm_niu = 0.08` and `lbm_niu = 0.12` both retain an interior collapse label at
`x = 24`, step 220, with mass acceptance still above `0.01` and outlet CV near
`0.25`.

The convective comparator is diagnostic only. It has lower outlet CV than the
regularized baseline, but fails mass acceptance and ratio gates. Its outlet tail
rises rather than collapses, while the compact collapse proxy first appears
upstream (`x = 12`, step 235). That again points to bulk dynamics rather than a
single outlet-cell artifact.

Controller feedback appears to respond to the bulk transient. Regularized rows
show tail mean velocity feedback near `-0.0023` with density feedback below
`1.2e-05`. The x-profile changes are already visible throughout the interior
sample stations, so Step135 does not justify blaming a disconnected outlet
controller alone.

## Next Step

Step136 should remain bounded 48^3 LBM-only. A reasonable next diagnostic is a
ramped regularized branch that directly addresses the ratio overdrive seen in
ramp100, for example a bounded ramp-plus-target/feedback calibration or
interior-development control. Step136 should not start selected 96^3 or a
500-step promotion unless a later artifact-backed step first passes the
explicit relaxed gates.

## Verification

Focused verification run before artifact generation:

```text
D:\working\taichi\env\python.exe -m pytest -q tests/test_step135_interior_reflection_diagnostics_contract.py --basetemp=outputs/tmp/pytest-step135-contract
D:\working\taichi\env\python.exe -m pytest -q tests/test_step134_outlet_stationarity_contract.py tests/test_step133_mass_damped_plane_flux_contract.py tests/test_step132_plane_flux_authority_sweep_contract.py tests/test_step131_plane_flux_controller_contract.py --basetemp=outputs/tmp/pytest-step131-134
D:\working\taichi\env\python.exe -m pytest -q tests/test_step56_behavior_preservation_contract.py tests/test_step56_canonical_runtime_migration_contract.py tests/test_step56_import_execution_contract.py tests/test_step56_legacy_shim_contract.py tests/test_step57_behavior_preservation_contract.py tests/test_step57_driver_support_migration_contract.py tests/test_step57_import_execution_contract.py tests/test_step57_legacy_shim_contract.py tests/test_step57_src_init_export_contract.py tests/test_step57_step56_regression_contract.py tests/test_step58_behavior_preservation_contract.py tests/test_step58_fsidriver_migration_contract.py tests/test_step58_import_execution_contract.py tests/test_step58_legacy_shim_contract.py tests/test_step58_optional_bridge_contract.py tests/test_step58_step57_regression_contract.py --basetemp=outputs/tmp/pytest-step56-58
D:\working\taichi\env\python.exe -m pytest -q tests/test_step116_lbm_boundary_diagnostics_contract.py tests/test_step130_flow_development_diagnostics_contract.py --basetemp=outputs/tmp/pytest-diagnostics
D:\working\taichi\env\python.exe -m py_compile experiments/steps/step120_lbm_boundary_repair_large_real_execution.py experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py src/mpm_lbm/sim/diagnostics/lbm_boundary_diagnostics.py src/mpm_lbm/sim/lbm/fluid.py
```

The original goal-listed Step56 filenames were stale in this checkout; the
actual Step56/57/58 contract files listed above were run instead.

An initial 120-second run of the Step131-Step134 group timed out after 23
passing tests; the same command completed with a longer timeout and passed all
24 tests.
