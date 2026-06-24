import os

from step105_common import ROOT, write_log
from src.mpm_lbm.evidence.step105_transient_gap_smoke_runner import validate_step105_flow_development


def main():
    os.chdir(ROOT)
    rows, summary = validate_step105_flow_development(ROOT)
    marker = "[OK] Step105 flow development finished"
    write_log("logs/step105_flow_development.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
