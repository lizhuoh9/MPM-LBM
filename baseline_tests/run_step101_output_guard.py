import os

from step101_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step101_output_guard import build_step101_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step101_output_guard,
        "outputs/step101_output_guard",
        "logs/step101_output_guard.log",
        "output_guard_pass",
        "[OK] Step101 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
