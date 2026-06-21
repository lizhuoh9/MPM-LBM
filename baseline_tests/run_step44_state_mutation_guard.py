import os

from step44_common import STEP44_CONFIG_PATH, ROOT, write_log


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_state_guard import compute_state_mutation_guard, write_state_mutation_guard

    payload = compute_state_mutation_guard(STEP44_CONFIG_PATH, root=ROOT)
    summary = payload["summary"]
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 44 state mutation guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_state_mutation_guard"
    write_state_mutation_guard(payload, out_dir / "state_mutation_guard.csv", out_dir / "state_mutation_guard.json")
    marker = "[OK] Step 44 state mutation guard finished"
    write_log("logs/step44_state_mutation_guard.log", [marker, f"guard_pass={summary['guard_pass']}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
