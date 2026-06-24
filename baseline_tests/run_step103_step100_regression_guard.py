import os

from step103_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step103_step100_regression_guard import build_step103_step100_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step103_step100_regression_guard,
        "outputs/step103_step100_regression_guard",
        "logs/step103_step100_regression_guard.log",
        "step103_step100_regression_guard_pass",
        "[OK] Step103 Step100 regression guard finished",
        "step100_regression_guard",
    )


if __name__ == "__main__":
    main()
