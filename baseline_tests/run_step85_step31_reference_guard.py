from step85_common import run_named_audit
from src.mpm_lbm.evidence.step85_step31_reference_guard import build_step85_step31_reference_guard


def main():
    run_named_audit(
        build_step85_step31_reference_guard,
        "outputs/step85_step31_reference_guard",
        "logs/step85_step31_reference_guard.log",
        "step85_step31_reference_guard_pass",
        "[OK] Step85 Step31 reference guard finished",
        "step31_reference_guard",
    )


if __name__ == "__main__":
    main()
