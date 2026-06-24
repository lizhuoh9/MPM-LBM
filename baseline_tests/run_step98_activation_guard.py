import os

from step98_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step98_activation_guard import build_step98_activation_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step98_activation_guard,
        "outputs/step98_activation_guard",
        "logs/step98_activation_guard.log",
        "step98_activation_guard_pass",
        "[OK] Step98 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
