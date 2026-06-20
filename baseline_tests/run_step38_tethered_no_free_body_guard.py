import os

from step38_common import ROOT, STEP38_DRIVER_CONFIGS, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.tethered_cycle_diagnostics import guard_rows, summarize_no_free_body_state


def main():
    os.chdir(ROOT)
    configs = [read_json(path) for path in STEP38_DRIVER_CONFIGS]
    summary = summarize_no_free_body_state(configs, ROOT / "outputs" / "step38_cycle_driver")
    rows = guard_rows(summary)
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 38 tethered no-free-body guard failed: {summary}")

    out_dir = ROOT / "outputs" / "step38_tethered_no_free_body_guard"
    write_csv_rows(out_dir / "tethered_no_free_body_guard.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "tethered_no_free_body_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 tethered no-free-body guard finished"
    write_log("logs/step38_tethered_no_free_body_guard.log", [marker, f"guard_pass={summary['guard_pass']}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
