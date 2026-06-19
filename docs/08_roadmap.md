# Roadmap

The next steps should preserve the existing regression baselines and mode matrix before adding new physics.

## Current Status

Step 15 is completed as the moving-boundary calibration and momentum-accounting stage once `STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md` is accepted. The next implementation step is Step 16: long-run validation and 64^3 moving_boundary feasibility.

## Proposed Steps

| step | focus | boundary |
| ---- | ----- | -------- |
| Step 12 | completed: performance and memory cleanup | preserve Step 10 mode matrix |
| Step 13 | completed: geometry ingestion / squid proxy geometry | squid_proxy is procedural and not real squid validation |
| Step 14 | completed: larger-grid validation | 48^3 engineering scale baseline and 64^3 feasibility checks |
| Step 15 | completed: moving-boundary reaction calibration and sharper momentum accounting | keep engineering-scale MVP path available for comparison |
| Step 16 | long-run validation and 64^3 moving_boundary feasibility | preserve Step 10 mode matrix, Step 13 geometry contracts, and Step 14 scale baselines |

## Regression Rule

Every future step should keep these checks available:

```text
pytest -q
Step 10 penalty driver baseline
Step 10 moving_boundary driver baseline
Step 10 mode matrix baseline
Step 10 performance profile baseline
Step 12 resource and artifact checks
Step 13 geometry ingestion contracts
Step 14 larger-grid validation contracts
Step 15 moving-boundary calibration contracts
```

New physics should be added behind explicit modes or new configs, not by silently changing validated behavior.
