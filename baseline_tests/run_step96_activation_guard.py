import os

from step96_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step96_activation_guard import build_step96_activation_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step96_activation_guard,
        "outputs/step96_activation_guard",
        "logs/step96_activation_guard.log",
        "step96_activation_guard_pass",
        "[OK] Step96 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
