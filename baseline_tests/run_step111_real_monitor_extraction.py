import os

from step110_common import ROOT
from src.mpm_lbm.evidence.step111_common import write_log
from src.mpm_lbm.evidence.step111_real_monitor_extraction import build_step111_monitor_report


def main():
    os.chdir(ROOT)
    rows, summary = build_step111_monitor_report(ROOT)
    if not summary["monitor_alignment_pass"]:
        raise RuntimeError(f"Step111 monitor extraction failed: {summary}")
    marker = "[OK] Step111 real monitor extraction finished"
    write_log(ROOT, "logs/step111_real_monitor_extraction.log", [marker, f"monitor_rows={len(rows)}"])
    print(marker)


if __name__ == "__main__":
    main()
