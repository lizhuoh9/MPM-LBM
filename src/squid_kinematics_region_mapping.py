from .squid_region_config import REQUIRED_REGION_IDS


REGION_MAPPING_FIELDS = ["check", "pass", "value", "notes"]


KINEMATIC_REGION_IDS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
)


def validate_kinematics_region_mapping(schedule_config, region_config) -> dict:
    region_by_id = {region.region_id: region for region in region_config.regions}
    required_present = all(region_id in region_by_id for region_id in REQUIRED_REGION_IDS)
    active_regions = [region.region_id for region in region_config.regions if region.active_for_actuation]
    mapping = {
        "required_region_count": len(REQUIRED_REGION_IDS),
        "present_required_region_count": sum(1 for region_id in REQUIRED_REGION_IDS if region_id in region_by_id),
        "all_required_regions_present": required_present,
        "mantle_outer_present": "mantle_outer" in region_by_id,
        "mantle_cavity_proxy_present": "mantle_cavity_proxy" in region_by_id,
        "funnel_outlet_proxy_present": "funnel_outlet_proxy" in region_by_id,
        "kinematic_region_ids": list(KINEMATIC_REGION_IDS),
        "active_for_actuation_region_count": len(active_regions),
        "active_for_actuation_region_ids": active_regions,
        "driver_integration_enabled": bool(schedule_config.driver_integration_enabled),
        "actuation_enabled": bool(schedule_config.actuation_enabled),
        "region_config_geometry_type": region_config.geometry_type,
        "mapping_note": "future mapping only; Step 32 does not enable driver integration or region actuation",
    }
    mapping["mapping_pass"] = bool(
        mapping["all_required_regions_present"]
        and mapping["mantle_outer_present"]
        and mapping["mantle_cavity_proxy_present"]
        and mapping["funnel_outlet_proxy_present"]
        and mapping["active_for_actuation_region_count"] == 0
        and mapping["driver_integration_enabled"] is False
        and mapping["actuation_enabled"] is False
        and region_config.geometry_type == "squid_proxy"
    )
    return mapping


def region_mapping_rows(mapping: dict) -> list[dict]:
    return [
        _row("all_required_regions_present", mapping["all_required_regions_present"], mapping["present_required_region_count"], "all Step 30 region IDs must remain present"),
        _row("mantle_outer_present", mapping["mantle_outer_present"], "mantle_outer", "mantle radius schedule future target exists"),
        _row("mantle_cavity_proxy_present", mapping["mantle_cavity_proxy_present"], "mantle_cavity_proxy", "cavity volume proxy future target exists"),
        _row("funnel_outlet_proxy_present", mapping["funnel_outlet_proxy_present"], "funnel_outlet_proxy", "funnel aperture proxy future target exists"),
        _row("active_for_actuation_disabled", mapping["active_for_actuation_region_count"] == 0, mapping["active_for_actuation_region_count"], "Step 30 regions must remain inactive"),
        _row("driver_integration_disabled", not mapping["driver_integration_enabled"], mapping["driver_integration_enabled"], "Step 32 must not integrate with driver"),
        _row("actuation_disabled", not mapping["actuation_enabled"], mapping["actuation_enabled"], "Step 32 must not enable actuation"),
        _row("mapping_pass", mapping["mapping_pass"], mapping["mapping_pass"], mapping["mapping_note"]),
    ]


def assert_region_mapping(mapping: dict) -> None:
    if not bool(mapping.get("mapping_pass", False)):
        raise RuntimeError(f"Step 32 region mapping failed: {mapping}")


def _row(check: str, passed: bool, value, notes: str) -> dict:
    return {"check": check, "pass": bool(passed), "value": value, "notes": notes}
