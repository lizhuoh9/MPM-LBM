# Limitations

Current implementation limitations:

1. single-phase fluid only
2. no two-phase surface tension/contact angle physics
3. no real squid geometry
4. dense grid only
5. moving-boundary reaction uses engineering scale
6. not strict final momentum-conserving sharp-interface FSI
7. small-scale validation only: n_grid = 32, n_particles = 4096
8. diagnostics often copy data to NumPy and are not production performance paths
9. committed logs/outputs are for reproducibility and may be large

## Coupling Scope

The penalty mode is a diffuse-interface MVP. The moving_boundary mode is a sharper-interface MVP based on opt-in moving bounce-back and engineering-scale reaction transfer.

Neither mode should be described as final strict momentum-conserving sharp-interface FSI.

## Geometry Scope

There is no real squid geometry in the current validation package. Any future squid case should be introduced as a separate geometry-ingestion and validation step.

## Validation Scope

The accepted baselines are short, small-scale engineering runs. They are adequate for regression checks and documentation, but they are not full physical validation.
