import os

from step83_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step83_step82_regression_guard import build_step83_step82_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step83_step82_regression_guard,
        "outputs/step83_step82_regression_guard",
        "logs/step83_step82_regression_guard.log",
        "step83_step82_regression_guard_pass",
        "[OK] Step83 Step82 regression guard finished",
        "step82_regression_guard",
    )


if __name__ == "__main__":
    main()
