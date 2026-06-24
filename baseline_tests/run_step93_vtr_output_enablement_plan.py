from step93_common import run_named_audit
from src.mpm_lbm.evidence.step93_vtr_output_enablement_plan import (
    build_step93_vtr_output_enablement_plan,
)


def main():
    run_named_audit(
        build_step93_vtr_output_enablement_plan,
        "outputs/step93_vtr_output_enablement_plan",
        "logs/step93_vtr_output_enablement_plan.log",
        "step93_vtr_output_enablement_plan_pass",
        "[OK] Step93 VTR output enablement plan finished",
        "vtr_output_enablement_plan",
    )


if __name__ == "__main__":
    main()
