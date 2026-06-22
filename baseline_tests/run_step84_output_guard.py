import os

from step84_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step84_output_guard import build_step84_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step84_output_guard,
        "outputs/step84_output_guard",
        "logs/step84_output_guard.log",
        "output_guard_pass",
        "[OK] Step84 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
