import os

from step94_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step94_step90_regression_guard import build_step94_step90_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step94_step90_regression_guard,
        "outputs/step94_step90_regression_guard",
        "logs/step94_step90_regression_guard.log",
        "step94_step90_regression_guard_pass",
        "[OK] Step94 Step90 regression guard finished",
        "step90_regression_guard",
    )


if __name__ == "__main__":
    main()
