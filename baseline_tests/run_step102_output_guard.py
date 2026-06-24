import os

from step102_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step102_output_guard import build_step102_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step102_output_guard,
        "outputs/step102_output_guard",
        "logs/step102_output_guard.log",
        "output_guard_pass",
        "[OK] Step102 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
