# Repository Evidence Integrity Errata

Step 54 records these repository-wide evidence errata.

## LBM Relaxation Parameter

The existing LBM `niu` field follows the legacy external solver parameter formula `tau = niu / 3.0 + 0.5`. Step 54 names this helper explicitly and also provides the standard lattice kinematic viscosity helper `tau = 3.0 * nu_lbm + 0.5`. Step 54 does not migrate defaults and does not claim standard-viscosity validation.

## Proxy Diagnostic Rows

Step 50, Step 51, and Step 52 rows use proxy formulas and config-declared step counts. They are not driver time-integration records. Step 54 adds explicit metadata fields to the generated row and per-step records.

## State Guard Fixed-Zero Fields

Step 50, Step 51, and Step 52 state guard summaries had fixed-zero default mutation counts. Step 54 discloses the method: default driver/LBM/MPM/projection mutation counts are not applicable because these proxy runs do not instantiate those default solver objects; persistent output counts remain config and artifact guard checks.

## Test Strength

Repository tests can check file existence, log markers, report text, committed JSON artifacts, source strings, runner re-execution, solver execution, formulas, or numerical benchmarks. Step 54 classifies those checks so test-suite pass counts are not overread.
