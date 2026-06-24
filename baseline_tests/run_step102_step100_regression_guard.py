import os

from step102_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step102_step100_regression_guard import build_step102_step100_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step102_step100_regression_guard,
        "outputs/step102_step100_regression_guard",
        "logs/step102_step100_regression_guard.log",
        "step102_step100_regression_guard_pass",
        "[OK] Step102 Step100 regression guard finished",
        "step100_regression_guard",
    )


if __name__ == "__main__":
    main()
