from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json


UTF8_BOM = b"\xef\xbb\xbf"


def build_encoding_policy_audit(
    root: Path,
    policy_path: str = "configs/step63_encoding_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    files = sorted({path for pattern in policy["scan_globs"] for path in root.glob(pattern) if path.is_file()})
    rows = [encoding_row(path, root) for path in files]
    summary = {
        "file_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "utf8_bom_count": sum(1 for row in rows if row["has_utf8_bom"]),
        "non_utf8_readable_count": sum(1 for row in rows if not row["utf8_decodable"]),
        "encoding_policy_audit_pass": False,
    }
    summary["encoding_policy_audit_pass"] = bool(
        summary["file_count"] > 0
        and summary["file_count"] == summary["pass_count"]
        and summary["utf8_bom_count"] == 0
        and summary["non_utf8_readable_count"] == 0
    )
    return rows, summary


def encoding_row(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    has_bom = data.startswith(UTF8_BOM)
    error = ""
    try:
        data.decode("utf-8")
        decodable = True
    except UnicodeDecodeError as exc:
        decodable = False
        error = str(exc)
    return {
        "path": path.relative_to(root).as_posix(),
        "has_utf8_bom": has_bom,
        "utf8_decodable": decodable,
        "pass": decodable and not has_bom,
        "error": error,
    }
