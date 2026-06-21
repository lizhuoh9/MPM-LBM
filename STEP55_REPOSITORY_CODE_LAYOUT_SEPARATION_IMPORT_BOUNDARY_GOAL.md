# Step 55 Repository Code Layout Separation And Import Boundary Contract Goal

## Step Name

Step 55 Repository Code Layout Separation And Import Boundary Contract.

## Source Context

Step 54 repaired the main evidence-integrity semantics:

- LBM `niu` is now explicitly named as a legacy external solver relaxation parameter.
- Step 50, Step 51, and Step 52 proxy diagnostic records disclose proxy source fields.
- Step 50, Step 51, and Step 52 state guards disclose fixed-zero method metadata.
- Step 54 added evidence index, test-strength audit, claim guard, Step 53 regression guard, and artifact manifest.

Step 55 must now address the remaining repository layout problem without restarting physics expansion. The current root `src/` namespace still mixes simulation runtime, diagnostics, step-specific proxy/audit code, and repository evidence tools. Step 55 must introduce a stable package boundary, import-boundary checks, and compatibility surfaces so later work cannot keep adding unrelated code to root `src/`.

Step 55 must also fix two Step 54 follow-up issues:

- `test_strength_level` values must match an explicit policy enum.
- Step 54 long-lived docs/tests must not hard-code stale pytest pass counts such as `604/614`.

## Non-Negotiable Scope Boundaries

Step 55 is a structure and contract step only.

Step 55 must not:

- add a 48^3 `link_area_experimental` run,
- lengthen the cycle window,
- add a 64^3 case,
- migrate the LBM tau / viscosity formula,
- recompute historical physics outputs with changed formulas,
- change default solver behavior,
- edit `external/taichi_LBM3D`,
- edit `data/real_geometry_candidates`,
- claim real-jet validation,
- claim jet-propulsion validation,
- claim squid-swimming implementation,
- claim grid convergence,
- claim production readiness,
- claim full solver validation,
- hide solver behavior in test or runner code.

If a proposed edit would affect solver physics, runtime stepping, default coupling behavior, or historical physical artifact values, it is outside Step 55.

## Strategy

Use a copy-first layout separation with compatibility surfaces:

1. Create the canonical package hierarchy under `src/mpm_lbm/`.
2. Create the step/experiment hierarchy under `experiments/steps/`.
3. Copy or wrap representative runtime, diagnostics, evidence, and step-specific surfaces into those new locations.
4. Keep old import paths stable for existing tests, runners, and reports.
5. Add audits that classify root-level `src/*.py` files as one of:
   - compatibility shim,
   - approved legacy runtime surface pending final migration,
   - approved legacy diagnostics surface pending final migration,
   - approved legacy step-specific surface pending final migration,
   - approved legacy evidence surface pending final migration.
6. Make future drift visible by failing audits if new root-level mixed-purpose files appear without classification.

This avoids a dangerous one-shot deletion of legacy modules while still establishing the new boundaries and enforcing them with artifacts and tests.

## Target Layout

Create these packages:

```text
src/
  mpm_lbm/
    __init__.py
    sim/
      __init__.py
      lbm/
        __init__.py
        config.py
        fluid.py
        relaxation_semantics.py
      mpm/
        __init__.py
        config.py
        solid.py
      coupling/
        __init__.py
        projection.py
        penalty.py
        moving_boundary.py
        link_area.py
        link_area_accounting.py
        momentum_accounting.py
      drivers/
        __init__.py
        fsi_config.py
        fsi_driver.py
        sim_config.py
      units/
        __init__.py
        mapper.py
      io/
        __init__.py
        run_utils.py
    diagnostics/
      __init__.py
    evidence/
      __init__.py
      proxy_diagnostic_truthfulness.py
      state_guard_truthfulness.py
      repository_evidence_index.py
      repository_test_strength_audit.py
      repository_evidence_integrity_claim_guard.py
      repository_evidence_integrity_artifact_manifest.py
      repository_evidence_integrity_regression_guard.py
      code_layout_audit.py
      import_boundary_audit.py
      compatibility_shim_audit.py

experiments/
  __init__.py
  steps/
    __init__.py
    step50_one_cycle_proxy/
      __init__.py
    step51_transfer_comparison_proxy/
      __init__.py
    step52_48_feasibility_proxy/
      __init__.py
    step53_support_scaling_audit/
      __init__.py
    step54_evidence_integrity_repair/
      __init__.py
```

Step 55 may start with wrappers for heavy runtime modules where direct import would trigger optional runtime dependencies in the pre-push hook environment. The wrapper must be explicit and documented as compatibility-safe; it must not change solver behavior.

## Required Step 55 Files

Goal/report/docs:

```text
STEP55_REPOSITORY_CODE_LAYOUT_SEPARATION_IMPORT_BOUNDARY_GOAL.md
STEP55_REPOSITORY_CODE_LAYOUT_SEPARATION_IMPORT_BOUNDARY_REPORT.md
docs/55_repository_code_layout_separation_import_boundary.md
docs/REPOSITORY_CODE_LAYOUT_POLICY.md
```

Configs:

```text
configs/step55_code_layout_policy.json
configs/step55_import_boundary_policy.json
configs/step55_compatibility_shim_policy.json
configs/step55_test_strength_enum_policy.json
```

Evidence tools:

```text
src/mpm_lbm/evidence/code_layout_audit.py
src/mpm_lbm/evidence/import_boundary_audit.py
src/mpm_lbm/evidence/compatibility_shim_audit.py
```

Runners:

```text
baseline_tests/step55_common.py
baseline_tests/run_step55_code_layout_audit.py
baseline_tests/run_step55_import_boundary_audit.py
baseline_tests/run_step55_compatibility_shim_audit.py
baseline_tests/run_step55_test_strength_enum_audit.py
baseline_tests/run_step55_step54_regression_guard.py
baseline_tests/run_step55_artifact_manifest.py
```

Tests:

```text
tests/test_step55_repository_code_layout_contract.py
tests/test_step55_import_boundary_contract.py
tests/test_step55_compatibility_shim_contract.py
tests/test_step55_test_strength_enum_contract.py
```

## Code Layout Policy Requirements

The code layout audit must produce:

```text
outputs/step55_code_layout_audit/code_layout_audit.csv
outputs/step55_code_layout_audit/code_layout_audit_summary.csv
outputs/step55_code_layout_audit/code_layout_audit.json
logs/step55_code_layout_audit.log
```

The audit must check:

- `src/mpm_lbm/sim` exists.
- `src/mpm_lbm/diagnostics` exists.
- `src/mpm_lbm/evidence` exists.
- `experiments/steps` exists.
- Runtime canonical modules exist under `src/mpm_lbm/sim`.
- Evidence canonical modules exist under `src/mpm_lbm/evidence`.
- Step-specific package directories exist under `experiments/steps`.
- Root-level `src/*.py` files are classified by explicit policy.
- No unclassified root-level `src/*.py` files are allowed.
- New Step55 evidence code is under `src/mpm_lbm/evidence`, not root `src/`.

The audit summary must include:

```text
code_layout_audit_pass
canonical_sim_package_exists
canonical_diagnostics_package_exists
canonical_evidence_package_exists
experiments_steps_package_exists
root_src_file_count
unclassified_root_src_file_count
step55_new_root_evidence_file_count
```

## Import Boundary Policy Requirements

The import boundary audit must produce:

```text
outputs/step55_import_boundary_audit/import_boundary_audit.csv
outputs/step55_import_boundary_audit/import_boundary_audit_summary.csv
outputs/step55_import_boundary_audit/import_boundary_audit.json
logs/step55_import_boundary_audit.log
```

The audit must check:

- `src/mpm_lbm/sim` must not import `experiments`.
- `src/mpm_lbm/sim` must not import `baseline_tests`.
- `src/mpm_lbm/sim` must not import `tests`.
- `src/mpm_lbm/sim` must not import `outputs`.
- `src/mpm_lbm/sim` must not import `logs`.
- `src/mpm_lbm/sim` must not import `docs`.
- `src/mpm_lbm/sim` must not contain Step 50/51/52/53/54 implementation constants.
- `experiments/steps` may import `src.mpm_lbm.sim`.
- `experiments/steps` may import `src.mpm_lbm.diagnostics`.
- `experiments/steps` may import `src.mpm_lbm.evidence`.
- `baseline_tests` may import `src.mpm_lbm` and `experiments`.
- `tests` may inspect `src.mpm_lbm` and `experiments`.

The audit summary must include:

```text
import_boundary_audit_pass
sim_forbidden_import_count
sim_step_constant_count
scanned_sim_file_count
```

## Compatibility Shim Policy Requirements

The compatibility shim audit must produce:

```text
outputs/step55_compatibility_shim_audit/compatibility_shim_audit.csv
outputs/step55_compatibility_shim_audit/compatibility_shim_audit_summary.csv
outputs/step55_compatibility_shim_audit/compatibility_shim_audit.json
logs/step55_compatibility_shim_audit.log
```

It must verify old and new surfaces without requiring optional heavy dependencies in the hook environment:

- old source path exists,
- new canonical source path exists,
- expected symbol text exists in old source,
- expected symbol text or lazy-export text exists in new source,
- root compatibility remains documented,
- canonical destination is recorded.

Required compatibility surfaces:

```text
src.lbm_fluid.LBMFluid3D -> src.mpm_lbm.sim.lbm.fluid.LBMFluid3D
src.lbm_config.LBMConfig -> src.mpm_lbm.sim.lbm.config.LBMConfig
src.fsi_driver.FSIDriver3D -> src.mpm_lbm.sim.drivers.fsi_driver.FSIDriver3D
src.fsi_config.FSIDriverConfig -> src.mpm_lbm.sim.drivers.fsi_config.FSIDriverConfig
src.projection.MPMToLBMProjector3D -> src.mpm_lbm.sim.coupling.projection.MPMToLBMProjector3D
src.repository_evidence_index.build_repository_evidence_index -> src.mpm_lbm.evidence.repository_evidence_index.build_repository_evidence_index
src.repository_test_strength_audit.build_repository_test_strength_audit -> src.mpm_lbm.evidence.repository_test_strength_audit.build_repository_test_strength_audit
src.runtime_geometry_wall_velocity_one_cycle_envelope.run_one_cycle_envelope_matrix -> experiments.steps.step50_one_cycle_proxy.envelope.run_one_cycle_envelope_matrix
src.runtime_geometry_wall_velocity_transfer_envelope.run_transfer_comparison_matrix -> experiments.steps.step51_transfer_comparison_proxy.envelope.run_transfer_comparison_matrix
src.runtime_geometry_wall_velocity_48_feasibility_envelope.run_48_feasibility_matrix -> experiments.steps.step52_48_feasibility_proxy.envelope.run_48_feasibility_matrix
```

## Step 54 Test Strength Enum Repair

The allowed test strength enum must be:

```text
artifact_contract
artifact_plus_source_contract
runner_reexecution_contract
proxy_diagnostic_contract
solver_smoke_contract
formula_unit_contract
numerical_benchmark_contract
```

`src/repository_test_strength_audit.py` and the canonical evidence copy under `src/mpm_lbm/evidence/` must return only these values.

The Step55 enum audit must produce:

```text
outputs/step55_test_strength_enum_audit/test_strength_enum_audit.csv
outputs/step55_test_strength_enum_audit/test_strength_enum_audit_summary.csv
outputs/step55_test_strength_enum_audit/test_strength_enum_audit.json
logs/step55_test_strength_enum_audit.log
```

The audit must fail if any `test_strength_level` is outside policy.

## Step 54 Pytest Count Wording Repair

Remove stale hard-coded text like:

```text
604/614 passed means contract/artifact/proxy tests passed unless explicitly classified otherwise.
```

Use this durable wording instead:

```text
A passing full pytest run means contract/artifact/proxy/solver-smoke tests passed according to the test strength audit classification.
```

Do not hard-code `624 passed` in long-lived reports/docs/tests because the number changes when tests are added.

## Step 54 Regression Guard

Step55 must include a Step54 regression guard that checks:

- Step54 LBM relaxation semantics audit still passes.
- Step54 proxy truthfulness audit still passes.
- Step54 state guard truthfulness audit still passes.
- Step54 repository evidence index still passes.
- Step54 claim guard still passes.
- Step54 artifact manifest still passes.
- Step54 docs/report no longer contain stale hard-coded pytest pass-count wording.
- Step54 test strength audit uses only the Step55 policy enum after regeneration.

## Artifact Manifest Requirements

Step55 artifact manifest must prove:

- no large Step55 files,
- no VTR files,
- no particle NPY files,
- no dense/displaced geometry outputs,
- no edits under `external/taichi_LBM3D`,
- no edits under `data/real_geometry_candidates`,
- Step55 output size remains small,
- generated logs are included.

## Required Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\code_layout_audit.py `
  src\mpm_lbm\evidence\import_boundary_audit.py `
  src\mpm_lbm\evidence\compatibility_shim_audit.py `
  baseline_tests\step55_common.py `
  baseline_tests\run_step55_code_layout_audit.py `
  baseline_tests\run_step55_import_boundary_audit.py `
  baseline_tests\run_step55_compatibility_shim_audit.py `
  baseline_tests\run_step55_test_strength_enum_audit.py `
  baseline_tests\run_step55_step54_regression_guard.py `
  baseline_tests\run_step55_artifact_manifest.py `
  tests\test_step55_repository_code_layout_contract.py `
  tests\test_step55_import_boundary_contract.py `
  tests\test_step55_compatibility_shim_contract.py `
  tests\test_step55_test_strength_enum_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step55_code_layout_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step55_import_boundary_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step55_compatibility_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step55_test_strength_enum_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step55_step54_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step55_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step55_repository_code_layout_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step55_import_boundary_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step55_compatibility_shim_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step55_test_strength_enum_contract.py -q

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The final push must let the ECC pre-push hook run and pass.

## Acceptance Criteria

Step 55 is accepted only when all of the following are true:

- detailed Step55 goal exists,
- short active goal references this file,
- Step55 report/docs exist,
- code layout policy exists,
- import boundary policy exists,
- compatibility shim policy exists,
- test strength enum policy exists,
- `src/mpm_lbm/sim` package exists,
- `src/mpm_lbm/diagnostics` package exists,
- `src/mpm_lbm/evidence` package exists,
- `experiments/steps` package exists,
- required canonical runtime/evidence/step package surfaces exist,
- root-level `src/*.py` files are classified and no new unclassified root mixed-purpose files appear,
- old import/source paths remain compatible,
- new canonical source paths exist,
- import boundary audit passes,
- code layout audit passes,
- compatibility shim audit passes,
- test strength enum audit passes,
- Step54 regression guard passes,
- stale hard-coded pytest count wording is removed from long-lived docs/tests,
- Step55 artifact manifest passes,
- `external/taichi_LBM3D` is unchanged,
- `data/real_geometry_candidates` is unchanged,
- `git diff --check` passes,
- full pytest passes under `D:\working\taichi\env\python.exe`,
- full pytest passes under `D:\TOOL\Anaconda\python.exe`,
- pre-push hook passes,
- final commit is pushed to `origin/main`.

## Commit Message

Use:

```text
test: add step55 repository code layout separation
```
