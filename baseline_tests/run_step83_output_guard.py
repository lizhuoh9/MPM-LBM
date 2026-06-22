import os

from step83_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step83_output_guard import build_step83_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step83_output_guard,
        "outputs/step83_output_guard",
        "logs/step83_output_guard.log",
        "output_guard_pass",
        "[OK] Step83 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
