from step93_common import run_named_audit
from src.mpm_lbm.evidence.step93_step91_regression_guard import (
    build_step93_step91_regression_guard,
)


def main():
    run_named_audit(
        build_step93_step91_regression_guard,
        "outputs/step93_step91_regression_guard",
        "logs/step93_step91_regression_guard.log",
        "step93_step91_regression_guard_pass",
        "[OK] Step93 Step91 regression guard finished",
        "step91_regression_guard",
    )


if __name__ == "__main__":
    main()
