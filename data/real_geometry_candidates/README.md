# Controlled Real Geometry Candidate Intake

This directory is for local Step 25 candidate geometry descriptors and local-only raw candidate files.

Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Step 25 does not implement squid swimming.
Step 25 does not implement squid actuation.
Step 25 does not implement new FSI physics.
Step 25 does not validate production sharp-interface FSI.

Policy:

- Do not commit large raw real geometry files.
- Do not commit scan data.
- Do not commit private anatomy, proprietary CAD, or private absolute paths.
- Commit descriptors only when they use repo-relative smoke fixtures or redacted local paths.
- A passing intake report is not swimming validation.
- Candidate intake does not perform production mesh repair or automatic remeshing.
- Raw large real geometry files and scan data are not committed.

The `.gitignore` keeps local candidate payloads out of git while allowing this README, `.gitkeep`, and descriptor files.
