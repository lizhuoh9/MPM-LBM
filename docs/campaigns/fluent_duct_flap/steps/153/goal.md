# Step153 Goal: Official Fluent Monitor Extraction and Normalization

## Source Contract

Step153 follows `origin/main = 123c50258f689ef5f34525a65045df878f621190`.
Step152 is correct but currently blocked: it refuses solver runtime patches
because Step151 has no `targeted_fix_plan_ready`, and Step151 has no plan
because Step150 has no real official monitor comparison.

The current missing private input is:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

This checkout also has no local `benchmarks/private/fluent_fsi_2way/outputs`
directory and no raw Fluent/System Coupling monitor export. Therefore Step153
must not fabricate official data and must not claim Step150 readiness in the
current local no-input state.

## Objective

Add Step153 as an executable official monitor extractor/normalizer. Step153 is
not a blocked gate, not a solver patch, and not another Step152-style apply
gate. Its useful purpose is to convert a user-supplied private official monitor
export into the exact private CSV consumed by Step150:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

Step153 must support synthetic contract tests that prove a raw monitor export
can become a Step150-ready private official monitor. In the current checkout,
where no private raw export is present, Step153 must write honest metadata
artifacts with `ready_for_step150 = false` and `official_monitor_written_private
= false`.

## Accepted Inputs

The runner must accept a path supplied with `--input`. Supported sources are
local private exports only, for example:

```text
benchmarks/private/fluent_fsi_2way/outputs/raw_monitor_export.txt
benchmarks/private/fluent_fsi_2way/outputs/system_coupling_monitor.csv
benchmarks/private/fluent_fsi_2way/outputs/fluent_monitor_report.dat
```

Supported text shapes:

```text
CSV with headers
tab-delimited text with headers
whitespace-delimited text with headers
simple Ansys/Fluent monitor table exports copied to text
```

Step153 must tolerate common column labels and normalize them to Step150's
required schema.

## Required Normalized Output

The private output path defaults to:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

Required output columns:

```text
time_s
flap_tip_total_displacement_m
```

Optional normalized columns, if source data contains them:

```text
step
flap_tip_x_displacement_m
flap_tip_y_displacement_m
flap_tip_velocity_m_per_s
fluid_force_x_n
fluid_force_y_n
fluid_force_magnitude_n
```

Step153 must preserve monotonic time order, reject non-finite numeric values,
and reject files without a usable displacement column.

## Column Alias Contract

At minimum, Step153 must map these aliases:

```text
time_s <- time_s, time, Time, flow-time, flow_time_s, Flow Time
flap_tip_total_displacement_m <- flap_tip_total_displacement_m, total_displacement, Total Displacement, displacement, disp, monitor_displacement_m
flap_tip_x_displacement_m <- flap_tip_x_displacement_m, x_displacement, X Displacement, disp_x
flap_tip_y_displacement_m <- flap_tip_y_displacement_m, y_displacement, Y Displacement, disp_y
fluid_force_magnitude_n <- fluid_force_magnitude_n, force_magnitude, Force Magnitude, force, fluid_force
fluid_force_x_n <- fluid_force_x_n, force_x, X Force
fluid_force_y_n <- fluid_force_y_n, force_y, Y Force
step <- step, Step, timestep, time_step
```

## Committed Step153 Artifacts

Step153 must never commit the official monitor CSV body. It may commit only
metadata under:

```text
outputs/step153_official_monitor_extract/
  official_monitor_extraction_summary.json
  official_monitor_schema_preview.json
  official_monitor_hash_report.json
  report.md
```

If a private source is available and conversion succeeds, the summary must
include:

```json
{
  "status": "official_monitor_ready_for_step150",
  "official_monitor_written_private": true,
  "official_monitor_path": "benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv",
  "official_monitor_committed": false,
  "columns": ["time_s", "flap_tip_total_displacement_m"],
  "row_count": 1,
  "time_start_s": 0.0,
  "time_end_s": 0.0,
  "ready_for_step150": true
}
```

If no source is available in the current checkout, the summary must include:

```json
{
  "status": "waiting_for_official_monitor_source",
  "official_monitor_written_private": false,
  "official_monitor_committed": false,
  "ready_for_step150": false,
  "next_action": "export_fluent_or_system_coupling_monitor"
}
```

## Runner Command

Default no-input/current-state command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step153_official_monitor_extract_and_normalize `
  --input benchmarks\private\fluent_fsi_2way\outputs\raw_monitor_export.txt `
  --output benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --output-dir outputs\step153_official_monitor_extract `
  --force
```

When a private raw export is available, the same command must write the private
official monitor and produce `ready_for_step150 = true`.

## Step150 Follow-Up Contract

After Step153 reports `ready_for_step150 = true`, the next command is:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step150_official_monitor_intake_and_error_localization `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --solver-monitor outputs\step148_our_solver_fluent_official_case\solver_monitor.csv `
  --solver-force-monitor outputs\step148_our_solver_fluent_official_case\solver_force_monitor.csv `
  --solver-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --output-dir outputs\step150_official_monitor_error_localization `
  --force
```

Step153 itself must not claim Step150 error localization unless Step150 is
actually rerun and produces `error_localization_complete`.

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/153/goal.md
docs/campaigns/fluent_duct_flap/steps/153/report.md
experiments/steps/step153_official_monitor_extract_and_normalize.py
tests/test_step153_official_monitor_extract_and_normalize_contract.py
```

Generate:

```text
outputs/step153_official_monitor_extract/official_monitor_extraction_summary.json
outputs/step153_official_monitor_extract/official_monitor_schema_preview.json
outputs/step153_official_monitor_extract/official_monitor_hash_report.json
outputs/step153_official_monitor_extract/report.md
```

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
README.md
```

## Contract Tests

Add `tests/test_step153_official_monitor_extract_and_normalize_contract.py`
covering:

1. Missing private source writes `waiting_for_official_monitor_source` and does
   not create `official_monitor.csv`.
2. CSV input with canonical Step150 columns writes a private official monitor
   and reports `ready_for_step150 = true`.
3. Tab-delimited Ansys-style headers are normalized to `time_s` and
   `flap_tip_total_displacement_m`.
4. Space-delimited copied table headers are normalized.
5. Optional force and component displacement columns are preserved when
   available.
6. Non-monotonic time is rejected and no ready claim is made.
7. Missing displacement column is rejected and no ready claim is made.
8. Output artifacts never include private row bodies; only preview metadata may
   include column names and row/time counts.
9. `official_monitor_committed = false` for private outputs in test fixtures.
10. All paths preserve `validation_claim_allowed = false` and
    `selected96_execution_allowed = false`.

Tests must be lightweight and use temporary files only. They must not require
real Fluent, private official data, selected96, or long solver jobs.

## Prohibited Actions

Do not:

```text
write another blocked gate as the main feature
modify solver runtime code
modify MPM/LBM/FSI formulas
run selected96
claim Fluent validation, Figure 29.3 parity, or production readiness
commit benchmarks/private files
commit official_monitor.csv or raw private Fluent exports
fabricate official monitor samples from solver outputs
fake Step150 error localization
fake Step151 targeted fix plan
fake solver patch readiness
```

## Done Criteria

Step153 is complete for the current checkout when:

- The detailed goal file exists and the active goal references it.
- The extractor runner and contract tests exist.
- Synthetic private raw exports convert to a Step150-ready private
  `official_monitor.csv` in test temp directories.
- Current no-private-input artifacts honestly report
  `waiting_for_official_monitor_source` and `ready_for_step150 = false`.
- No `benchmarks/private` payload is staged or committed.
- No solver runtime files are modified.
- Current docs point to Step153 as the active path for obtaining the missing
  official monitor source, without claiming validation.
- Focused Step150/151/152/153 tests pass with
  `D:\working\taichi\env\python.exe`.
- JSON and `git diff --check` verification pass.
- Changes are committed, pushed to `origin/main`, and codebase-memory is
  refreshed.
