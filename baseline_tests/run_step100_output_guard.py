import os

from step100_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step100_output_guard import build_step100_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step100_output_guard,
        "outputs/step100_output_guard",
        "logs/step100_output_guard.log",
        "output_guard_pass",
        "[OK] Step100 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
