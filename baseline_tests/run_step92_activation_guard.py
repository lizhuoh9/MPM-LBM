from step92_common import run_named_audit
from src.mpm_lbm.evidence.step92_activation_guard import build_step92_activation_guard


def main():
    run_named_audit(
        build_step92_activation_guard,
        "outputs/step92_activation_guard",
        "logs/step92_activation_guard.log",
        "step92_activation_guard_pass",
        "[OK] Step92 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
