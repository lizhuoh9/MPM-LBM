from step76_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_rebaseline_quality_audit import (
    build_step76_post_gate_rebaseline_quality_audit,
)


FIELDS = ["row_name", "check", "actual", "operator", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step76_post_gate_rebaseline_quality_audit,
        "outputs/step76_post_gate_rebaseline_quality",
        "logs/step76_post_gate_rebaseline_quality.log",
        "post_gate_rebaseline_quality_pass",
        "[OK] Step76 post-gate rebaseline quality finished",
        "post_gate_rebaseline_quality",
        FIELDS,
    )
