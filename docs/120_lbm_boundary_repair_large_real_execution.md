# Step 120 LBM Boundary Repair Large Real Execution

Step120 repairs the Step119 real-run boundary workflow before any quasi-2D,
FSI, Fluent validation, or Figure 29.3 parity work is allowed.

## Scope

Step120 is LBM-only. It does not run a dynamic flap FSI case and does not claim
Fluent parity.

The committed matrix includes:

- one tiny real LBM runner smoke row;
- incomplete 48^3 real boundary target rows that require explicit operator
  authorization;
- one expected physical-nu strict tau-margin policy skip;
- gate reports that keep Step121 quasi-2D blocked.

## Runner

Main entrypoint:

`experiments/steps/step120_lbm_boundary_repair_large_real_execution.py`

Default output:

`outputs/step120_lbm_boundary_repair_large_real_execution/`

Runtime checkpoints:

`outputs/tmp/step120_checkpoints/`

Important flags:

- `--row`
- `--force`
- `--resume` / `--no-resume`
- `--output-interval`
- `--checkpoint-every`
- `--max-wall-seconds`
- `--allow-large-real-rows`

Large real rows are not run unless `--allow-large-real-rows` is explicitly
passed.

## Artifacts

Top-level files:

- `solver_report.json`
- `run_matrix_summary.json`
- `row_status_summary.json`
- `boundary_variant_48_comparison.json`
- `best_boundary_selection.json`
- `boundary_variant_96_validation.json`
- `first_failure_global_summary.json`
- `limiter_actual_activation_summary.json`
- `step120_gate_report.json`
- `README.md`

Each row writes:

- `run_metadata.json`
- `driver_config.json`
- `duct_boundary_condition_report.json`
- `finite_stability_report.json`
- `first_failure_diagnostics.json`
- `limiter_activation_summary.json`
- `velocity_profile_summary.json`
- `fluid_diagnostics_timeseries.csv`
- `density_drift_timeseries.csv`
- `boundary_flux_timeseries.csv`
- `stability_diagnostics_timeseries.csv`

## Gate Rules

Step120 first compares completed 48^3 candidates against completed 48^3
reference rows. If no 48^3 candidate passes, the campaign stops at 48^3 with
`boundary_repair_failed_revisit_lbm_solver`.

If a 48^3 candidate passes, Step120 selects one best boundary variant and then
requires only these selected rows:

- `duct_only_96_<selected_boundary_slug>_1000step_real`
- `static_two_flap_96_<selected_boundary_slug>_1000step_real`

Only when both selected rows complete and pass does Step120 allow Step121
quasi-2D.

## Current Status

Current committed status:

`boundary_repair_failed_revisit_lbm_solver`

The default committed output has one completed tiny smoke row, four incomplete
large-row placeholders, and one expected tau-margin policy skip. The next work
is to run the 48^3 rows one at a time with `--allow-large-real-rows`, then let
Step120's best-boundary selection decide whether any 96^3 row is justified.
