import os

from step107_common import ROOT, write_log
from src.mpm_lbm.evidence.step107_public_reference_digitization import build_step107_public_reference_digitization


def main():
    os.chdir(ROOT)
    metadata, quality = build_step107_public_reference_digitization(ROOT)
    marker = "[OK] Step107 public Fluent reference digitization finished"
    write_log(
        "logs/step107_public_reference_digitization.log",
        [
            marker,
            f"source_url={metadata['source_url']}",
            f"sample_count={quality['sample_count']}",
            f"max_displacement_m={quality['max_displacement_m']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
