import os

from step51_common import ROOT, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import summarize_transfer_component_effects

    rows = transfer_comparison_rows()
    comparison_rows, summary = summarize_transfer_component_effects(rows)
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 51 component effect by transfer failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_component_effect_by_transfer"
    write_csv_rows(out_dir / "component_effect_by_transfer.csv", comparison_rows)
    write_json(out_dir / "component_effect_by_transfer.json", {"summary": summary, "rows": comparison_rows})
    marker = "[OK] Step 51 component effect by transfer finished"
    write_log("logs/step51_component_effect_by_transfer.log", [marker, f"comparison_count={summary['comparison_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
