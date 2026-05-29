from __future__ import annotations

from enum import Enum

from infrastructure.config.runtime_config import RuntimeConfig
from infrastructure.hardware.mock_gpio import MockGardenHardware
from infrastructure.hardware.protocols import HardwareController
from infrastructure.hardware.real_gpio import GPIOZERO_AVAILABLE, RealGardenHardware


class FertilizerTypeEmulator(Enum):
    KP = "K+P+микро"
    NPK = "NPK"
    NONE = "Без"


def create_hardware(runtime_config: RuntimeConfig | None = None) -> HardwareController:
    config = runtime_config or RuntimeConfig()
    if config.mock_gpio or not GPIOZERO_AVAILABLE:
        return MockGardenHardware(config)
    try:
        return RealGardenHardware(config)
    except Exception as exc:
        print(f"⚠️ Не удалось инициализировать реальный GPIO: {exc}")
        print("🔄 Переключаемся на mock GPIO")
        return MockGardenHardware(config)


class GardenHardware:
    def __init__(self, runtime_config: RuntimeConfig | None = None) -> None:
        self._implementation = create_hardware(runtime_config)

    def __getattr__(self, item: str):
        return getattr(self._implementation, item)
