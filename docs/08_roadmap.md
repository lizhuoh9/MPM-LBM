# Roadmap

The next steps should preserve the existing regression baselines and mode matrix before adding new physics.

## Current Status

Step 17 is completed as the diagnostic-only direction-wise and link-area proxy accounting stage once `STEP17_LINK_AREA_ACCOUNTING_REPORT.md` is accepted. The next implementation step should preserve this baseline before adding any opt-in experimental link-area reaction transfer.

## Proposed Steps

| step | focus | boundary |
| ---- | ----- | -------- |
| Step 12 | completed: performance and memory cleanup | preserve Step 10 mode matrix |
| Step 13 | completed: geometry ingestion / squid proxy geometry | squid_proxy is procedural and not real squid validation |
| Step 14 | completed: larger-grid validation | 48^3 engineering scale baseline and 64^3 feasibility checks |
| Step 15 | completed: moving-boundary reaction calibration and sharper momentum accounting | keep engineering-scale MVP path available for comparison |
| Step 16 | completed: long-run validation and 64^3 moving_boundary feasibility | preserve Step 10 mode matrix, Step 13 geometry contracts, and Step 14 scale baselines |
| Step 17 | completed: diagnostic-only direction-wise and link-area proxy accounting | no new FSI mode and no solver physics change |
| Step 18 | proposed: experimental link-area reaction transfer mode | opt-in only; do not replace the engineering-scale moving_boundary path |
| Future | stricter sharp-interface momentum accounting and real geometry ingestion | Strict link-area momentum-conserving coupling remains future work. |

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
Step 16 long-run validation contracts
Step 17 link-area momentum accounting contracts
```

New physics should be added behind explicit modes or new configs, not by silently changing validated behavior.

Step 16 does not add new FSI physics. The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation.

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction.
