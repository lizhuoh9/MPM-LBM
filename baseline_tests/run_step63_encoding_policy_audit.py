import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.encoding_policy_audit import build_encoding_policy_audit


def main():
    os.chdir(ROOT)
    run_audit(build_encoding_policy_audit, "outputs/step63_encoding_policy_audit", "logs/step63_encoding_policy_audit.log", "encoding_policy_audit_pass", "[OK] Step 63 encoding policy audit finished", None)


if __name__ == "__main__":
    main()
