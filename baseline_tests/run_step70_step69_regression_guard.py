import os

from step70_common import ROOT, run_audit
from src.mpm_lbm.evidence.step70_regression_guard import build_step70_regression_guard


def main():
    os.chdir(ROOT)
    run_audit(build_step70_regression_guard, "outputs/step70_step69_regression_guard", "logs/step70_step69_regression_guard.log", "step70_step69_regression_guard_pass", "[OK] Step 70 Step69 regression guard finished")


if __name__ == "__main__":
    main()
