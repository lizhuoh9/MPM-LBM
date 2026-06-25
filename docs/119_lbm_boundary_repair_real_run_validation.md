# Step 119 LBM Boundary Repair Real-Run Validation

Step119 turns the Step118 boundary repair surface into a real-run validation
workflow. It still does not open quasi-2D, FSI, Fluent validation, or Figure
29.3 parity.

## Scope

Step119 is LBM-only. The committed artifacts use
`synthetic_diagnostic_mode=false`.

The committed matrix includes:

- one tiny real LBM runner smoke row;
- incomplete real 48^3 and 96^3 target rows;
- explicit gate reports that keep Step119 quasi-2D remains blocked.

No Fluent validation is claimed. No full FSI validation is claimed.

## Runner

Main entrypoint:

`experiments/steps/step119_lbm_boundary_repair_real_run_validation.py`

Default output:

`outputs/step119_lbm_boundary_repair_real_run_validation/`

Important flags:

- `--row`
- `--force`
- `--resume` / `--no-resume`
- `--output-interval`
- `--stop-on-first-failure`
- `--no-stop-on-first-failure`
- `--checkpoint-every`
- `--max-wall-seconds`
- `--allow-large-real-rows`

Large real rows are not run unless `--allow-large-real-rows` is explicitly
passed. This prevents 48^3/96^3 long-window execution from being hidden inside
pytest or a default artifact refresh.

## Artifacts

Top-level files:

- `solver_report.json`
- `run_matrix_summary.json`
- `boundary_variant_real_run_comparison.json`
- `first_failure_global_summary.json`
- `limiter_activation_summary.json`
- `step119_gate_report.json`
- `README.md`

Each row writes:

- `run_metadata.json`
- `driver_config.json`
- `duct_boundary_condition_report.json`
- `finite_stability_report.json`
- `first_failure_diagnostics.json`
- `limiter_activation_summary.json`
- `fluid_diagnostics_timeseries.csv`
- `density_drift_timeseries.csv`
- `boundary_flux_timeseries.csv`
- `stability_diagnostics_timeseries.csv`

Static two-flap rows also write:

- `flap_region_flow_summary.json`
- `throat_speed_summary.json`
- `recirculation_proxy_summary.json`

## Gate Rules

`step120_quasi2d_allowed` remains false unless all required real validation
rows complete and pass:

- 48^3 legacy reference;
- 48^3 old regularized reference;
- 48^3 limited repair row;
- 48^3 convective repair row;
- 96^3 limited duct-only row;
- 96^3 convective duct-only row;
- 96^3 static two-flap best-boundary row.

High limiter activation blocks validation. A limiter-stabilized row is reported
as numerically bounded, not physically validated.

## Current Status

Current committed status:

`boundary_repair_partial_continue_lbm`

The next work is to run real 48^3 rows one at a time with
`--allow-large-real-rows`, compare limited/convective against legacy and old
regularized behavior, then decide whether the 96^3 phase is justified.
