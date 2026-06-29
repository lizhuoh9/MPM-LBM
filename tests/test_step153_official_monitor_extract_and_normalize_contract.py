import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step153_missing_private_source_waits_without_writing_official_monitor(tmp_path):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    out_dir = tmp_path / "out"
    official_monitor = tmp_path / "private" / "official_monitor.csv"
    summary = step153.run_step153_official_monitor_extract_and_normalize(
        input_path=tmp_path / "private" / "missing_raw_monitor_export.txt",
        official_monitor=official_monitor,
        output_dir=out_dir,
        force=True,
    )

    assert summary["step"] == 153
    assert summary["status"] == "waiting_for_official_monitor_source"
    assert summary["official_monitor_written_private"] is False
    assert summary["ready_for_step150"] is False
    assert summary["official_monitor_committed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert not official_monitor.exists()
    assert read_json(out_dir / "official_monitor_extraction_summary.json")["ready_for_step150"] is False


def test_step153_canonical_csv_writes_private_official_monitor(tmp_path):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    raw = tmp_path / "raw_monitor_export.csv"
    official_monitor = tmp_path / "private" / "official_monitor.csv"
    write_csv(
        raw,
        [
            {"time_s": 0.0, "flap_tip_total_displacement_m": 0.0, "fluid_force_magnitude_n": 1.0},
            {"time_s": 0.5, "flap_tip_total_displacement_m": 0.002, "fluid_force_magnitude_n": 3.0},
        ],
    )

    summary = step153.run_step153_official_monitor_extract_and_normalize(
        input_path=raw,
        official_monitor=official_monitor,
        output_dir=tmp_path / "out",
        force=True,
    )

    rows = read_csv(official_monitor)
    assert summary["status"] == "official_monitor_ready_for_step150"
    assert summary["official_monitor_written_private"] is True
    assert summary["ready_for_step150"] is True
    assert summary["row_count"] == 2
    assert summary["time_start_s"] == 0.0
    assert summary["time_end_s"] == 0.5
    assert len(summary["official_monitor_hash"]) == 64
    assert summary["official_monitor_committed"] is False
    assert rows[0]["time_s"] == "0"
    assert rows[1]["flap_tip_total_displacement_m"] == "0.002"
    assert "fluid_force_magnitude_n" in rows[0]


def test_step153_tab_delimited_ansys_headers_are_normalized(tmp_path):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    raw = tmp_path / "system_coupling_monitor.txt"
    raw.write_text("Flow Time\tTotal Displacement\tForce Magnitude\n0.0\t0.0\t2.0\n0.25\t0.001\t4.0\n", encoding="utf-8")
    official_monitor = tmp_path / "private" / "official_monitor.csv"

    summary = step153.run_step153_official_monitor_extract_and_normalize(
        input_path=raw,
        official_monitor=official_monitor,
        output_dir=tmp_path / "out",
        force=True,
    )

    rows = read_csv(official_monitor)
    assert summary["ready_for_step150"] is True
    assert summary["columns"] == ["time_s", "flap_tip_total_displacement_m", "fluid_force_magnitude_n"]
    assert rows[1]["time_s"] == "0.25"
    assert rows[1]["fluid_force_magnitude_n"] == "4"


def test_step153_space_delimited_copied_table_is_normalized(tmp_path):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    raw = tmp_path / "copied_table.txt"
    raw.write_text("time displacement force\n0.0 0.0 1.0\n0.1 0.0005 1.5\n", encoding="utf-8")
    official_monitor = tmp_path / "private" / "official_monitor.csv"

    summary = step153.run_step153_official_monitor_extract_and_normalize(
        input_path=raw,
        official_monitor=official_monitor,
        output_dir=tmp_path / "out",
        force=True,
    )

    rows = read_csv(official_monitor)
    assert summary["status"] == "official_monitor_ready_for_step150"
    assert rows[1]["time_s"] == "0.1"
    assert rows[1]["flap_tip_total_displacement_m"] == "0.0005"
    assert rows[1]["fluid_force_magnitude_n"] == "1.5"


def test_step153_preserves_optional_component_columns(tmp_path):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    raw = tmp_path / "raw_monitor_export.csv"
    official_monitor = tmp_path / "private" / "official_monitor.csv"
    write_csv(
        raw,
        [
            {
                "Time": 0.0,
                "Total Displacement": 0.0,
                "X Displacement": 0.0,
                "Y Displacement": 0.0,
                "X Force": 0.0,
                "Y Force": 1.0,
                "Step": 0,
            },
            {
                "Time": 0.5,
                "Total Displacement": 0.003,
                "X Displacement": 0.001,
                "Y Displacement": 0.002,
                "X Force": 2.0,
                "Y Force": 3.0,
                "Step": 1,
            },
        ],
    )

    summary = step153.run_step153_official_monitor_extract_and_normalize(
        input_path=raw,
        official_monitor=official_monitor,
        output_dir=tmp_path / "out",
        force=True,
    )

    rows = read_csv(official_monitor)
    assert summary["ready_for_step150"] is True
    assert "step" in summary["columns"]
    assert "flap_tip_x_displacement_m" in summary["columns"]
    assert "flap_tip_y_displacement_m" in summary["columns"]
    assert "fluid_force_x_n" in summary["columns"]
    assert "fluid_force_y_n" in summary["columns"]
    assert rows[1]["flap_tip_x_displacement_m"] == "0.001"
    assert rows[1]["fluid_force_y_n"] == "3"


def test_step153_rejects_nonmonotonic_time_without_ready_claim(tmp_path):
    summary, official_monitor = run_invalid_fixture(
        tmp_path,
        [
            {"time_s": 0.0, "flap_tip_total_displacement_m": 0.0},
            {"time_s": 0.5, "flap_tip_total_displacement_m": 0.001},
            {"time_s": 0.25, "flap_tip_total_displacement_m": 0.002},
        ],
    )

    assert summary["status"] == "official_monitor_source_invalid"
    assert summary["ready_for_step150"] is False
    assert summary["official_monitor_written_private"] is False
    assert any("monotonic" in item for item in summary["schema_errors"])
    assert not official_monitor.exists()


def test_step153_rejects_missing_displacement_without_ready_claim(tmp_path):
    summary, official_monitor = run_invalid_fixture(
        tmp_path,
        [
            {"time_s": 0.0, "fluid_force_magnitude_n": 1.0},
            {"time_s": 0.5, "fluid_force_magnitude_n": 2.0},
        ],
    )

    assert summary["status"] == "official_monitor_source_invalid"
    assert summary["ready_for_step150"] is False
    assert summary["official_monitor_written_private"] is False
    assert "displacement" in " ".join(summary["schema_errors"]).lower()
    assert not official_monitor.exists()


def test_step153_preview_metadata_omits_private_row_bodies(tmp_path):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    raw = tmp_path / "raw_monitor_export.csv"
    official_monitor = tmp_path / "private" / "official_monitor.csv"
    write_csv(
        raw,
        [
            {"time_s": 0.0, "flap_tip_total_displacement_m": 0.123456789},
            {"time_s": 0.5, "flap_tip_total_displacement_m": 0.987654321},
        ],
    )

    step153.run_step153_official_monitor_extract_and_normalize(
        input_path=raw,
        official_monitor=official_monitor,
        output_dir=tmp_path / "out",
        force=True,
    )

    preview = read_json(tmp_path / "out" / "official_monitor_schema_preview.json")
    preview_text = json.dumps(preview, sort_keys=True)
    assert "rows" not in preview
    assert "0.123456789" not in preview_text
    assert "0.987654321" not in preview_text
    assert preview["row_count"] == 2
    assert preview["sample_values_included"] is False


def run_invalid_fixture(tmp_path: Path, rows: list[dict]):
    import experiments.steps.step153_official_monitor_extract_and_normalize as step153

    raw = tmp_path / "raw_monitor_export.csv"
    official_monitor = tmp_path / "private" / "official_monitor.csv"
    write_csv(raw, rows)
    summary = step153.run_step153_official_monitor_extract_and_normalize(
        input_path=raw,
        official_monitor=official_monitor,
        output_dir=tmp_path / "out",
        force=True,
    )
    return summary, official_monitor


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
