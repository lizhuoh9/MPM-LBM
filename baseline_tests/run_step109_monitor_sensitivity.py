import os

from step109_common import ROOT, write_log
from src.mpm_lbm.evidence.step109_monitor_sensitivity import build_step109_monitor_sensitivity


def main():
    os.chdir(ROOT)
    rows, summary = build_step109_monitor_sensitivity(ROOT)
    if not summary["monitor_sensitivity_pass"]:
        raise RuntimeError(f"Step109 monitor sensitivity failed: {summary}")
    marker = "[OK] Step109 monitor sensitivity finished"
    write_log(
        "logs/step109_monitor_sensitivity.log",
        [marker, f"monitor_count={summary['monitor_count']}", f"max_to_mean_peak_ratio={summary['max_to_mean_peak_ratio']}"],
    )
    print(marker)


if __name__ == "__main__":
    main()
