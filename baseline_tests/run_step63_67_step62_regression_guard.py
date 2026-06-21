import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.step63_67_regression_guard import build_step63_67_step62_regression_guard


def main():
    os.chdir(ROOT)
    run_audit(build_step63_67_step62_regression_guard, "outputs/step63_67_step62_regression_guard", "logs/step63_67_step62_regression_guard.log", "step63_67_regression_guard_pass", "[OK] Step 63-67 Step 62 regression guard finished", None)


if __name__ == "__main__":
    main()
