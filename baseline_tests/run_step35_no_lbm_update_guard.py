import os
from pathlib import Path

from step35_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log


SCAN_PATHS = [
    "src/wall_velocity_config.py",
    "src/wall_velocity_field.py",
    "src/wall_velocity_quality.py",
    "src/wall_velocity_consistency.py",
    "configs/step35_squid_proxy_wall_velocity_field.json",
    "configs/step35_squid_proxy_wall_velocity_sampling.json",
]


def main():
    os.chdir(ROOT)
    rows = build_guard_rows()
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "lbm_population_update_count": value_for(rows, "lbm_population_update_count"),
        "moving_bounceback_update_count": value_for(rows, "moving_bounceback_update_count"),
        "driver_integration_enabled_count": value_for(rows, "driver_integration_enabled_count"),
        "apply_to_lbm_count": value_for(rows, "apply_to_lbm_count"),
    }
    summary["guard_pass"] = (
        summary["pass_count"] == summary["row_count"]
        and int(summary["lbm_population_update_count"]) == 0
        and int(summary["moving_bounceback_update_count"]) == 0
        and int(summary["driver_integration_enabled_count"]) == 0
        and int(summary["apply_to_lbm_count"]) == 0
    )
    if not bool(summary["guard_pass"]):
        raise RuntimeError(f"Step 35 no LBM update guard failed: {summary}")

    out_dir = ROOT / "outputs" / "step35_no_lbm_update_guard"
    write_csv_rows(out_dir / "no_lbm_update_guard.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "no_lbm_update_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 35 no LBM update guard finished"
    write_log(
        "logs/step35_no_lbm_update_guard.log",
        [
            marker,
            f"guard_pass={summary['guard_pass']}",
            f"lbm_population_update_count={summary['lbm_population_update_count']}",
            f"moving_bounceback_update_count={summary['moving_bounceback_update_count']}",
        ],
    )
    print(f"guard_pass={summary['guard_pass']}")
    print(marker)


def build_guard_rows() -> list[dict]:
    joined_source = "\n".join(read_text(path) for path in SCAN_PATHS)
    config = read_json("configs/step35_squid_proxy_wall_velocity_field.json")
    wall_rows_payload = read_optional_json("outputs/step35_wall_velocity_field/wall_velocity_field.json")
    wall_rows = wall_rows_payload.get("rows", []) if wall_rows_payload else []
    return [
        guard_row("lbm_population_update_count", count_population_write_patterns(joined_source), 0, "Step 35 source must not write distribution populations"),
        guard_row("moving_bounceback_update_count", joined_source.count("step_moving_bounceback("), 0, "Step 35 source must not call moving bounce-back updates"),
        guard_row("dynamic_solid_mutation_count", joined_source.count("dynamic_solid") + joined_source.count("solid_velocity"), 0, "Step 35 source must not mutate dynamic solid state"),
        guard_row("projector_mutation_count", joined_source.count("projector."), 0, "Step 35 source must not mutate projector state"),
        guard_row("driver_integration_enabled_count", int(bool(config["driver_integration_enabled"])) + sum(1 for row in wall_rows if bool(row["driver_integration_enabled"])), 0, "driver integration must remain disabled"),
        guard_row("apply_to_lbm_count", int(bool(config["apply_to_lbm"])) + sum(1 for row in wall_rows if bool(row["apply_to_lbm"])), 0, "Step 35 must not apply diagnostics to LBM"),
        guard_row(
            "lbm_population_update_enabled_count",
            int(bool(config["lbm_population_update_enabled"])) + sum(1 for row in wall_rows if bool(row["lbm_population_update_enabled"])),
            0,
            "LBM population update flag must remain disabled",
        ),
        guard_row(
            "moving_bounceback_update_enabled_count",
            int(bool(config["moving_bounceback_update_enabled"])) + sum(1 for row in wall_rows if bool(row["moving_bounceback_update_enabled"])),
            0,
            "moving bounce-back update flag must remain disabled",
        ),
    ]


def guard_row(check: str, observed: int, expected: int, notes: str) -> dict:
    return {"check": check, "observed": int(observed), "expected": int(expected), "pass": int(observed) == int(expected), "notes": notes}


def count_population_write_patterns(text: str) -> int:
    patterns = ("lbm.f =", "lbm.f[", "lbm.f_next =", "lbm.f_next[", ".f =", ".f[", ".f_next =", ".f_next[")
    return sum(text.count(pattern) for pattern in patterns)


def value_for(rows: list[dict], check: str) -> int:
    matches = [row for row in rows if row["check"] == check]
    return int(matches[0]["observed"]) if matches else 0


def read_optional_json(path: str) -> dict:
    resolved = ROOT / path
    if not resolved.is_file():
        return {}
    return read_json(path)


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8") if (ROOT / relative_path).is_file() else ""


if __name__ == "__main__":
    main()
