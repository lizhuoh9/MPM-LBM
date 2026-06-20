import os

from step30_common import ROOT, load_step30_region_config, summary_rows, write_csv_rows, write_json, write_log
from src.squid_region_config import validate_squid_region_config


FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = load_step30_region_config()
    summary = validate_squid_region_config(config)
    if not summary["schema_pass"]:
        raise RuntimeError(f"Step 30 region schema validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step30_region_schema_validation"
    write_csv_rows(out_dir / "region_schema_validation.csv", summary_rows(summary), FIELDS)
    write_json(out_dir / "region_schema_validation.json", {"summary": summary, "config": config.to_dict()})
    marker = "[OK] Step 30 region schema validation finished"
    write_log(
        "logs/step30_region_schema_validation.log",
        [
            marker,
            f"required_region_count={summary['required_region_count']}",
            f"schema_pass={summary['schema_pass']}",
        ],
    )
    print(f"required_region_count={summary['required_region_count']}")
    print(marker)


if __name__ == "__main__":
    main()
