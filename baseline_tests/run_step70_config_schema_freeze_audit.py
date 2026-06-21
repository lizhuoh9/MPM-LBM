import os

from step70_common import ROOT, run_audit, write_csv_rows, write_json
from src.mpm_lbm.evidence.config_schema_freeze_audit import build_step70_config_schema_freeze_audit


def main():
    os.chdir(ROOT)
    rows, summary = run_audit(build_step70_config_schema_freeze_audit, "outputs/step70_config_schema_freeze_audit", "logs/step70_config_schema_freeze_audit.log", "config_schema_freeze_audit_pass", "[OK] Step 70 config schema freeze audit finished")
    out_dir = ROOT / "outputs" / "step70_config_schema_freeze_audit"
    write_csv_rows(out_dir / "config_schema_freeze.csv", rows)
    write_json(out_dir / "config_schema_freeze.json", {"summary": summary, "rows": rows})


if __name__ == "__main__":
    main()
