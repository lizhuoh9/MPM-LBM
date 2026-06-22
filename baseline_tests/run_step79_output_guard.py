from step79_common import run_named_audit
from src.mpm_lbm.evidence.step79_output_guard import build_step79_output_guard


FIELDS = ["path", "size_bytes", "extension", "forbidden", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step79_output_guard,
        "outputs/step79_output_guard",
        "logs/step79_output_guard.log",
        "output_guard_pass",
        "[OK] Step79 output guard finished",
        "output_guard",
        FIELDS,
    )
