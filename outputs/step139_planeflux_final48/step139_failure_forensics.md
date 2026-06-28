# Step139 Failure Forensics

Step139 completed the requested 48^3 / 500-step window and stayed finite, but failed the final hard gate.

First failed gate: `candidate_mass_acceptance_gate_pass`.

Failed gates:

- `candidate_mass_acceptance_gate_pass`
- `flow_development_gate_pass`
- `flux_imbalance_rel_tail_mean`
- `outlet_flux_tail_cv`

Final 500-step metrics:

- `candidate_mass_acceptance_observed_abs = 0.008321150189010917`
- `flux_imbalance_rel_tail_mean = 0.10270018561574665`
- `flux_imbalance_rel_tail_max = 0.16810119026843742`
- `outlet_flux_tail_cv = 0.11556697847525366`
- `collapse_first_x = None`
- `collapse_first_step = None`

No selected boundary, selected96, selected-static, 96^3, FSI validation, Fluent validation, or Figure 29.3 parity claim is allowed.

Suggested next diagnostic: Analyze long-window mass drift and outlet stationarity around steps 250-500 without changing Step139 parameters and without running selected96.
