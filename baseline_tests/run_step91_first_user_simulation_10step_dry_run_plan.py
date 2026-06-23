from step91_common import run_named_audit
from src.mpm_lbm.evidence.step91_first_user_simulation_10step_dry_run_plan import (
    build_step91_first_user_simulation_10step_dry_run_plan,
)


def main():
    run_named_audit(
        build_step91_first_user_simulation_10step_dry_run_plan,
        "outputs/step91_first_user_simulation_10step_dry_run_plan",
        "logs/step91_first_user_simulation_10step_dry_run_plan.log",
        "step91_first_user_simulation_10step_dry_run_plan_pass",
        "[OK] Step91 first user simulation 10-step dry run plan finished",
        "first_user_simulation_10step_dry_run_plan",
    )


if __name__ == "__main__":
    main()
