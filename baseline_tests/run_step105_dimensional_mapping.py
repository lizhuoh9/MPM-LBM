import os

from step105_common import ROOT, write_log
from src.mpm_lbm.evidence.step105_dimensional_mapping import (
    build_step105_dimensional_mapping,
    write_step105_dimensional_mapping_artifacts,
)


def main():
    os.chdir(ROOT)
    rows, summary = build_step105_dimensional_mapping(ROOT)
    if not summary["dimensional_mapping_report_pass"]:
        raise RuntimeError(f"Step105 dimensional mapping failed: {summary}")
    write_step105_dimensional_mapping_artifacts(ROOT, rows, summary)
    marker = "[OK] Step105 dimensional mapping finished"
    write_log("logs/step105_dimensional_mapping.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
