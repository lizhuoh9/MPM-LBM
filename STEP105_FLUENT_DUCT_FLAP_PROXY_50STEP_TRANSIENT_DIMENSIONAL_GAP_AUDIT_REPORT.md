# Step105 Fluent Duct-Flap Proxy 50-Step Transient Dimensional-Gap Audit Report

Allowed claim:

```text
Fluent duct-flap proxy 50-step transient smoke ran with repaired Step104 setup, and dimensional/modeling gaps blocking Fluent-equivalence claims are explicitly audited.
```

This report does not claim Fluent equivalence, Fluent validation, physical
validation, real FSI validation, official steady-preflow initialization,
official structural-point monitor equivalence, or production readiness.

## Implementation Summary

- Added Step105 detailed goal, config, acceptance policy, runners, evidence
  modules, docs, tests, output guard, and artifact manifest.
- Added a dimensional mapping report showing the current proxy inlet maps to
  about `0.08333333333333333 m/s`, not the official `10 m/s`.
- Ran one repaired-setup 48^3 / 1024-particle / 50-step duct-flap proxy smoke.
- Added flow-development diagnostics for inlet, mid-duct, and outlet planes.
- Restored an eight-gap taxonomy covering the remaining blockers to Fluent
  equivalence claims.

No LBM collision, tau, MPM update, moving-boundary, bounce-back, coupling, or
reaction-transfer formulas were changed.

## Primary Results

Dimensional mapping:

- `proxy_inlet_velocity_mps = 0.08333333333333333`
- `official_inlet_velocity_mps = 10.0`
- `velocity_ratio = 0.008333333333333333`
- `dimensional_velocity_mapping_gap_present = true`

Transient smoke:

- row: `fluent_duct_flap_proxy_48_50step_transient_gap_smoke`
- completed LBM steps: `50`
- diagnostics rows: `51`
- proxy flap-tip time-series rows: `51`
- `has_nan = false`
- `has_inf = false`
- fixed-base max displacement: `0.0`
- fixed-base max velocity: `0.0`
- `target_u_lbm_applied_to_inlet = true`
- `target_u_lbm_applied_to_solid_initial_velocity = false`
- `all_fluid_geometry_used = false`
- `step36_squid_wall_velocity_config_used = false`

Flow development:

- inlet plane mean `ux`: `0.02000000700354576`
- mid-duct plane mean `ux`: `0.010271445848047733`
- outlet plane mean `ux`: `0.0`
- final fluid mean `ux`: `0.005699269473552704`
- final far-field fluid mean `ux`: `0.005688079632818699`
- `flow_development_not_fluent_equivalent = true`

Gap taxonomy:

- `gap_count = 8`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`

## Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\evidence\step105_common.py src\mpm_lbm\evidence\step105_dimensional_mapping.py src\mpm_lbm\evidence\step105_gap_taxonomy.py src\mpm_lbm\evidence\step105_transient_gap_smoke_runner.py src\mpm_lbm\evidence\step105_output_guard.py baseline_tests\step105_common.py baseline_tests\run_step105_dimensional_mapping.py baseline_tests\run_step105_gap_taxonomy.py baseline_tests\run_step105_fluent_duct_flap_proxy_50step_transient_gap_smoke.py baseline_tests\run_step105_flow_development.py baseline_tests\run_step105_output_guard.py baseline_tests\run_step105_artifact_manifest.py tests\test_step105_fluent_duct_flap_proxy_transient_gap_contract.py tests\test_step105_output_guard_contract.py
```

Result: passed.

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_dimensional_mapping.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_gap_taxonomy.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_fluent_duct_flap_proxy_50step_transient_gap_smoke.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_flow_development.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_output_guard.py
```

Result: all passed.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step105_fluent_duct_flap_proxy_transient_gap_contract.py tests\test_step105_output_guard_contract.py
```

Result: `6 passed in 0.55s`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Result: `1159 passed in 167.96s`.

```powershell
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
```

Result: `1159 passed, 1 warning in 77.97s`.
The warning is a Taichi dependency deprecation warning for
`locale.getdefaultlocale` on the Anaconda interpreter.

```powershell
pytest -q
```

Result: `1159 passed, 1 warning in 77.87s`.
This is the entrypoint used by the ECC pre-push hook.

## Final Guard Snapshot

- dimensional mapping pass: `true`
- transient gap smoke pass: `true`
- transient elapsed seconds: `114.038758900002`
- flow-development report pass: `true`
- gap taxonomy pass: `true`
- output guard pass: `true`
- output guard row count: `37`
- output guard total size: `0.3846321105957031 MB`
- artifact manifest pass: see
  `outputs/step105_artifact_manifest/artifact_summary.csv`
