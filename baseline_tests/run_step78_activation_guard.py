from step78_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_5step_activation_guard import build_step78_post_gate_5step_activation_guard


FIELDS = ["row_name", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step78_post_gate_5step_activation_guard,
        "outputs/step78_activation_guard",
        "logs/step78_activation_guard.log",
        "post_gate_5step_activation_guard_pass",
        "[OK] Step78 activation guard finished",
        "activation_guard",
        FIELDS,
    )
