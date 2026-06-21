import os

from step51_common import ROOT, STEP51_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_state_guard import compute_step51_state_mutation_guard, write_step51_state_mutation_guard

    payload = compute_step51_state_mutation_guard(STEP51_CONFIG_PATH, root=ROOT)
    summary = payload["summary"]
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 51 state mutation guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_state_mutation_guard"
    write_step51_state_mutation_guard(payload, out_dir / "state_mutation_guard.csv", out_dir / "state_mutation_guard.json")
    marker = "[OK] Step 51 state mutation guard finished"
    write_log("logs/step51_state_mutation_guard.log", [marker, f"guard_pass={summary['guard_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
