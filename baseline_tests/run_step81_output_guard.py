import os

from step81_common import ROOT, run_named_audit

from src.mpm_lbm.evidence.step81_output_guard import build_step81_output_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step81_output_guard,
        "outputs/step81_output_guard",
        "logs/step81_output_guard.log",
        "output_guard_pass",
        "[OK] Step81 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
