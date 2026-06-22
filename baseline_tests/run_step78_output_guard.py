from step78_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_5step_output_guard import build_step78_post_gate_output_guard


FIELDS = ["path", "size_bytes", "extension", "forbidden", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step78_post_gate_output_guard,
        "outputs/step78_output_guard",
        "logs/step78_output_guard.log",
        "output_guard_pass",
        "[OK] Step78 output guard finished",
        "output_guard",
        FIELDS,
    )
