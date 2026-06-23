from step90_common import run_named_audit
from src.mpm_lbm.evidence.step90_activation_guard import build_step90_activation_guard


def main():
    run_named_audit(
        build_step90_activation_guard,
        "outputs/step90_activation_guard",
        "logs/step90_activation_guard.log",
        "step90_activation_guard_pass",
        "[OK] Step90 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
