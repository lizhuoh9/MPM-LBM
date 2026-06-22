import os

from step71_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step71_regression_guard import build_step71_step70_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(build_step71_step70_regression_guard, "outputs/step71_step70_regression_guard", "logs/step71_step70_regression_guard.log", "step71_step70_regression_guard_pass", "[OK] Step 71 Step70 regression guard finished", "step70_regression_guard")


if __name__ == "__main__":
    main()
