import os

from step72_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step72_regression_guard import build_step72_step71_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(build_step72_step71_regression_guard, "outputs/step72_step71_regression_guard", "logs/step72_step71_regression_guard.log", "step72_step71_regression_guard_pass", "[OK] Step 72 Step71 regression guard finished", "step71_regression_guard")


if __name__ == "__main__":
    main()
