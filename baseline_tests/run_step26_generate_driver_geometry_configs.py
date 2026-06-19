import os

from step26_common import (
    ROOT,
    STEP26_DESCRIPTORS,
    STEP26_GEOMETRY_CONFIGS,
    write_csv_rows,
    write_json,
    write_log,
)
from src.geometry_candidate_manifest import load_candidate_descriptor
from src.geometry_config import GeometryConfig
from src.geometry_driver_config import driver_config_payload_for_candidate, write_geometry_config_from_descriptor


FIELDS = [
    "candidate_id",
    "geometry_type",
    "geometry_config_path",
    "source_file",
    "n_particles",
    "quality_check_enabled",
    "quality_check_strict",
    "geometry_config_valid",
]


DRIVER_ROWS = [
    ("real_candidate_smoke_mesh", "none", "engineering", "configs/step26_driver_real_candidate_smoke_mesh_48_none.json"),
    ("real_candidate_smoke_mesh", "penalty", "engineering", "configs/step26_driver_real_candidate_smoke_mesh_48_penalty.json"),
    (
        "real_candidate_smoke_mesh",
        "moving_boundary",
        "engineering",
        "configs/step26_driver_real_candidate_smoke_mesh_48_moving_boundary.json",
    ),
    (
        "real_candidate_smoke_mesh",
        "moving_boundary",
        "link_area_experimental",
        "configs/step26_driver_real_candidate_smoke_mesh_48_link_area.json",
    ),
    ("real_candidate_smoke_voxel", "none", "engineering", "configs/step26_driver_real_candidate_smoke_voxel_48_none.json"),
    ("real_candidate_smoke_voxel", "penalty", "engineering", "configs/step26_driver_real_candidate_smoke_voxel_48_penalty.json"),
    (
        "real_candidate_smoke_voxel",
        "moving_boundary",
        "engineering",
        "configs/step26_driver_real_candidate_smoke_voxel_48_moving_boundary.json",
    ),
    (
        "real_candidate_smoke_voxel",
        "moving_boundary",
        "link_area_experimental",
        "configs/step26_driver_real_candidate_smoke_voxel_48_link_area.json",
    ),
]


def main():
    os.chdir(ROOT)
    rows = []
    for descriptor_path in STEP26_DESCRIPTORS:
        descriptor = load_candidate_descriptor(descriptor_path)
        candidate_id = descriptor["candidate_id"]
        geometry_config_path = STEP26_GEOMETRY_CONFIGS[candidate_id]
        payload = write_geometry_config_from_descriptor(descriptor_path, geometry_config_path)
        config = GeometryConfig.from_json(ROOT / geometry_config_path)
        rows.append(
            {
                "candidate_id": candidate_id,
                "geometry_type": config.geometry_type,
                "geometry_config_path": geometry_config_path,
                "source_file": payload["geometry_file"],
                "n_particles": int(config.n_particles),
                "quality_check_enabled": bool(config.quality_check_enabled),
                "quality_check_strict": bool(config.quality_check_strict),
                "geometry_config_valid": True,
            }
        )
        for n_grid in (32, 48, 64):
            write_json(
                f"configs/step26_projection_{candidate_id}_{n_grid}.json",
                {"candidate_id": candidate_id, "geometry_config_path": geometry_config_path, "n_grid": n_grid},
            )

    for candidate_id, mode, transfer, out_path in DRIVER_ROWS:
        payload = driver_config_payload_for_candidate(
            STEP26_GEOMETRY_CONFIGS[candidate_id],
            coupling_mode=mode,
            reaction_transfer_mode=transfer,
            n_grid=48,
            n_lbm_steps=5,
            mpm_substeps_per_lbm_step=5,
        )
        write_json(out_path, payload)

    if len(rows) != 2 or not all(row["geometry_config_valid"] for row in rows):
        raise RuntimeError(f"Step 26 generated geometry configs failed: {rows}")

    out_dir = ROOT / "outputs" / "step26_generated_geometry_configs"
    write_csv_rows(out_dir / "generated_geometry_configs.csv", rows, FIELDS)
    write_json(
        out_dir / "generated_geometry_configs.json",
        {"row_count": len(rows), "driver_config_count": len(DRIVER_ROWS), "rows": rows},
    )
    marker = "[OK] Step 26 generated driver geometry configs finished"
    write_log(
        "logs/step26_generate_driver_geometry_configs.log",
        [marker, f"row_count={len(rows)}", f"driver_config_count={len(DRIVER_ROWS)}"],
    )
    print(f"row_count={len(rows)}")
    print(marker)


if __name__ == "__main__":
    main()
