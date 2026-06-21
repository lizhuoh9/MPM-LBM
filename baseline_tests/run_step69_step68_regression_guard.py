import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.step69_regression_guard import build_step69_regression_guard


def main():
    os.chdir(ROOT)
    run_audit(build_step69_regression_guard, "outputs/step69_step68_regression_guard", "logs/step69_step68_regression_guard.log", "step69_step68_regression_guard_pass", "[OK] Step 69 Step68 regression guard finished")


if __name__ == "__main__":
    main()
