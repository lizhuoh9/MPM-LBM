import os

from step103_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step103_activation_guard import build_step103_activation_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step103_activation_guard,
        "outputs/step103_activation_guard",
        "logs/step103_activation_guard.log",
        "step103_activation_guard_pass",
        "[OK] Step103 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
