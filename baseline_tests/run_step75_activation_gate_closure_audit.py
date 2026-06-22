from step75_common import run_named_audit
from src.mpm_lbm.evidence.activation_gate_closure_audit import build_step75_activation_gate_closure_audit


if __name__ == "__main__":
    run_named_audit(
        build_step75_activation_gate_closure_audit,
        "outputs/step75_activation_gate_closure_audit",
        "logs/step75_activation_gate_closure_audit.log",
        "activation_gate_closure_audit_pass",
        "[OK] Step 75 activation gate closure audit finished",
        "activation_gate_closure",
    )
