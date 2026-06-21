import os

from step51_common import ROOT, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import summarize_link_area_envelope

    rows = transfer_comparison_rows()
    envelope_rows, summary = summarize_link_area_envelope(rows)
    if not summary["link_area_envelope_pass"]:
        raise RuntimeError(f"Step 51 link-area envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_link_area_envelope"
    write_csv_rows(out_dir / "link_area_envelope.csv", envelope_rows)
    write_json(out_dir / "link_area_envelope.json", {"summary": summary, "rows": envelope_rows})
    marker = "[OK] Step 51 link-area envelope finished"
    write_log("logs/step51_link_area_envelope.log", [marker, f"link_area_row_count={summary['link_area_row_count']}", f"link_area_envelope_pass={summary['link_area_envelope_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
