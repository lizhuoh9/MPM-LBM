from step86_common import run_named_audit
from src.mpm_lbm.evidence.step86_step31_reference_guard import build_step86_step31_reference_guard


def main():
    run_named_audit(
        build_step86_step31_reference_guard,
        "outputs/step86_step31_reference_guard",
        "logs/step86_step31_reference_guard.log",
        "step86_step31_reference_guard_pass",
        "[OK] Step86 Step31 reference guard finished",
        "step31_reference_guard",
    )


if __name__ == "__main__":
    main()
