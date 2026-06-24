import os

from step94_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step94_output_guard import build_step94_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step94_output_guard,
        "outputs/step94_output_guard",
        "logs/step94_output_guard.log",
        "output_guard_pass",
        "[OK] Step94 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
