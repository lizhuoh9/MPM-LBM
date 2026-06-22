from step78_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_5step_rebaseline_quality_audit import (
    build_step78_post_gate_5step_rebaseline_quality_audit,
)


FIELDS = ["row_name", "check", "actual", "operator", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step78_post_gate_5step_rebaseline_quality_audit,
        "outputs/step78_post_gate_5step_rebaseline_quality",
        "logs/step78_post_gate_5step_rebaseline_quality.log",
        "post_gate_5step_rebaseline_quality_pass",
        "[OK] Step78 post-gate rebaseline quality finished",
        "post_gate_5step_rebaseline_quality",
        FIELDS,
    )
