import os

from step32_common import ROOT, load_schedule_config, resolve_path, write_csv_rows, write_json, write_log
from src.squid_kinematics_region_mapping import REGION_MAPPING_FIELDS, assert_region_mapping, region_mapping_rows, validate_kinematics_region_mapping
from src.squid_region_config import load_squid_proxy_region_config


def main():
    os.chdir(ROOT)
    config = load_schedule_config()
    region_config = load_squid_proxy_region_config(resolve_path(config.region_config_path))
    mapping = validate_kinematics_region_mapping(config, region_config)
    assert_region_mapping(mapping)
    rows = region_mapping_rows(mapping)

    out_dir = ROOT / "outputs" / "step32_region_mapping_validation"
    write_csv_rows(out_dir / "region_mapping_validation.csv", rows, REGION_MAPPING_FIELDS)
    write_json(out_dir / "region_mapping_validation.json", {"summary": mapping, "rows": rows})
    marker = "[OK] Step 32 region mapping validation finished"
    write_log(
        "logs/step32_region_mapping_validation.log",
        [marker, f"present_required_region_count={mapping['present_required_region_count']}", f"mapping_pass={mapping['mapping_pass']}"],
    )
    print(f"present_required_region_count={mapping['present_required_region_count']}")
    print(marker)


if __name__ == "__main__":
    main()
