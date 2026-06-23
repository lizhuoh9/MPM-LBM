from step90_common import run_named_audit
from src.mpm_lbm.evidence.step90_first_user_simulation_dry_run_quality_audit import (
    build_step90_first_user_simulation_dry_run_quality_audit,
)


def main():
    run_named_audit(
        build_step90_first_user_simulation_dry_run_quality_audit,
        "outputs/step90_first_user_simulation_dry_run_quality",
        "logs/step90_first_user_simulation_dry_run_quality.log",
        "step90_first_user_simulation_dry_run_quality_pass",
        "[OK] Step90 first user simulation dry run quality finished",
        "first_user_simulation_dry_run_quality",
    )


if __name__ == "__main__":
    main()
