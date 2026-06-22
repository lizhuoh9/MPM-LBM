from step77_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_3step_rebaseline_quality_audit import (
    build_step77_post_gate_3step_rebaseline_quality_audit,
)


FIELDS = ["row_name", "check", "actual", "operator", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step77_post_gate_3step_rebaseline_quality_audit,
        "outputs/step77_post_gate_3step_rebaseline_quality",
        "logs/step77_post_gate_3step_rebaseline_quality.log",
        "post_gate_3step_rebaseline_quality_pass",
        "[OK] Step77 post-gate rebaseline quality finished",
        "post_gate_3step_rebaseline_quality",
        FIELDS,
    )
