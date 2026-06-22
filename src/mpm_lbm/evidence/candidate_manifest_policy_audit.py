from __future__ import annotations

import json
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.geometry.candidate_manifest import (
    candidate_manifest_row,
    validate_candidate_descriptor,
    write_candidate_manifest,
)
from src.mpm_lbm.sim.geometry.fingerprint import fingerprint_geometry_file


def build_step74_candidate_manifest_policy_audit(
    root: Path,
    policy_path: str = "configs/step74_candidate_manifest_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    fixture_path = root / policy["synthetic_fixture_file"]
    descriptor_path = root / policy["synthetic_descriptor_file"]
    write_synthetic_fixture(fixture_path)
    write_descriptor(descriptor_path, synthetic_descriptor(policy["synthetic_fixture_file"]))

    valid_row = candidate_manifest_row(descriptor_path, root=root)
    write_candidate_manifest([valid_row], root / policy["synthetic_manifest_csv"], root / policy["synthetic_manifest_json"])

    rows = [
        bool_row("valid_small_synthetic_manifest_pass", bool(valid_row["manifest_pass"]), True, "valid_synthetic_fixture"),
        bool_row("absolute_path_redaction_pass", absolute_path_redaction_pass(fixture_path), True, "fingerprint_redaction"),
        bool_row("large_file_policy_enforced", large_file_policy_enforced(root, policy), True, "large_policy_probe"),
        bool_row("unavailable_source_policy_enforced", unavailable_source_policy_enforced(), True, "source_available_false"),
        bool_row("duplicate_candidate_id_rejected", duplicate_candidate_id_rejected(valid_row, root, policy), True, "duplicate_manifest"),
    ]
    protected_files = [
        path for path in step74_files(root) if any(path.startswith(prefix) for prefix in policy["protected_prefixes"])
    ]
    rows.extend(absence_row("no_protected_step74_manifest_file", path) for path in protected_files)
    synthetic_fixture_count = int(fixture_path.exists())
    summary = {
        "absolute_path_redaction_pass": rows[1]["pass"],
        "candidate_manifest_policy_audit_pass": False,
        "duplicate_candidate_id_rejected": rows[4]["pass"],
        "large_file_policy_enforced": rows[2]["pass"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "real_geometry_candidate_edit_count": sum(
            1 for path in step74_files(root) if path.startswith("data/real_geometry_candidates/")
        ),
        "row_count": len(rows),
        "synthetic_fixture_count": synthetic_fixture_count,
        "unavailable_source_policy_enforced": rows[3]["pass"],
    }
    summary["candidate_manifest_policy_audit_pass"] = bool(
        summary["pass_count"] == summary["row_count"]
        and summary["absolute_path_redaction_pass"]
        and summary["large_file_policy_enforced"]
        and summary["unavailable_source_policy_enforced"]
        and summary["duplicate_candidate_id_rejected"]
        and summary["synthetic_fixture_count"] <= 1
        and summary["real_geometry_candidate_edit_count"] == 0
    )
    return rows, summary


def synthetic_descriptor(source_file: str) -> dict:
    return {
        "artifact_policy": "do_not_commit_large_raw_geometry",
        "candidate_id": "synthetic_box_fixture",
        "commit_policy": "small_controlled_fixture_allowed",
        "geometry_type": "mesh",
        "license_status": "synthetic",
        "n_particles": 128,
        "normalize_to_domain": True,
        "padding": 0.05,
        "preserve_aspect_ratio": True,
        "quality_check_enabled": True,
        "quality_check_strict": True,
        "source_available": True,
        "source_file": source_file,
        "source_policy": "synthetic_fixture",
        "validation_scope": "intake_qa_normalization_sampling_projection_only",
    }


def write_synthetic_fixture(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("step74 synthetic geometry boundary fixture\n", encoding="utf-8")


def write_descriptor(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def absolute_path_redaction_pass(path: Path) -> bool:
    fingerprint = fingerprint_geometry_file(path.resolve(), root=None, redact_absolute=True)
    return bool(fingerprint["path"].startswith("<redacted>/") and fingerprint["path_policy"] == "absolute_redacted")


def large_file_policy_enforced(root: Path, policy: dict) -> bool:
    probe = root / policy["large_probe_path"]
    descriptor = root / "outputs" / "step74_synthetic_geometry_fixture" / "large_policy_probe_descriptor.json"
    try:
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_bytes(b"x" * 1_000_001)
        write_descriptor(descriptor, synthetic_descriptor(policy["large_probe_path"]))
        try:
            candidate_manifest_row(descriptor, root=root)
        except ValueError:
            return True
        return False
    finally:
        if probe.exists():
            probe.unlink()
        if descriptor.exists():
            descriptor.unlink()


def unavailable_source_policy_enforced() -> bool:
    payload = synthetic_descriptor("outputs/step74_synthetic_geometry_fixture/missing_fixture.txt")
    payload["source_available"] = False
    payload["commit_policy"] = "small_controlled_fixture_allowed"
    try:
        validate_candidate_descriptor(payload)
    except ValueError:
        return True
    return False


def duplicate_candidate_id_rejected(row: dict, root: Path, policy: dict) -> bool:
    duplicate_path = root / "outputs" / "step74_candidate_manifest_policy_audit" / "duplicate_probe.csv"
    duplicate_json = root / "outputs" / "step74_candidate_manifest_policy_audit" / "duplicate_probe.json"
    try:
        write_candidate_manifest([row, dict(row)], duplicate_path, duplicate_json)
    except ValueError:
        return True
    return False


def bool_row(check: str, actual, expected, path: str) -> dict:
    return {"actual": actual, "check": check, "expected": expected, "pass": actual == expected, "path": path}


def absence_row(check: str, path: str) -> dict:
    return {"actual": True, "check": check, "expected": False, "pass": False, "path": path}


def step74_files(root: Path) -> list[str]:
    rows = []
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if "step74" in rel.lower() or "real_geometry_data_boundary" in rel.lower():
                rows.append(rel)
    return rows
