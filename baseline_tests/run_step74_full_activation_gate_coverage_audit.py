from step74_common import run_named_audit
from src.mpm_lbm.evidence.step74_full_activation_gate_coverage_audit import build_step74_full_activation_gate_coverage_audit


if __name__ == "__main__":
    run_named_audit(
        build_step74_full_activation_gate_coverage_audit,
        "outputs/step74_full_activation_gate_coverage_audit",
        "logs/step74_full_activation_gate_coverage_audit.log",
        "full_activation_gate_coverage_audit_pass",
        "[OK] Step 74 full activation gate coverage audit finished",
        "full_activation_gate_coverage",
    )
