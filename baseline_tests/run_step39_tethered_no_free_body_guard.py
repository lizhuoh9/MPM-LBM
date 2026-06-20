import os

from step39_common import ROOT, STEP39_DRIVER_CONFIGS, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.tethered_cycle_diagnostics import guard_rows, summarize_multicycle_tethered_guard


def main():
    os.chdir(ROOT)
    configs = [read_json(path) for path in STEP39_DRIVER_CONFIGS]
    summary = summarize_multicycle_tethered_guard(configs, ROOT / "outputs" / "step39_multicycle_driver")
    rows = guard_rows(summary)
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 39 tethered no-free-body guard failed: {summary}")

    out_dir = ROOT / "outputs" / "step39_tethered_no_free_body_guard"
    write_csv_rows(out_dir / "tethered_no_free_body_guard.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "tethered_no_free_body_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 tethered no-free-body guard finished"
    write_log("logs/step39_tethered_no_free_body_guard.log", [marker, f"guard_pass={summary['guard_pass']}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
