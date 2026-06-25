from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.mpm_lbm.evidence.step107_common import read_json


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def build_step107_output_guard(
    root: Path,
    policy_path: str = "configs/step107_output_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [output_row(root, path, policy) for path in step107_output_files(root)]
    protected_external = git_changed_paths(root, "external/taichi_LBM3D")
    protected_real_geometry = git_changed_paths(root, "data/real_geometry_candidates")
    total_size_mb = sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0)
    large_file_count = sum(1 for row in rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"]))
    validation_claims = pattern_rows(root, policy["validation_claim_patterns"])
    direct_claims = pattern_rows(root, policy["direct_equivalence_claim_patterns"])
    summary = {
        "artifact_budget_pass": bool(total_size_mb < float(policy["max_step107_total_size_mb"]) and large_file_count == 0),
        "direct_equivalence_claim_count": len(direct_claims),
        "official_case_data_h5_count": sum(1 for row in rows if is_case_data_file(row, policy)),
        "official_case_file_count": sum(1 for row in rows if is_case_file(row, policy)),
        "official_journal_file_count": sum(1 for row in rows if row["extension"] in set(policy["journal_suffixes"])),
        "official_mesh_file_count": sum(1 for row in rows if is_mesh_file(row, policy)),
        "official_png_committed_count": sum(1 for row in rows if row["extension"] in set(policy["image_extensions"])),
        "output_guard_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_absolute_path_rows(root)),
        "private_fluent_csv_committed_count": sum(1 for row in rows if row["path"].startswith("benchmarks/private/")),
        "protected_external_edit_count": len(protected_external),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "row_count": len(rows),
        "step107_forbidden_file_count": sum(1 for row in rows if row["forbidden"]),
        "step107_large_file_count": large_file_count,
        "step107_total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "step107_total_size_mb": total_size_mb,
        "step107_video_count": sum(1 for row in rows if row["extension"] in set(policy["video_extensions"])),
        "validation_claim_count": len(validation_claims),
    }
    summary["output_guard_pass"] = bool(
        rows
        and summary["row_count"] == summary["pass_count"]
        and summary["official_case_file_count"] == 0
        and summary["official_mesh_file_count"] == 0
        and summary["official_journal_file_count"] == 0
        and summary["official_case_data_h5_count"] == 0
        and summary["official_png_committed_count"] == 0
        and summary["private_fluent_csv_committed_count"] == 0
        and summary["validation_claim_count"] == 0
        and summary["direct_equivalence_claim_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step107_forbidden_file_count"] == 0
        and summary["step107_video_count"] == 0
        and summary["artifact_budget_pass"]
    )
    return rows, summary


def output_row(root: Path, path: Path, policy: dict) -> dict:
    rel = path.relative_to(root).as_posix()
    extension = path.suffix.lower()
    forbidden = is_forbidden(rel, policy)
    large = path.stat().st_size > int(policy["large_file_threshold_bytes"])
    return {
        "extension": extension,
        "forbidden": forbidden,
        "pass": not forbidden and not large,
        "path": rel,
        "size_bytes": int(path.stat().st_size),
    }


def step107_output_files(root: Path) -> list[Path]:
    files = []
    for base in (root / "benchmarks" / "public" / "fluent_fsi_2way_digitized", root / "configs", root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith(("outputs/step107_output_guard/", "outputs/step107_artifact_manifest/")):
                continue
            if rel.startswith(
                (
                    "benchmarks/public/fluent_fsi_2way_digitized/",
                    "configs/step107_",
                    "outputs/step107_",
                    "logs/step107_",
                )
            ):
                files.append(path)
    return sorted(files)


def is_forbidden(rel: str, policy: dict) -> bool:
    lower = rel.lower()
    if any(token.lower() in lower for token in policy["forbidden_filename_tokens"]):
        return True
    for protected in policy["protected_prefixes"]:
        if rel.startswith(protected):
            return True
    return False


def is_case_data_file(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    return lower.endswith(tuple(suffix.lower() for suffix in policy["case_data_suffixes"]))


def is_case_file(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(lower).name in names or lower.endswith((".cas", ".cas.h5", ".zip"))


def is_mesh_file(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    return lower.endswith(tuple(suffix.lower() for suffix in policy["mesh_suffixes"]))


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in step107_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if PRIVATE_ABSOLUTE_RE.search(text):
            paths.append(path.relative_to(root).as_posix())
    return paths


def pattern_rows(root: Path, patterns: list[str]) -> list[str]:
    compiled = [re.compile(re.escape(pattern), re.IGNORECASE) for pattern in patterns]
    paths = []
    for path in step107_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        if path.name == "step107_output_guard_policy.json":
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if any(pattern.search(text) for pattern in compiled):
            paths.append(path.relative_to(root).as_posix())
    return paths


def git_changed_paths(root: Path, pathspec: str) -> list[str]:
    result = subprocess.run(["git", "status", "--short", "--", pathspec], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return [f"git_status_error:{result.stderr.strip()}"]
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
