from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Optional, Tuple


REQUIRED_REGION_IDS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
    "head_proxy",
    "arms_proxy",
    "left_fin_proxy",
    "right_fin_proxy",
)

VALID_BODY_AXES = ("+x", "-x", "+y", "-y", "+z", "-z")
VALID_REGION_ROLES = (
    "solid_region",
    "cavity_proxy",
    "outlet_proxy",
    "appendage_proxy",
    "fin_proxy",
)

FORBIDDEN_REGION_CLAIMS = (
    "real squid simulation is validated",
    "validated squid swimming",
    "squid actuation is implemented",
    "production-ready sharp-interface fsi",
    "final solver readiness",
    "production mesh repair is complete",
    "automatic remeshing is implemented",
    "strict momentum-conserving fsi is complete",
    "mantle contraction is implemented",
    "funnel actuation is implemented",
    "implements two_phase",
    "implements contact_angle",
)

DEFAULT_SCOPE_NOTE = (
    "procedural squid-like proxy region semantics only; not anatomical validation; "
    "not real squid validation; no actuation or swimming"
)


def _as_float_tuple3(values, name: str) -> Tuple[float, float, float]:
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    result = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in result):
        raise ValueError(f"{name} must be finite")
    return result


def _canonical_pair(pair) -> Tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("allowed overlap pairs must contain exactly two region IDs")
    first, second = str(pair[0]), str(pair[1])
    if first == second:
        raise ValueError("allowed overlap pairs must not contain diagonal pairs")
    return tuple(sorted((first, second)))


@dataclass(frozen=True)
class SquidRegion:
    region_id: str
    name: str
    role: str
    material: str
    parent_id: Optional[str] = None
    active_for_actuation: bool = False
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "SquidRegion":
        return cls(
            region_id=str(payload["region_id"]),
            name=str(payload.get("name", payload["region_id"])),
            role=str(payload["role"]),
            material=str(payload.get("material", "semantic_proxy")),
            parent_id=payload.get("parent_id"),
            active_for_actuation=bool(payload.get("active_for_actuation", False)),
            notes=str(payload.get("notes", "")),
        )


@dataclass(frozen=True)
class SquidProxyRegionConfig:
    geometry_type: str = "squid_proxy"
    body_axis: str = "+y"
    reference_length: float = 1.0
    body_frame_origin: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    scope_note: str = DEFAULT_SCOPE_NOTE
    regions: Tuple[SquidRegion, ...] = ()
    allowed_overlap_pairs: Tuple[Tuple[str, str], ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "reference_length", float(self.reference_length))
        object.__setattr__(
            self,
            "body_frame_origin",
            _as_float_tuple3(self.body_frame_origin, "body_frame_origin"),
        )
        object.__setattr__(
            self,
            "regions",
            tuple(region if isinstance(region, SquidRegion) else SquidRegion.from_dict(region) for region in self.regions),
        )
        object.__setattr__(
            self,
            "allowed_overlap_pairs",
            tuple(sorted({_canonical_pair(pair) for pair in self.allowed_overlap_pairs})),
        )

    @classmethod
    def from_dict(cls, payload: dict) -> "SquidProxyRegionConfig":
        return cls(
            geometry_type=str(payload.get("geometry_type", "squid_proxy")),
            body_axis=str(payload.get("body_axis", "+y")),
            reference_length=float(payload.get("reference_length", 1.0)),
            body_frame_origin=payload.get("body_frame_origin", (0.5, 0.5, 0.5)),
            scope_note=str(payload.get("scope_note", DEFAULT_SCOPE_NOTE)),
            regions=tuple(SquidRegion.from_dict(row) for row in payload.get("regions", ())),
            allowed_overlap_pairs=tuple(tuple(pair) for pair in payload.get("allowed_overlap_pairs", ())),
        )

    @classmethod
    def from_json(cls, path) -> "SquidProxyRegionConfig":
        with Path(path).open("r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["body_frame_origin"] = list(self.body_frame_origin)
        payload["regions"] = [asdict(region) for region in self.regions]
        payload["allowed_overlap_pairs"] = [list(pair) for pair in self.allowed_overlap_pairs]
        return payload


def default_squid_regions() -> Tuple[SquidRegion, ...]:
    return (
        SquidRegion(
            region_id="mantle_outer",
            name="mantle outer proxy",
            role="solid_region",
            material="solid_proxy",
            notes="outer mantle semantic proxy; static region only; not anatomical validation",
        ),
        SquidRegion(
            region_id="mantle_cavity_proxy",
            name="mantle cavity proxy",
            role="cavity_proxy",
            material="void_semantic_proxy",
            parent_id="mantle_outer",
            notes="internal cavity semantics only; static descriptor; not anatomical validation",
        ),
        SquidRegion(
            region_id="funnel_outlet_proxy",
            name="funnel outlet proxy",
            role="outlet_proxy",
            material="outlet_semantic_proxy",
            parent_id="mantle_outer",
            notes="static funnel or siphon outlet semantics only; no prescribed motion",
        ),
        SquidRegion(
            region_id="head_proxy",
            name="head proxy",
            role="solid_region",
            material="solid_proxy",
            notes="coarse head semantic proxy; static region only; not anatomical validation",
        ),
        SquidRegion(
            region_id="arms_proxy",
            name="arms proxy",
            role="appendage_proxy",
            material="solid_proxy",
            parent_id="head_proxy",
            notes="coarse arms semantic proxy; static region only; not anatomical validation",
        ),
        SquidRegion(
            region_id="left_fin_proxy",
            name="left fin proxy",
            role="fin_proxy",
            material="solid_proxy",
            parent_id="mantle_outer",
            notes="optional left fin semantic proxy; static region only",
        ),
        SquidRegion(
            region_id="right_fin_proxy",
            name="right fin proxy",
            role="fin_proxy",
            material="solid_proxy",
            parent_id="mantle_outer",
            notes="optional right fin semantic proxy; static region only",
        ),
    )


def default_allowed_overlap_pairs() -> Tuple[Tuple[str, str], ...]:
    return (
        ("mantle_outer", "mantle_cavity_proxy"),
        ("mantle_outer", "funnel_outlet_proxy"),
        ("mantle_outer", "head_proxy"),
        ("mantle_outer", "left_fin_proxy"),
        ("mantle_outer", "right_fin_proxy"),
        ("head_proxy", "arms_proxy"),
        ("head_proxy", "funnel_outlet_proxy"),
    )


def default_squid_proxy_region_config() -> SquidProxyRegionConfig:
    return SquidProxyRegionConfig(
        geometry_type="squid_proxy",
        body_axis="+y",
        reference_length=1.0,
        body_frame_origin=(0.5, 0.5, 0.5),
        scope_note=DEFAULT_SCOPE_NOTE,
        regions=default_squid_regions(),
        allowed_overlap_pairs=default_allowed_overlap_pairs(),
    )


def load_squid_proxy_region_config(path) -> SquidProxyRegionConfig:
    return SquidProxyRegionConfig.from_json(path)


def validate_squid_region_config(config: SquidProxyRegionConfig) -> dict:
    region_ids = [region.region_id for region in config.regions]
    required = set(REQUIRED_REGION_IDS)
    present = set(region_ids)
    missing = sorted(required - present)
    duplicates = sorted({region_id for region_id in region_ids if region_ids.count(region_id) > 1})
    note_blob = " ".join([config.scope_note] + [region.notes for region in config.regions]).lower()
    forbidden_claims = [claim for claim in FORBIDDEN_REGION_CLAIMS if claim in note_blob]
    valid_roles = [region.role in VALID_REGION_ROLES for region in config.regions]
    active_regions = [region.region_id for region in config.regions if region.active_for_actuation]
    nonempty_fields = [
        bool(region.region_id and region.name and region.role and region.material and region.notes)
        for region in config.regions
    ]
    known_overlap_ids = all(first in present and second in present for first, second in config.allowed_overlap_pairs)
    result = {
        "geometry_type": config.geometry_type,
        "required_region_count": len(REQUIRED_REGION_IDS),
        "region_count": len(config.regions),
        "present_required_region_count": len(required & present),
        "missing_required_regions": missing,
        "duplicate_region_ids": duplicates,
        "region_ids_unique": len(duplicates) == 0,
        "body_axis": config.body_axis,
        "body_axis_valid": config.body_axis in VALID_BODY_AXES,
        "reference_length": config.reference_length,
        "reference_length_positive": math.isfinite(config.reference_length) and config.reference_length > 0.0,
        "body_frame_origin_finite": all(math.isfinite(value) for value in config.body_frame_origin),
        "scope_note_mentions_not_anatomical_validation": "not anatomical validation" in config.scope_note.lower(),
        "roles_valid": all(valid_roles),
        "region_fields_nonempty": all(nonempty_fields),
        "actuation_disabled_count": len(config.regions) - len(active_regions),
        "active_for_actuation_region_ids": active_regions,
        "allowed_overlap_pair_count": len(config.allowed_overlap_pairs),
        "allowed_overlap_ids_known": known_overlap_ids,
        "forbidden_claims": forbidden_claims,
        "forbidden_claim_count": len(forbidden_claims),
    }
    result["schema_pass"] = (
        config.geometry_type == "squid_proxy"
        and result["present_required_region_count"] == result["required_region_count"]
        and result["region_ids_unique"]
        and result["body_axis_valid"]
        and result["reference_length_positive"]
        and result["body_frame_origin_finite"]
        and result["scope_note_mentions_not_anatomical_validation"]
        and result["roles_valid"]
        and result["region_fields_nonempty"]
        and result["actuation_disabled_count"] == result["region_count"]
        and result["allowed_overlap_ids_known"]
        and result["forbidden_claim_count"] == 0
    )
    return result
