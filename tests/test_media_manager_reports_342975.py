#!/usr/bin/env python3
"""Regression coverage for 3.4.29.75 responsive media and dated reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.lcd_media_manager.v1_1 import (  # noqa: E402
    DesignLibraryDialog,
    DesignLibraryState,
    friendly_media_name,
    load_library_state,
    save_library_state,
)
from modules.responsive_gallery.v1_0 import responsive_column_count  # noqa: E402
from modules.temperature_history.v1_2 import (  # noqa: E402
    TemperatureHistoryBuffer,
    TemperatureHistoryChart,
    temperature_report_rows,
    write_temperature_report,
)


def test_media_manager_migrates_sources_aliases_and_non_destructive_exclusions(tmp_path: Path) -> None:
    folder = tmp_path / "designs"
    folder.mkdir()
    media = folder / "e012.mp4"
    media.write_bytes(b"local video")
    alias = "Waldlichtung"
    state = DesignLibraryState((folder,), (), {str(media): alias}, (media,))
    restored = load_library_state(save_library_state(state))
    assert restored.folders == (folder.resolve(),)
    assert restored.aliases[str(media.resolve())] == alias
    assert restored.excluded == (media.resolve(),)
    assert friendly_media_name(media) == "Natur 012"
    assert friendly_media_name(media, alias) == alias
    assert media.read_bytes() == b"local video"


def test_media_manager_lists_a_theme_once_instead_of_its_internal_preview(tmp_path: Path) -> None:
    folder = tmp_path / "designs"
    theme = folder / "Theme1"
    theme.mkdir(parents=True)
    (theme / "trcc.json").write_text("{}", encoding="utf-8")
    (theme / "Theme.png").write_bytes(b"preview")
    standalone = folder / "e007.mp4"
    standalone.write_bytes(b"video")
    assert DesignLibraryDialog._folder_media(folder) == [standalone.resolve(), theme.resolve()]


def test_responsive_columns_use_actual_width_and_stay_bounded() -> None:
    assert responsive_column_count(390) == 2
    assert responsive_column_count(920) == 4
    assert responsive_column_count(2300) == 12
    assert responsive_column_count(8000) == 12


def test_temperature_report_uses_absolute_range_all_selected_sensors_and_local_dates(tmp_path: Path) -> None:
    history = TemperatureHistoryBuffer(max_age_seconds=3600, max_samples=100)
    history.append({"cpu": 51.25, "ssd": 39.5}, timestamp=1_786_000_000)
    history.append({"cpu": 52.0, "ssd": 40.0}, timestamp=1_786_000_100)
    catalog = {
        "cpu": ("CPU", "cpu", "OHC"),
        "ssd": ("SSD", "storage", "nvme"),
    }
    rows = temperature_report_rows(
        history, 1_786_000_000, 1_786_000_050, {"cpu", "ssd"}, catalog,
    )
    assert len(rows) == 2
    assert {row["sensor_key"] for row in rows} == {"cpu", "ssd"}
    assert all(row["date"] and row["time"] and "+" in str(row["timestamp_local"]) for row in rows)

    csv_path = write_temperature_report(tmp_path / "report", rows, "csv")
    json_path = write_temperature_report(tmp_path / "report-json", rows, "json")
    with csv_path.open(encoding="utf-8", newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 2
    assert len(json.loads(json_path.read_text(encoding="utf-8"))["readings"]) == 2
    assert TemperatureHistoryChart.timestamp_label(1_786_000_000).count(".") == 2


def test_current_module_versions_and_responsive_viewport_watchers_are_registered() -> None:
    effects = (SRC / "modules/display_effects/v1_11/base_page.py").read_text(encoding="utf-8")
    studio = (SRC / "thermalright_display_ui.py").read_text(encoding="utf-8")
    panel = (SRC / "modules/temperature_history/v1_2/panel.py").read_text(encoding="utf-8")
    assert "ViewportResizeRelay" in effects
    assert "responsive_column_count" in effects
    assert "ViewportResizeRelay" in studio
    assert "DesignLibraryPanel" in studio
    assert "QSplitter" in panel
    assert "TemperatureReportDialog" in panel
