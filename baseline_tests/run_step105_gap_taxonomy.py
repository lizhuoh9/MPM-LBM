import os

from step105_common import ROOT, write_log
from src.mpm_lbm.evidence.step105_gap_taxonomy import build_step105_gap_taxonomy, write_step105_gap_taxonomy_artifacts


def main():
    os.chdir(ROOT)
    rows, summary = build_step105_gap_taxonomy(ROOT)
    if not summary["gap_taxonomy_report_pass"]:
        raise RuntimeError(f"Step105 gap taxonomy failed: {summary}")
    write_step105_gap_taxonomy_artifacts(ROOT, rows, summary)
    marker = "[OK] Step105 gap taxonomy finished"
    write_log("logs/step105_gap_taxonomy.log", [marker, f"gap_count={summary['gap_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
