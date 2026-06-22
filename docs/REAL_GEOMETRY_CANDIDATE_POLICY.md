# Real Geometry Candidate Policy

Step74 keeps `data/real_geometry_candidates` protected. No new real geometry
candidate data, raw scan files, VTR files, particle NPY files, or large geometry
files are added by this step.

Candidate descriptors must use the controlled validation scope:

```text
intake_qa_normalization_sampling_projection_only
```

Descriptors must not imply validation, swimming, actuation, anatomy, production
readiness, or real squid behavior. Private or local-only source paths must not
be committed in manifest outputs, and unavailable sources must be marked with a
local-only or do-not-commit policy.

Step74 uses only a tiny synthetic text fixture under
`outputs/step74_synthetic_geometry_fixture/` to exercise manifest boundaries.
That fixture is not real geometry candidate data.
