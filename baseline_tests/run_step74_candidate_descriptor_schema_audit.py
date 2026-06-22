from step74_common import run_named_audit
from src.mpm_lbm.evidence.candidate_descriptor_schema_audit import build_step74_candidate_descriptor_schema_audit


if __name__ == "__main__":
    run_named_audit(
        build_step74_candidate_descriptor_schema_audit,
        "outputs/step74_candidate_descriptor_schema_audit",
        "logs/step74_candidate_descriptor_schema_audit.log",
        "candidate_descriptor_schema_audit_pass",
        "[OK] Step 74 candidate descriptor schema audit finished",
        "candidate_descriptor_schema",
    )
