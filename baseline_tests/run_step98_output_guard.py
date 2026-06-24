import os

from step98_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step98_output_guard import build_step98_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step98_output_guard,
        "outputs/step98_output_guard",
        "logs/step98_output_guard.log",
        "output_guard_pass",
        "[OK] Step98 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
