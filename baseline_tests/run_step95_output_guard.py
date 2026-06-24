import os

from step95_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step95_output_guard import build_step95_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step95_output_guard,
        "outputs/step95_output_guard",
        "logs/step95_output_guard.log",
        "output_guard_pass",
        "[OK] Step95 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
