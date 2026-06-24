import os

from step96_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step96_output_guard import build_step96_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step96_output_guard,
        "outputs/step96_output_guard",
        "logs/step96_output_guard.log",
        "output_guard_pass",
        "[OK] Step96 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
