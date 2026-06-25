import os

from step110_common import ROOT, write_log
from src.mpm_lbm.evidence.step110_monitor_alignment import build_step110_monitor_alignment


def main():
    os.chdir(ROOT)
    _, summary = build_step110_monitor_alignment(ROOT)
    marker = "[OK] Step110 monitor alignment finished"
    write_log("logs/step110_monitor_alignment.log", [marker, f"monitor_count={summary['monitor_count']}"])
    print(marker)


if __name__ == "__main__":
    main()

