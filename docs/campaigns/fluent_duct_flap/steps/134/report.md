# Step134 Outlet Tail-Collapse Diagnosis Report

## Decision

Step134 produced bounded real 48^3 / 250-step LBM-only triage evidence for
`planeflux_stationarity48`. The code surface and artifacts are valid, but no
row passed the promotion gates.

Final Step134 state:

- `accepted_row_count = 0`
- No 500-step Step134 promotion was run.
- No selected 96^3 run is allowed.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.

The evidence supports continuing the 48^3 boundary-repair loop. It does not
support selecting a boundary.

## Baseline

Step134 starts from Step133, where all six `planeflux_mass_damped48` rows
completed 250/250 with finite state and no first-failure event, but every row
failed the relaxed promotion gate.

The best Step133 regularized mass row was:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p0005_alpha0p02_du0p0005_slew0p50_250step_triage
candidate_mass_acceptance_observed_abs = 0.014184975814691638
flux_imbalance_rel_tail_mean = 0.3987696128026395
outlet_to_inlet_flux_ratio_tail_mean = 1.0280528796842723
midplane_to_inlet_flux_ratio_tail_mean = 0.9111280219154153
outlet_flux_tail_cv = 0.47087164136218246
tail_outlet_flux_values = [58.49066409992427, 55.08408557414636, 14.30614811182022]
```

That tail pattern was the direct Step134 target: the outlet flux stayed high at
steps 200 and 225, then collapsed at the 250-step terminal sample.

## Code Surface

Step134 added a bounded diagnostic and control-plane surface without changing
default Step131-Step133 behavior.

New `LBMConfig` fields:

- `open_boundary_flux_control_measure_plane_offset: int = 0`
- `open_boundary_outlet_flux_drop_guard_enabled: bool = False`
- `open_boundary_outlet_flux_drop_guard_min_ratio: float = 0.60`

The default offset `0` preserves the old control plane at `x = nx - 1`. Step134
rows may measure controller flux at `nx - 2` or `nx - 3` by setting offset `1`
or `2`. The optional drop guard is disabled by default.

New diagnostics include:

- `near_outlet_flux_xminus1`
- `near_outlet_flux_xminus2`
- `near_outlet_flux_xminus3`
- `near_outlet_to_outlet_flux_ratio`
- `controller_true_outlet_flux_for_guard`
- `controller_drop_guard_activation_count_run`
- `drop_guard_activation_count_tail`

Step121 now exposes the distinct bounded phase:

```text
planeflux_stationarity48
```

This phase keeps `row_role = plane_flux_control_candidate_48` and does not add
any selected-candidate semantics.

## Tiny Smoke

Tiny smoke artifact:

```text
outputs/step134_outlet_stationarity_repair/tiny_smoke/tiny_step134_outlet_stationarity_smoke
```

Tiny smoke was rerun after the Step134 implementation commit so the artifact
records:

```text
code_commit_at_run = 26a79a492565e98ada2e55c1fd968b790f9f7df7
executed_shape = [8, 6, 6]
steps_completed = 20
requested_window_completed = true
finite_pass = true
first_failure_step = null
validation_claim_allowed = false
selected96_claim_allowed = false
```

The tiny smoke exists only to prove wiring and real kernel execution. It is not
validation evidence.

## 48^3 Command

The final 48^3 Step134 artifacts were also rerun after the implementation
commit to avoid stale `code_commit_at_run` provenance.

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_stationarity48 `
  --output-dir outputs\step134_outlet_stationarity_repair\planeflux_stationarity48 `
  --allow-large-real-rows `
  --output-interval 25 `
  --force `
  --no-resume
```

Artifact root:

```text
outputs/step134_outlet_stationarity_repair/planeflux_stationarity48
```

All six rows record:

```text
code_commit_at_run = 26a79a492565e98ada2e55c1fd968b790f9f7df7
steps_completed = 250
requested_window_completed = true
finite_pass = true
first_failure_step = null
validation_claim_allowed = false
selected96_claim_allowed = false
```

## 48^3 Results

| Row | mass abs | flux mean | flux max | outlet/inlet | mid/inlet | outlet CV | last/mean | slope | near/outlet | guard tail | accepted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| convective offset1 guard_on min0p70 | 0.0220512406 | 0.2598977292 | 0.4462588912 | 1.4026043008 | 1.2407131120 | 0.2017983225 | 1.2780022965 | 20.0922909225 | 0.9847224949 | 0 | no |
| regularized offset1 guard_on min0p70 alpha0p01 | 0.0198232643 | 0.4413925197 | 0.6123331130 | 1.1647833139 | 1.0147826175 | 0.4729750761 | 0.3336844969 | -50.3680201354 | 0.9990451988 | 0 | no |
| regularized offset1 guard_off min0p60 alpha0p02 | 0.0140914290 | 0.3965887438 | 0.6523567810 | 1.0273294064 | 0.9095671323 | 0.4682320104 | 0.3393907727 | -43.8961871290 | 0.9916974656 | 0 | no |
| regularized offset1 guard_on min0p50 alpha0p02 | 0.0140913273 | 0.3966219504 | 0.6524571054 | 1.0272954331 | 0.9095676267 | 0.4682932535 | 0.3393040344 | -43.9003244764 | 0.9916992227 | 0 | no |
| regularized offset1 guard_on min0p70 alpha0p02 | 0.0140913788 | 0.3969569189 | 0.6534690502 | 1.0269529058 | 0.9095918397 | 0.4689114066 | 0.3384286953 | -43.9421526353 | 0.9917012526 | 0 | no |
| regularized offset2 guard_on min0p70 alpha0p02 | 0.0140072222 | 0.3934756112 | 0.6463693210 | 1.0272119276 | 0.9077078805 | 0.4640345823 | 0.3452949272 | -43.4927941638 | 0.9913981763 | 0 | no |

Tail outlet flux values:

| Row | tail outlet flux values |
| --- | --- |
| convective offset1 guard_on min0p70 | `[51.00883558931479, 44.79379082689665, 71.10112651184923]` |
| regularized offset1 guard_on min0p70 alpha0p01 | `[66.37126387105036, 61.50311225838913, 16.003243735658877]` |
| regularized offset1 guard_off min0p60 alpha0p02 | `[58.35474459384096, 54.99121087467459, 14.458557464887052]` |
| regularized offset1 guard_on min0p50 alpha0p02 | `[58.35471020178748, 54.99120345169703, 14.45438572542148]` |
| regularized offset1 guard_on min0p70 alpha0p02 | `[58.35445773732047, 54.99106591941627, 14.412305101996845]` |
| regularized offset2 guard_on min0p70 alpha0p02 | `[58.20238007592607, 54.88822525253548, 14.709585912146114]` |

## Interpretation

Step134 ruled out the simplest "controller reads the wrong final outlet plane"
hypothesis. For the regularized rows, `near_outlet_to_outlet_flux_ratio_tail_mean`
stays around `0.991` to `0.999`, which means the near-outlet control planes and
the true outlet plane collapse together at the tail. Moving the control-plane
measurement from `nx - 1` to `nx - 2` or `nx - 3` did not repair stationarity.

The drop guard also did not address the terminal collapse. It did activate in
some full-run counts, but `drop_guard_activation_count_tail = 0` for every 48^3
row, so it did not intervene during the late tail samples where the regularized
collapse appears.

The convective diagnostic row reduced mean flux imbalance relative to the
regularized rows, but it still failed mass acceptance, flux max, outlet/inlet
ratio, mid/inlet ratio, and outlet-tail stationarity. It is diagnostic evidence,
not a promotion candidate.

## Verification

TDD red was observed before implementation: the Step134 test failed because the
`planeflux_stationarity48` phase and new config fields were absent.

Green checks before the final 48^3 rerun:

```text
tests/test_step134_outlet_stationarity_contract.py
6 passed in 1.49 s

tests/test_step133_mass_damped_plane_flux_contract.py
tests/test_step134_outlet_stationarity_contract.py
12 passed in 1.74 s

tests/test_step118_open_boundary_limiter_contract.py
tests/test_step120_actual_limiter_counter_contract.py
tests/test_step120_best_boundary_selection_contract.py
tests/test_step121_campaign_gate_contract.py
14 passed, 4 Taichi matrix warnings in 32.55 s

tests/test_step131_plane_flux_controller_contract.py
tests/test_step132_plane_flux_authority_sweep_contract.py
tests/test_step133_mass_damped_plane_flux_contract.py
tests/test_step134_outlet_stationarity_contract.py
24 passed, 8 Taichi matrix warnings in 161.66 s
```

Final verification after the report/docs and provenance-test updates:

```text
py_compile on touched Step134 modules/tests: passed

tests/test_step125_campaign_provenance_identity_contract.py::test_step125_current_campaign_records_split_commit_identity
1 passed in 0.82 s

Step123-Step134 focused contract set
63 passed, 28 Taichi matrix warnings in 408.85 s

Step56/57/58 behavior-preservation regression set
10 passed in 12.20 s
```

The focused set initially exposed that the Step125 provenance test still looked
only at the legacy Step121 manifest path. The test now resolves the current
manifest from `ACTIVE_CAMPAIGN.artifact_root` first, with the old path retained
as fallback. The Step56/57/58 set initially exposed that the Step56 behavior
policy was missing the current no-op default fields; the policy and generated
Step56 behavior audit artifact were refreshed with the Step133/Step134 default
fields.

## Claim Boundary

Step134 is complete as bounded 48^3 diagnostic evidence. It does not select a
boundary, does not repair 48^3 to final acceptance, and does not authorize
selected 96^3.
