import os

from step32_common import ROOT, finite_values, load_schedule_config, make_schedule_rows, write_csv_rows, write_json, write_log
from src.squid_kinematics_schedule import summarize_schedule


FIELDS = [
    "mantle_radius_scale_min_observed",
    "mantle_radius_scale_max_observed",
    "cavity_volume_scale_min_observed",
    "cavity_volume_scale_max_observed",
    "funnel_aperture_scale_min_observed",
    "funnel_aperture_scale_max_observed",
    "max_abs_mantle_radius_rate",
    "max_abs_cavity_volume_rate",
    "max_abs_funnel_aperture_rate",
    "contraction_sample_count",
    "refill_sample_count",
    "funnel_open_sample_count",
    "envelope_pass",
]


def main():
    os.chdir(ROOT)
    config = load_schedule_config()
    rows = make_schedule_rows()
    summary = summarize_schedule(rows)
    envelope = dict(summary)
    envelope.update(
        {
            "contraction_sample_count": sum(
                1 for row in rows if config.contraction_start_phase <= float(row["phase"]) <= config.contraction_end_phase
            ),
            "refill_sample_count": sum(
                1 for row in rows if config.refill_start_phase <= float(row["phase"]) <= config.refill_end_phase
            ),
            "funnel_open_sample_count": sum(
                1 for row in rows if float(row["funnel_aperture_scale"]) > float(config.funnel_aperture_scale_rest)
            ),
        }
    )
    envelope["envelope_pass"] = bool(
        finite_values(envelope, excluded=("finite_pass", "endpoint_repeatability_pass", "envelope_pass"))
        and float(envelope["mantle_radius_scale_min_observed"]) >= config.mantle_radius_scale_min
        and float(envelope["mantle_radius_scale_max_observed"]) <= config.mantle_radius_scale_rest
        and float(envelope["cavity_volume_scale_min_observed"]) >= config.cavity_volume_scale_min
        and float(envelope["cavity_volume_scale_max_observed"]) <= config.cavity_volume_scale_rest
        and float(envelope["funnel_aperture_scale_min_observed"]) >= config.funnel_aperture_scale_rest
        and float(envelope["funnel_aperture_scale_max_observed"]) <= config.funnel_aperture_scale_max
        and int(envelope["contraction_sample_count"]) > 0
        and int(envelope["refill_sample_count"]) > 0
        and int(envelope["funnel_open_sample_count"]) > 0
    )
    if not envelope["envelope_pass"]:
        raise RuntimeError(f"Step 32 schedule envelope failed: {envelope}")

    out_dir = ROOT / "outputs" / "step32_schedule_envelope_summary"
    write_csv_rows(out_dir / "schedule_envelope_summary.csv", [envelope], FIELDS)
    write_json(out_dir / "schedule_envelope_summary.json", {"summary": envelope, "rows": [envelope]})
    marker = "[OK] Step 32 schedule envelope summary finished"
    write_log(
        "logs/step32_schedule_envelope_summary.log",
        [
            marker,
            f"contraction_sample_count={envelope['contraction_sample_count']}",
            f"refill_sample_count={envelope['refill_sample_count']}",
            f"funnel_open_sample_count={envelope['funnel_open_sample_count']}",
        ],
    )
    print(f"contraction_sample_count={envelope['contraction_sample_count']}")
    print(marker)


if __name__ == "__main__":
    main()
