import os

from step110_common import ROOT, write_log
from src.mpm_lbm.evidence.step110_proxy_preflow_runner import build_step110_proxy_preflow


def main():
    os.chdir(ROOT)
    summary = build_step110_proxy_preflow(ROOT)
    marker = "[OK] Step110 proxy preflow finished"
    write_log(
        "logs/step110_proxy_preflow.log",
        [marker, f"preflow_completed_lbm_substeps={summary['preflow_completed_lbm_substeps']}"],
    )
    print(marker)


if __name__ == "__main__":
    main()

