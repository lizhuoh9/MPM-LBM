# Roadmap

The next steps should preserve the existing regression baselines and mode matrix before adding new physics.

## Current Status

Step 12 is completed as the performance and memory cleanup stage once `STEP12_PERFORMANCE_MEMORY_REPORT.md` is accepted. The next implementation step is Step 13: geometry ingestion / squid proxy geometry.

## Proposed Steps

| step | focus | boundary |
| ---- | ----- | -------- |
| Step 12 | completed: performance and memory cleanup | preserve Step 10 mode matrix |
| Step 13 | geometry ingestion / squid proxy geometry | do not claim real squid validation until baselines pass |
| Step 14 | larger-grid validation | expand stability evidence beyond 32^3 |
| Step 15 | moving-boundary reaction calibration and sharper momentum accounting | keep engineering-scale MVP path available for comparison |
| Step 16 | optional two-phase LBM exploration | keep single-phase baseline intact |

## Regression Rule

Every future step should keep these checks available:

```text
pytest -q
Step 10 penalty driver baseline
Step 10 moving_boundary driver baseline
Step 10 mode matrix baseline
Step 10 performance profile baseline
```

New physics should be added behind explicit modes or new configs, not by silently changing validated behavior.
