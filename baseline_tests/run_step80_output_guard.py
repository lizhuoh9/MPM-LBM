from step80_common import run_named_audit
from src.mpm_lbm.evidence.step80_output_guard import build_step80_output_guard


FIELDS = ["path", "size_bytes", "extension", "forbidden", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step80_output_guard,
        "outputs/step80_output_guard",
        "logs/step80_output_guard.log",
        "output_guard_pass",
        "[OK] Step80 output guard finished",
        "output_guard",
        FIELDS,
    )
