# Step125 LBM Boundary Campaign Provenance Identity Report

## Summary

Step125 is a provenance-only patch before real 48^3 campaign execution.

It separates the original campaign base commit from the current code commit in
current campaign metadata and upgrades the Step121 manifest writer so future
phase runs record the code commit used for each phase.

No solver physics, LBM boundary formulas, gate thresholds, 48^3 rows, 96^3
rows, quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3
parity claim is changed by this step.

## Red Test Evidence

Before implementation, the new Step125 regression file failed as expected:

```text
3 failed in 1.33s
```

The failures were:

- `ACTIVE_CAMPAIGN.json` had no `campaign_base_commit`.
- `write_step121_campaign_manifest()` had no `campaign_base_commit` argument.
- Step120 finite summary rows had no `code_commit_at_run`.

## Changes

Implemented changes:

- `docs/current/ACTIVE_CAMPAIGN.json` now records:
  - `campaign_base_commit = 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc`
  - `base_commit = 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc`
  - `current_code_commit = 26d4d0a9597a440272e2d479decbf1fbf95cb2ff`
- Step121 campaign manifests are now schema version 2.
- Newly written Step121 manifests record `campaign_base_commit`,
  `current_code_commit`, compatibility `git_commit`, legacy `phase_history`,
  and structured `phase_commit_history`.
- The committed Step121 manifest was upgraded to schema version 2 without
  adding any new physical run claim.
- Step120 finite summary rows and row metadata now record
  `code_commit_at_run`.
- Current campaign reading docs now point to Step125 goal/report.

## Verification

Step125 single-file regression:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step125_campaign_provenance_identity_contract.py
```

Result:

```text
3 passed in 1.96s
```

Focused Step123-Step125 campaign contracts were first run without a repo-local
pytest temp directory. That exposed a local Windows temp permission problem:

```text
PermissionError: [WinError 5] Access denied: 'D:\User_Temp\lizhu\pytest-of-lizhu'
17 passed, 4 warnings, 5 errors in 89.33s
```

The same focused suite passed when pytest temp files were forced into the repo:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step125-focused `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
22 passed, 8 warnings in 141.33s
```

Changed Python files compiled:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py
```

Result: pass.

## Remaining Physical Work

Step125 does not run real 48^3 or 96^3 rows. The next physical campaign action
is still:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase references48 `
  --allow-large-real-rows `
  --output-interval 25
```

After references complete, run `--phase summary` and advance to candidates only
if the legacy 48^3 reference row passes the required gates.
