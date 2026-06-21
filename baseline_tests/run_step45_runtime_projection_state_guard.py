import os

from step45_common import ROOT, STEP45_CONFIG_PATH, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_projection_state_guard import compute_runtime_projection_state_guard, write_runtime_projection_state_guard

    payload = compute_runtime_projection_state_guard(STEP45_CONFIG_PATH, root=ROOT)
    summary = payload["summary"]
    if not summary["guard_pass"]:
        raise RuntimeError(f"Step 45 runtime projection state guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step45_runtime_projection_state_guard"
    write_runtime_projection_state_guard(payload, out_dir / "runtime_projection_state_guard.csv", out_dir / "runtime_projection_state_guard.json")
    marker = "[OK] Step 45 runtime projection state guard finished"
    write_log("logs/step45_runtime_projection_state_guard.log", [marker, f"guard_pass={summary['guard_pass']}"])
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
