import os

from step95_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step95_step94_regression_guard import build_step95_step94_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step95_step94_regression_guard,
        "outputs/step95_step94_regression_guard",
        "logs/step95_step94_regression_guard.log",
        "step95_step94_regression_guard_pass",
        "[OK] Step95 Step94 regression guard finished",
        "step94_regression_guard",
    )


if __name__ == "__main__":
    main()
