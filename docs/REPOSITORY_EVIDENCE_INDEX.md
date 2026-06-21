# Repository Evidence Index

This document summarizes the Step 54 evidence-index policy. The generated index is `outputs/step54_repository_evidence_index/repository_evidence_index.json`.

## Required Classifications

- Step 1 and Step 2 are solver smoke baselines.
- Step 50, Step 51, and Step 52 are proxy diagnostics. Their generated records must use `record_kind = proxy_diagnostic_record` and `solver_time_integration_run = false`.
- Step 53 is a post-processing audit over accepted Step 51 and Step 52 artifacts.
- Step 54 is an evidence integrity repair.

## Claim Boundary

Proxy diagnostics, post-processing audits, and repository evidence repairs must not be described as real-jet validation, jet-propulsion validation, squid swimming, grid convergence, production readiness, full solver validation, or standard-viscosity validation.
