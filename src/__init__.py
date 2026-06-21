"""Local MPM-LBM compatibility exports.

The canonical Step 55 package boundary starts under ``src.mpm_lbm``.  This
module keeps legacy ``from src import ...`` imports working without importing
heavy optional runtime dependencies during package discovery.
"""

from importlib import import_module


_EXPORT_MODULES = {
    "LBMConfig": "src.lbm_config",
    "LBMFluid3D": "src.lbm_fluid",
    "LinkAreaMomentumAccounting3D": "src.mpm_lbm.sim.coupling.link_area_accounting",
    "LinkAreaMovingBoundaryCoupler3D": "src.mpm_lbm.sim.coupling.link_area",
    "PenaltyFSICoupler3D": "src.coupling",
    "FSIDiagnostics3D": "src.mpm_lbm.diagnostics.fsi_diagnostics",
    "FSIDriverConfig": "src.mpm_lbm.sim.drivers.fsi_config",
    "FSIDriver3D": "src.mpm_lbm.sim.drivers.fsi_driver",
    "GeometryConfig": "src.mpm_lbm.sim.geometry.config",
    "GeometrySampler3D": "src.mpm_lbm.sim.geometry.sampler",
    "ImportedGeometrySampler3D": "src.mpm_lbm.sim.geometry.importers",
    "GeometryQualityGate": "src.mpm_lbm.sim.geometry.quality",
    "analyze_geometry_config": "src.mpm_lbm.sim.geometry.quality",
    "SquidProxyRegionConfig": "src.squid_region_config",
    "SquidRegion": "src.squid_region_config",
    "default_squid_proxy_region_config": "src.squid_region_config",
    "sample_squid_proxy_regions": "src.squid_proxy_regions",
    "summarize_region_masks": "src.squid_proxy_regions",
    "analyze_mesh": "src.mpm_lbm.sim.geometry.mesh_quality",
    "load_obj": "src.mpm_lbm.sim.geometry.mesh_io",
    "mesh_bounds": "src.mpm_lbm.sim.geometry.mesh_io",
    "normalize_vertices": "src.mpm_lbm.sim.geometry.mesh_io",
    "write_obj": "src.mpm_lbm.sim.geometry.mesh_io",
    "MPMConfig": "src.mpm_config",
    "MPMSolid3D": "src.mpm_solid",
    "MovingBoundaryFSICoupler3D": "src.moving_boundary_coupling",
    "MomentumAccounting3D": "src.mpm_lbm.sim.coupling.momentum_accounting",
    "MPMToLBMProjector3D": "src.projection",
    "UnifiedSimConfig": "src.mpm_lbm.sim.drivers.sim_config",
    "GridUnitMapper": "src.units",
    "VoxelGeometry": "src.mpm_lbm.sim.geometry.voxel_io",
    "load_voxel_geometry": "src.mpm_lbm.sim.geometry.voxel_io",
    "save_voxel_geometry": "src.mpm_lbm.sim.geometry.voxel_io",
    "voxel_centers_to_points": "src.mpm_lbm.sim.geometry.voxel_io",
    "analyze_voxel_occupancy": "src.mpm_lbm.sim.geometry.voxel_quality",
    "classify_calibration_row": "src.calibration",
    "choose_recommended_row": "src.calibration",
    "write_calibration_summary": "src.calibration",
}

__all__ = list(_EXPORT_MODULES)


def __getattr__(name):
    if name not in _EXPORT_MODULES:
        raise AttributeError(f"module 'src' has no attribute {name!r}")
    module = import_module(_EXPORT_MODULES[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
