import os

from step82_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step82_step81_regression_guard import build_step82_step81_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step82_step81_regression_guard,
        "outputs/step82_step81_regression_guard",
        "logs/step82_step81_regression_guard.log",
        "step82_step81_regression_guard_pass",
        "[OK] Step82 Step81 regression guard finished",
        "step81_regression_guard",
    )


if __name__ == "__main__":
    main()
