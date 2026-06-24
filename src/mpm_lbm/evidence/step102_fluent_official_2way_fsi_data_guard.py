from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def build_step102_fluent_official_2way_fsi_data_guard(
    root: Path,
    policy_path: str = "configs/step102_fluent_official_2way_fsi_data_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    repo_paths = git_repo_paths(root)
    official_archive = matching_basenames(repo_paths, set(policy["official_archive_names"]))
    official_mesh = matching_basenames(repo_paths, set(policy["mesh_names"]))
    official_journal = matching_basenames(repo_paths, set(policy["journal_names"]))
    fluent_case_data = matching_suffixes(repo_paths, tuple(policy["case_data_suffixes"]))
    private_paths = [path for path in repo_paths if any(path.startswith(prefix) for prefix in policy["private_prefixes"])]
    large_excerpts = large_verbatim_excerpt_rows(root, policy)
    private_absolute_paths = private_absolute_path_rows(root)
    ansys_file_rows = sorted(set(official_archive + official_mesh + official_journal + fluent_case_data + private_paths))
    summary = {
        "ansys_large_verbatim_excerpt_count": len(large_excerpts),
        "ansys_proprietary_file_committed_count": len(ansys_file_rows),
        "artifact_budget_pass": False,
        "fluent_case_data_committed_count": len(fluent_case_data),
        "local_data_committed": bool(ansys_file_rows),
        "local_data_required": True,
        "official_archive_committed_count": len(official_archive),
        "official_journal_committed_count": len(official_journal),
        "official_mesh_committed_count": len(official_mesh),
        "private_absolute_path_count": len(private_absolute_paths),
        "private_benchmark_path_committed_count": len(private_paths),
        "row_count": 0,
        "step102_fluent_official_2way_fsi_data_guard_pass": False,
    }
    summary["artifact_budget_pass"] = bool(
        summary["official_archive_committed_count"] == 0
        and summary["official_mesh_committed_count"] == 0
        and summary["official_journal_committed_count"] == 0
        and summary["fluent_case_data_committed_count"] == 0
        and summary["private_benchmark_path_committed_count"] == 0
        and summary["ansys_proprietary_file_committed_count"] == 0
        and summary["ansys_large_verbatim_excerpt_count"] == 0
        and summary["private_absolute_path_count"] == 0
    )
    summary["step102_fluent_official_2way_fsi_data_guard_pass"] = bool(
        summary["artifact_budget_pass"]
        and summary["local_data_required"] is True
        and summary["local_data_committed"] is False
    )
    rows = [
        guard_row("official_archive_committed_count", summary["official_archive_committed_count"], 0),
        guard_row("official_mesh_committed_count", summary["official_mesh_committed_count"], 0),
        guard_row("official_journal_committed_count", summary["official_journal_committed_count"], 0),
        guard_row("fluent_case_data_committed_count", summary["fluent_case_data_committed_count"], 0),
        guard_row("private_benchmark_path_committed_count", summary["private_benchmark_path_committed_count"], 0),
        guard_row("ansys_proprietary_file_committed_count", summary["ansys_proprietary_file_committed_count"], 0),
        guard_row("ansys_large_verbatim_excerpt_count", summary["ansys_large_verbatim_excerpt_count"], 0),
        guard_row("private_absolute_path_count", summary["private_absolute_path_count"], 0),
        guard_row("local_data_required", summary["local_data_required"], True),
        guard_row("local_data_committed", summary["local_data_committed"], False),
    ]
    summary["row_count"] = len(rows)
    summary["pass_count"] = sum(1 for row in rows if row["pass"])
    return rows, summary


def guard_row(check: str, actual, expected) -> dict:
    return {
        "actual": actual,
        "check": check,
        "expected": expected,
        "pass": actual == expected,
    }


def git_repo_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"git_ls_files_error:{result.stderr.strip()}"]
    return sorted(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())


def matching_basenames(paths: list[str], names: set[str]) -> list[str]:
    return [path for path in paths if Path(path).name in names]


def matching_suffixes(paths: list[str], suffixes: tuple[str, ...]) -> list[str]:
    return [path for path in paths if path.lower().endswith(tuple(suffix.lower() for suffix in suffixes))]


def large_verbatim_excerpt_rows(root: Path, policy: dict) -> list[str]:
    rows = []
    patterns = policy["ansys_large_verbatim_excerpt_patterns"]
    for path in step102_text_files(root):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if any(pattern in text for pattern in patterns):
            rows.append(path.relative_to(root).as_posix())
    return rows


def private_absolute_path_rows(root: Path) -> list[str]:
    rows = []
    for path in step102_text_files(root):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if PRIVATE_ABSOLUTE_RE.search(text):
            rows.append(path.relative_to(root).as_posix())
    return rows


def step102_text_files(root: Path):
    for base in (root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if not (rel.startswith("outputs/step102_") or rel.startswith("logs/step102_")):
                continue
            if path.suffix.lower() in {".json", ".csv", ".log"}:
                yield path


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
