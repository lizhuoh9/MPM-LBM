import os

from step100_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step100_activation_guard import build_step100_activation_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step100_activation_guard,
        "outputs/step100_activation_guard",
        "logs/step100_activation_guard.log",
        "step100_activation_guard_pass",
        "[OK] Step100 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
