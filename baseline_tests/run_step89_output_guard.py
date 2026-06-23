from step89_common import run_named_audit
from src.mpm_lbm.evidence.step89_output_guard import build_step89_output_guard


def main():
    run_named_audit(
        build_step89_output_guard,
        "outputs/step89_output_guard",
        "logs/step89_output_guard.log",
        "output_guard_pass",
        "[OK] Step89 output guard finished",
        "output_guard",
    )


if __name__ == "__main__":
    main()
