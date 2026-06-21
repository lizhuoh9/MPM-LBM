from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text


def build_step69_no_simulation_audit(
    root: Path,
    policy_path: str = "configs/step69_no_simulation_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [python_scan_row(root, policy, path) for path in policy["scan_python_paths"]]
    forbidden_dirs = [path for path in policy["forbidden_output_directories"] if (root / path).exists()]
    related_files = step69_related_files(root)
    vtr_files = [path for path in related_files if path.lower().endswith(".vtr")]
    particle_npy_files = [
        path
        for path in related_files
        if path.lower().endswith(".npy") and "particle" in path.lower()
    ]
    for path in forbidden_dirs:
        rows.append({"check": "forbidden_output_directory_absent", "path": path, "forbidden_token_count": 1, "pass": False})
    for path in vtr_files:
        rows.append({"check": "no_step69_vtr", "path": path, "forbidden_token_count": 1, "pass": False})
    for path in particle_npy_files:
        rows.append({"check": "no_step69_particle_npy", "path": path, "forbidden_token_count": 1, "pass": False})
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "forbidden_python_token_count": sum(int(row.get("forbidden_token_count", 0)) for row in rows),
        "forbidden_output_directory_count": len(forbidden_dirs),
        "step69_vtr_count": len(vtr_files),
        "step69_particle_npy_count": len(particle_npy_files),
        "driver_run_detected": any(
            token == policy["forbidden_python_tokens"][0]
            for row in rows
            for token in row.get("found_tokens", [])
        ),
        "no_simulation_audit_pass": False,
    }
    summary["no_simulation_audit_pass"] = bool(
        rows
        and all(row["pass"] for row in rows)
        and summary["forbidden_python_token_count"] == 0
        and summary["forbidden_output_directory_count"] == 0
        and summary["step69_vtr_count"] == 0
        and summary["step69_particle_npy_count"] == 0
        and not summary["driver_run_detected"]
    )
    return rows, summary


def python_scan_row(root: Path, policy: dict, relative_path: str) -> dict:
    path = root / relative_path
    text = read_text(path)
    found_tokens = [token for token in policy["forbidden_python_tokens"] if token in text]
    exists = path.is_file()
    return {
        "check": "python_no_simulation_tokens",
        "path": relative_path,
        "file_exists": exists,
        "found_tokens": found_tokens,
        "forbidden_token_count": len(found_tokens),
        "pass": bool(exists and not found_tokens),
    }


def step69_related_files(root: Path) -> list[str]:
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "step69" in rel.lower():
            rows.append(rel)
    return sorted(rows)
