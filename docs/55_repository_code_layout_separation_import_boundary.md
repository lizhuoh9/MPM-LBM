# Step 55 Repository Code Layout Separation And Import Boundary

Step 55 establishes package boundaries for the repository without changing solver behavior.

The new canonical structure starts at `src/mpm_lbm`:

- `src/mpm_lbm/sim` for runtime simulation surfaces.
- `src/mpm_lbm/diagnostics` for reusable diagnostic surfaces.
- `src/mpm_lbm/evidence` for repository evidence and audit tools.
- `experiments/steps` for step-specific proxy and audit surfaces.

The initial migration is copy-first and compatibility-safe. Legacy root `src/*.py` modules remain available while audits make new mixed-purpose root files visible.

Step 55 also repairs the Step 54 test-strength enum and removes stale hard-coded pytest pass-count wording from long-lived Step 54 report/config/test surfaces.

Step 55 does not add physics capability, run new physical cases, migrate tau formulas, or modify protected external or real-geometry candidate directories.
