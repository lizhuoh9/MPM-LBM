import os

from step88_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step88_step84_regression_guard import build_step88_step84_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step88_step84_regression_guard,
        "outputs/step88_step84_regression_guard",
        "logs/step88_step84_regression_guard.log",
        "step88_step84_regression_guard_pass",
        "[OK] Step88 Step84 regression guard finished",
        "step84_regression_guard",
    )


if __name__ == "__main__":
    main()
