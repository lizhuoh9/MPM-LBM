# Repository Code Layout Policy

Step 55 defines these boundaries:

## Runtime

Runtime simulation surfaces belong under `src/mpm_lbm/sim`. The runtime package must not import experiments, baseline tests, tests, outputs, logs, or docs. Runtime package files must not contain Step 50/51/52/53/54 implementation constants.

## Diagnostics

Reusable diagnostic surfaces belong under `src/mpm_lbm/diagnostics`.

## Evidence

Repository evidence and audit tools belong under `src/mpm_lbm/evidence`.

## Step-Specific Code

Step-specific proxy and audit wrappers belong under `experiments/steps`.

## Legacy Root Source

Root `src/*.py` remains a compatibility and approved legacy surface during the copy-first migration. The code layout audit classifies each root file. New unclassified root files are not allowed.
