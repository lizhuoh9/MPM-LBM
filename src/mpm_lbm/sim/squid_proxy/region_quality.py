import math

import numpy as np

from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.squid_proxy.regions import mantle_normalized_radius
from src.mpm_lbm.sim.squid_proxy.region_config import (
    FORBIDDEN_REGION_CLAIMS,
    REQUIRED_REGION_IDS,
    SquidProxyRegionConfig,
    validate_squid_region_config,
)


def evaluate_region_quality(
    geometry_config: GeometryConfig,
    region_config: SquidProxyRegionConfig,
    points: np.ndarray,
    masks: dict[str, np.ndarray],
    region_rows: list[dict],
) -> tuple[list[dict], dict]:
    config_validation = validate_squid_region_config(region_config)
    row_by_id = {row["region_id"]: row for row in region_rows}
    rows = [
        _check("schema_pass", bool(config_validation["schema_pass"]), config_validation["present_required_region_count"], "region schema validation"),
        _check("no_required_region_missing", not config_validation["missing_required_regions"], ",".join(config_validation["missing_required_regions"]), "required region IDs present"),
        _check("region_ids_unique", bool(config_validation["region_ids_unique"]), config_validation["duplicate_region_ids"], "region IDs are stable and unique"),
        _check("all_masks_boolean", all(np.asarray(masks[region_id]).dtype == np.bool_ for region_id in REQUIRED_REGION_IDS), len(masks), "masks use boolean dtype"),
        _check("all_bboxes_finite", all(bool(row_by_id[region_id]["bbox_finite"]) for region_id in REQUIRED_REGION_IDS), len(region_rows), "every required region has finite bbox"),
        _check("solid_regions_positive", _all_positive(row_by_id, ("mantle_outer", "head_proxy", "arms_proxy", "left_fin_proxy", "right_fin_proxy")), "solid/appendage/fin regions", "required solid-like regions have positive counts"),
        _check("cavity_proxy_positive", int(row_by_id["mantle_cavity_proxy"]["point_count"]) > 0, row_by_id["mantle_cavity_proxy"]["point_count"], "mantle cavity proxy has positive count"),
        _check("funnel_outlet_positive", int(row_by_id["funnel_outlet_proxy"]["point_count"]) > 0, row_by_id["funnel_outlet_proxy"]["point_count"], "funnel outlet proxy has positive count"),
        _check("mantle_cavity_inside_mantle", _subset(masks["mantle_cavity_proxy"], masks["mantle_outer"]), "recorded", "mantle cavity proxy is inside mantle outer proxy"),
        _check("funnel_outlet_near_mantle_boundary", _funnel_near_boundary(geometry_config, points, masks["funnel_outlet_proxy"]), "recorded", "funnel outlet proxy lies near mantle boundary proxy"),
        _check("no_forbidden_region_claims", _forbidden_claim_count(region_config) == 0, _forbidden_claim_count(region_config), "region notes avoid validation and actuation claims"),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    summary = {
        "row_count": len(rows),
        "pass_count": len(rows) - len(failed),
        "required_region_count": len(REQUIRED_REGION_IDS),
        "region_quality_pass": len(failed) == 0,
        "missing_required_region_count": len(config_validation["missing_required_regions"]),
        "forbidden_claim_count": _forbidden_claim_count(region_config),
        "mantle_outer_count": int(row_by_id["mantle_outer"]["point_count"]),
        "mantle_cavity_proxy_count": int(row_by_id["mantle_cavity_proxy"]["point_count"]),
        "funnel_outlet_proxy_count": int(row_by_id["funnel_outlet_proxy"]["point_count"]),
        "head_proxy_count": int(row_by_id["head_proxy"]["point_count"]),
        "arms_proxy_count": int(row_by_id["arms_proxy"]["point_count"]),
        "left_fin_proxy_count": int(row_by_id["left_fin_proxy"]["point_count"]),
        "right_fin_proxy_count": int(row_by_id["right_fin_proxy"]["point_count"]),
    }
    return rows, summary


def overlap_matrix_rows(masks: dict[str, np.ndarray], region_config: SquidProxyRegionConfig) -> list[dict]:
    allowed = {tuple(sorted(pair)) for pair in region_config.allowed_overlap_pairs}
    rows = []
    for region_a in REQUIRED_REGION_IDS:
        mask_a = np.asarray(masks[region_a], dtype=bool)
        count_a = int(np.count_nonzero(mask_a))
        for region_b in REQUIRED_REGION_IDS:
            mask_b = np.asarray(masks[region_b], dtype=bool)
            overlap_count = int(np.count_nonzero(mask_a & mask_b))
            diagonal = region_a == region_b
            pair = tuple(sorted((region_a, region_b)))
            allowed_overlap = diagonal or pair in allowed
            rows.append(
                {
                    "region_a": region_a,
                    "region_b": region_b,
                    "overlap_count": overlap_count,
                    "fraction_of_region_a": float(overlap_count) / float(count_a) if count_a else 0.0,
                    "diagonal": diagonal,
                    "allowed_overlap": allowed_overlap,
                    "unintended_overlap": (not diagonal) and overlap_count > 0 and not allowed_overlap,
                }
            )
    return rows


def summarize_overlap_diagnostics(overlap_rows: list[dict], region_rows: list[dict]) -> dict:
    count_by_region = {row["region_id"]: int(row["point_count"]) for row in region_rows}
    diagonal_mismatches = [
        row
        for row in overlap_rows
        if row["diagonal"] and int(row["overlap_count"]) != count_by_region[row["region_a"]]
    ]
    unintended = [row for row in overlap_rows if row["unintended_overlap"]]
    finite = all(math.isfinite(float(row["fraction_of_region_a"])) for row in overlap_rows)
    intentional = [
        row
        for row in overlap_rows
        if not row["diagonal"] and int(row["overlap_count"]) > 0 and bool(row["allowed_overlap"])
    ]
    return {
        "row_count": len(overlap_rows),
        "matrix_finite": finite,
        "diagonal_match_count": len(REQUIRED_REGION_IDS) - len(diagonal_mismatches),
        "diagonal_mismatch_count": len(diagonal_mismatches),
        "intentional_overlap_count": len(intentional),
        "unintended_overlap_count": len(unintended),
        "overlap_pass": finite and not diagonal_mismatches and not unintended,
        "scope_note": "Step 30 overlap diagnostics document semantic proxy overlaps only.",
    }


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _all_positive(row_by_id: dict[str, dict], region_ids: tuple[str, ...]) -> bool:
    return all(int(row_by_id[region_id]["point_count"]) > 0 for region_id in region_ids)


def _subset(child_mask: np.ndarray, parent_mask: np.ndarray) -> bool:
    child = np.asarray(child_mask, dtype=bool)
    parent = np.asarray(parent_mask, dtype=bool)
    return bool(np.all(parent[child]))


def _funnel_near_boundary(geometry_config: GeometryConfig, points: np.ndarray, funnel_mask: np.ndarray) -> bool:
    selected = np.asarray(points, dtype=np.float64)[np.asarray(funnel_mask, dtype=bool)]
    if len(selected) == 0:
        return False
    normalized = mantle_normalized_radius(geometry_config, selected)
    return bool(float(np.mean(normalized)) >= 0.68 and float(np.max(normalized)) <= 1.05)


def _forbidden_claim_count(region_config: SquidProxyRegionConfig) -> int:
    blob = " ".join([region_config.scope_note] + [region.notes for region in region_config.regions]).lower()
    return sum(1 for claim in FORBIDDEN_REGION_CLAIMS if claim in blob)
