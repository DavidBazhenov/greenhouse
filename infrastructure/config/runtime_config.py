from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class PinMapping:
    light: int = 18
    water: int = 27
    fertilizer: int = 22


@dataclass(frozen=True)
class RuntimeConfig:
    mock_gpio: bool = False
    fullscreen: bool = False
    light_start_hour: int = 8
    default_light_end_hour: int = 24
    window_width: int = 320
    window_height: int = 240
    minimum_width: int = 320
    minimum_height: int = 240
    catalog_canvas_width: int = 300
    garden_canvas_width: int = 300
    settings_window_width: int = 320
    settings_window_height: int = 240
    wifi_window_width: int = 320
    wifi_window_height: int = 240
    scheduler_interval_seconds: int = 5
    shutdown_timeout_seconds: float = 1.5
    state_file: str = "var/state/greenbox-state.json"
    pin_mapping: PinMapping = field(default_factory=PinMapping)

    @classmethod
    def from_env(cls) -> RuntimeConfig:
        return cls(
            mock_gpio=os.getenv("GREENBOX_MOCK_GPIO", "0").lower() in {"1", "true", "yes", "on"},
            fullscreen=os.getenv("GREENBOX_FULLSCREEN", "0").lower() in {"1", "true", "yes", "on"},
            light_start_hour=int(os.getenv("GREENBOX_LIGHT_START_HOUR", "8")),
            default_light_end_hour=int(os.getenv("GREENBOX_LIGHT_END_HOUR", "24")),
            window_width=int(os.getenv("GREENBOX_WINDOW_WIDTH", "320")),
            window_height=int(os.getenv("GREENBOX_WINDOW_HEIGHT", "240")),
            minimum_width=int(os.getenv("GREENBOX_MIN_WIDTH", "320")),
            minimum_height=int(os.getenv("GREENBOX_MIN_HEIGHT", "240")),
            catalog_canvas_width=int(os.getenv("GREENBOX_CATALOG_WIDTH", "300")),
            garden_canvas_width=int(os.getenv("GREENBOX_GARDEN_WIDTH", "300")),
            settings_window_width=int(os.getenv("GREENBOX_SETTINGS_WIDTH", "320")),
            settings_window_height=int(os.getenv("GREENBOX_SETTINGS_HEIGHT", "240")),
            wifi_window_width=int(os.getenv("GREENBOX_WIFI_WIDTH", "320")),
            wifi_window_height=int(os.getenv("GREENBOX_WIFI_HEIGHT", "240")),
            scheduler_interval_seconds=int(os.getenv("GREENBOX_SCHEDULER_INTERVAL", "5")),
            shutdown_timeout_seconds=float(os.getenv("GREENBOX_SHUTDOWN_TIMEOUT", "1.5")),
            state_file=os.getenv("GREENBOX_STATE_FILE", "var/state/greenbox-state.json"),
            pin_mapping=PinMapping(
                light=int(os.getenv("GREENBOX_PIN_LIGHT", "18")),
                water=int(os.getenv("GREENBOX_PIN_WATER", "27")),
                fertilizer=int(os.getenv("GREENBOX_PIN_FERTILIZER", "22")),
            ),
        )
