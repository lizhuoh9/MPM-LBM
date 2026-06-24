from step92_common import run_named_audit
from src.mpm_lbm.evidence.step92_first_user_simulation_10step_dry_run_quality_audit import (
    build_step92_first_user_simulation_10step_dry_run_quality_audit,
)


def main():
    run_named_audit(
        build_step92_first_user_simulation_10step_dry_run_quality_audit,
        "outputs/step92_first_user_simulation_10step_dry_run_quality",
        "logs/step92_first_user_simulation_10step_dry_run_quality.log",
        "step92_first_user_simulation_10step_dry_run_quality_pass",
        "[OK] Step92 first user simulation 10-step dry run quality finished",
        "first_user_simulation_10step_dry_run_quality",
    )


if __name__ == "__main__":
    main()
