from step91_common import run_named_audit
from src.mpm_lbm.evidence.step91_first_user_simulation_10step_dry_run_guard import (
    build_step91_first_user_simulation_10step_dry_run_guard,
)


def main():
    run_named_audit(
        build_step91_first_user_simulation_10step_dry_run_guard,
        "outputs/step91_first_user_simulation_10step_dry_run_guard",
        "logs/step91_first_user_simulation_10step_dry_run_guard.log",
        "step91_first_user_simulation_10step_dry_run_guard_pass",
        "[OK] Step91 first user simulation 10-step dry run guard finished",
        "first_user_simulation_10step_dry_run_guard",
    )


if __name__ == "__main__":
    main()
