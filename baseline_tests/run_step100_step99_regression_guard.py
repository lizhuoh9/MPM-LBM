from step100_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step100_step99_regression_guard import build_step100_step99_regression_guard


def main():
    run_named_audit(
        build_step100_step99_regression_guard,
        "outputs/step100_step99_regression_guard",
        "logs/step100_step99_regression_guard.log",
        "step100_step99_regression_guard_pass",
        "[OK] Step100 Step99 regression guard finished",
        "step99_regression_guard",
    )


if __name__ == "__main__":
    main()
