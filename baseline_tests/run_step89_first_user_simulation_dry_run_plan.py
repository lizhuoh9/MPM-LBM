from step89_common import run_named_audit
from src.mpm_lbm.evidence.step89_first_user_simulation_dry_run_plan import (
    build_step89_first_user_simulation_dry_run_plan,
)


def main():
    run_named_audit(
        build_step89_first_user_simulation_dry_run_plan,
        "outputs/step89_first_user_simulation_dry_run_plan",
        "logs/step89_first_user_simulation_dry_run_plan.log",
        "step89_first_user_simulation_dry_run_plan_pass",
        "[OK] Step89 first user simulation dry run plan finished",
        "first_user_simulation_dry_run_plan",
    )


if __name__ == "__main__":
    main()
