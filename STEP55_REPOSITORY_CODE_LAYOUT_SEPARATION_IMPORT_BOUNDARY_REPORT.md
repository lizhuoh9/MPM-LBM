# Step 55 Repository Code Layout Separation And Import Boundary Report

Step 55 introduces repository code layout separation and import-boundary contracts. It is a structure step, not a physics expansion step.

## Scope Boundary

- Step 55 does not add a 48^3 `link_area_experimental` run.
- Step 55 does not lengthen the cycle window.
- Step 55 does not add a 64^3 case.
- Step 55 does not migrate LBM tau or viscosity formulas.
- Step 55 does not recompute historical physics outputs with changed formulas.
- Step 55 does not change default solver behavior.
- Step 55 does not edit `external/taichi_LBM3D`.
- Step 55 does not edit `data/real_geometry_candidates`.
- Step 55 does not claim real-jet, jet-propulsion, squid-swimming, grid-convergence, production-readiness, or full-solver validation.

## Layout Contract

Step 55 creates the canonical `src/mpm_lbm` package boundary and the `experiments/steps` step-specific boundary. The first migration is copy-first and wrapper-based: existing root `src/*.py` files remain available for old imports, while new canonical package paths exist and are enforced by audits.

The layout policy classifies root `src/*.py` files as compatibility or approved legacy surfaces. New Step55 evidence code is placed under `src/mpm_lbm/evidence`.

## Import Boundary Contract

`src/mpm_lbm/sim` is checked as the simulation runtime boundary. It must not import experiments, tests, baseline tests, outputs, logs, or docs, and it must not contain Step 50/51/52/53/54 implementation constants.

## Step 54 Repairs Folded Into Step 55

Step 55 standardizes the test strength enum to:

```text
artifact_contract
artifact_plus_source_contract
runner_reexecution_contract
proxy_diagnostic_contract
solver_smoke_contract
formula_unit_contract
numerical_benchmark_contract
```

Step 55 also replaces stale hard-coded pytest count wording with:

```text
A passing full pytest run means contract/artifact/proxy/solver-smoke tests passed according to the test strength audit classification.
```

## Evidence

- `outputs/step55_code_layout_audit/code_layout_audit.json`
- `outputs/step55_import_boundary_audit/import_boundary_audit.json`
- `outputs/step55_compatibility_shim_audit/compatibility_shim_audit.json`
- `outputs/step55_test_strength_enum_audit/test_strength_enum_audit.json`
- `outputs/step55_step54_regression_guard/step54_regression_guard.json`
- `outputs/step55_artifact_manifest/artifact_summary.json`

## Result

Step 55 is accepted when all Step55 audits pass, Step54 regression remains green, both supported pytest environments pass, and the pre-push hook passes.
