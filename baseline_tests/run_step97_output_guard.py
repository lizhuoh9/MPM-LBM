import os

from step97_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step97_output_guard import build_step97_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step97_output_guard,
        "outputs/step97_output_guard",
        "logs/step97_output_guard.log",
        "output_guard_pass",
        "[OK] Step97 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
