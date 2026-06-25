# Step107 Public Fluent Plot Error Comparison

This is not Fluent validation. It compares the current proxy solver displacement curve against an approximate public-plot digitization with explicit uncertainty.

| reference_loaded | solver_curve_loaded | monitor_used | monitor_equivalence | sample_count | peak_reference_m | peak_solver_m | peak_abs_error_m | peak_relative_error | rms_abs_error_m | normalized_rms_error | final_reference_m | final_solver_m | final_abs_error_m | final_relative_error | time_of_peak_reference_s | time_of_peak_solver_s | peak_time_error_s | shape_correlation | sign_consistency | all_metrics_finite | validation_claim_allowed | direct_quantitative_equivalence_allowed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | True | free_tip_proxy_mean | False | 51 | 0.000395 | 3.766233760416071e-07 | 0.0003946233766239584 | 0.9990465230986288 | 0.00024358400587801233 | 0.6166683693114237 | 6e-05 | 3.766233760416071e-07 | 5.9623376623958394e-05 | 0.9937229437326399 | 0.004 | 0.01 | 0.006 | 0.07747139097796335 | True | True | False | False |
