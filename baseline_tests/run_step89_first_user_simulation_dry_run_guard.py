from step89_common import run_named_audit
from src.mpm_lbm.evidence.step89_first_user_simulation_dry_run_guard import (
    build_step89_first_user_simulation_dry_run_guard,
)


def main():
    run_named_audit(
        build_step89_first_user_simulation_dry_run_guard,
        "outputs/step89_first_user_simulation_dry_run_guard",
        "logs/step89_first_user_simulation_dry_run_guard.log",
        "step89_first_user_simulation_dry_run_guard_pass",
        "[OK] Step89 first user simulation dry run guard finished",
        "first_user_simulation_dry_run_guard",
    )


if __name__ == "__main__":
    main()
