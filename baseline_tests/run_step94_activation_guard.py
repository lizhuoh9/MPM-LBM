import os

from step94_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step94_activation_guard import build_step94_activation_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step94_activation_guard,
        "outputs/step94_activation_guard",
        "logs/step94_activation_guard.log",
        "step94_activation_guard_pass",
        "[OK] Step94 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
