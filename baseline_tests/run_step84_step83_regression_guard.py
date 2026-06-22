import os

from step84_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step84_step83_regression_guard import build_step84_step83_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step84_step83_regression_guard,
        "outputs/step84_step83_regression_guard",
        "logs/step84_step83_regression_guard.log",
        "step84_step83_regression_guard_pass",
        "[OK] Step84 Step83 regression guard finished",
        "step83_regression_guard",
    )


if __name__ == "__main__":
    main()
