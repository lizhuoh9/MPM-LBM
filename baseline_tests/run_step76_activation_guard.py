from step76_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_activation_guard import build_step76_post_gate_activation_guard


FIELDS = ["row_name", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step76_post_gate_activation_guard,
        "outputs/step76_activation_guard",
        "logs/step76_activation_guard.log",
        "post_gate_activation_guard_pass",
        "[OK] Step76 activation guard finished",
        "activation_guard",
        FIELDS,
    )
