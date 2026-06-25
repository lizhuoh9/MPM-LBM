# Step117 Regularized LBM Long-Window Fluid Validation

Step117 runs the Step116 LBM-only duct/static-flap evidence as real
long-window rows instead of bounded 8 x 6 x 6 probes.

The output directory is:

`outputs/step117_regularized_lbm_long_window_fluid_validation/`

Step117 remains fluid-only. It does not run MPM, full FSI, Fluent, official
mesh/case import, quasi-2D flow, conservative traction transfer, or a
small-strain solid path.

## Runner

Use:

```powershell
& 'D:\working\taichi\env\python.exe' `
  experiments\steps\step117_regularized_lbm_long_window_fluid_validation.py `
  --row duct_only_48_regularized_boundary_500step_full `
  --force `
  --output-interval 50
```

The runner supports row-level resume, `--max-rows`, `--profile-only`, and
`--no-large-arrays`. This keeps expensive rows separable and avoids committing
dense 96^3 field dumps.

## Result Summary

- The 48^3 legacy 500-step duct-only row completed and passed density/mass
  gates.
- The 48^3 regularized 500-step duct-only row completed and passed
  density/mass gates, but it was worse than legacy by final mass drift and
  flux imbalance.
- The 96^3 regularized 1000-step duct-only row completed the step count but
  failed density and mass gates after severe late-window growth.
- The 96^3 static two-flap 1000-step row completed the step count but failed
  density and mass gates after severe late-window growth.
- The physical-nu official-like row is strict tau-gated and skipped before
  stepping.

## Step118 Decision

Step118 quasi-2D is blocked. The next step should repair LBM boundary/stability
behavior and rerun long-window fluid validation before adding quasi-2D,
conservative traction, small-strain solid behavior, or full FSI.
