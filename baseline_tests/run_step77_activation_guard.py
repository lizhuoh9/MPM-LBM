from step77_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_3step_activation_guard import build_step77_post_gate_3step_activation_guard


FIELDS = ["row_name", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step77_post_gate_3step_activation_guard,
        "outputs/step77_activation_guard",
        "logs/step77_activation_guard.log",
        "post_gate_3step_activation_guard_pass",
        "[OK] Step77 activation guard finished",
        "activation_guard",
        FIELDS,
    )
