from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FertilizerType(Enum):
    KP = "K+P+микро"
    NPK = "NPK"
    NONE = "Без"


@dataclass(frozen=True)
class PlantPreset:
    light: int
    water: int
    fertilizer: FertilizerType
    icon: str
    days: str
    temp: str
    description: str


PLANT_PRESETS: dict[str, PlantPreset] = {
    "Черри": PlantPreset(
        light=15,
        water=8,
        fertilizer=FertilizerType.KP,
        icon="🍒",
        days="60-80",
        temp="18-26",
        description="Сладкие черри помидоры",
    ),
    "Перец": PlantPreset(
        light=13,
        water=5,
        fertilizer=FertilizerType.NPK,
        icon="🌶️",
        days="70-90",
        temp="20-28",
        description="Сладкий болгарский перец",
    ),
    "Огурец": PlantPreset(
        light=15,
        water=3,
        fertilizer=FertilizerType.KP,
        icon="🥒",
        days="45-55",
        temp="20-25",
        description="Хрустящие огурцы",
    ),
    "Базилик": PlantPreset(
        light=14,
        water=4,
        fertilizer=FertilizerType.KP,
        icon="🌿",
        days="25-35",
        temp="20-25",
        description="Ароматный базилик",
    ),
    "Салат": PlantPreset(
        light=12,
        water=3,
        fertilizer=FertilizerType.NPK,
        icon="🥬",
        days="20-30",
        temp="15-20",
        description="Свежий листовой салат",
    ),
    "Помидоры": PlantPreset(
        light=16,
        water=6,
        fertilizer=FertilizerType.NPK,
        icon="🍅",
        days="70-90",
        temp="20-26",
        description="Крупные помидоры",
    ),
}


@dataclass
class GardenConfig:
    selected_plant: str = "Черри"
    light: int = 15
    watering: int = 8
    fertilizer: FertilizerType = FertilizerType.KP
    is_running: bool = False
    start_date: datetime | None = None
    wifi_connected: bool = False

    _KEY_MAP = {
        "selectedPlant": "selected_plant",
        "light": "light",
        "watering": "watering",
        "fertilizer": "fertilizer",
        "isRunning": "is_running",
        "startDate": "start_date",
        "wifi_connected": "wifi_connected",
    }

    def __getitem__(self, key: str) -> Any:
        return getattr(self, self._KEY_MAP[key])

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, self._KEY_MAP[key], value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, self._KEY_MAP.get(key, key), default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "selectedPlant": self.selected_plant,
            "light": self.light,
            "watering": self.watering,
            "fertilizer": self.fertilizer,
            "isRunning": self.is_running,
            "startDate": self.start_date,
            "wifi_connected": self.wifi_connected,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GardenConfig:
        fertilizer = data.get("fertilizer", FertilizerType.KP)
        if not isinstance(fertilizer, FertilizerType):
            fertilizer = FertilizerType(fertilizer)
        start_date = data.get("startDate")
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        return cls(
            selected_plant=data.get("selectedPlant", "Черри"),
            light=data.get("light", 15),
            watering=data.get("watering", 8),
            fertilizer=fertilizer,
            is_running=data.get("isRunning", False),
            start_date=start_date,
            wifi_connected=data.get("wifi_connected", False),
        )


@dataclass
class AppSettings:
    notifications: bool = True
    auto_mode: bool = True
    temperature_unit: str = "Celsius"

    _KEY_MAP = {
        "notifications": "notifications",
        "auto_mode": "auto_mode",
        "temperature_unit": "temperature_unit",
    }

    def __getitem__(self, key: str) -> Any:
        return getattr(self, self._KEY_MAP[key])

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, self._KEY_MAP[key], value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, self._KEY_MAP.get(key, key), default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "notifications": self.notifications,
            "auto_mode": self.auto_mode,
            "temperature_unit": self.temperature_unit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppSettings:
        return cls(
            notifications=data.get("notifications", True),
            auto_mode=data.get("auto_mode", True),
            temperature_unit=data.get("temperature_unit", "Celsius"),
        )


@dataclass
class Plant:
    name: str
    icon: str
    start_date: datetime
    last_water_date: datetime
    light: int
    watering: int
    fertilizer: FertilizerType
    days: str
    temp: str
    unique_id: str = ""

    _KEY_MAP = {
        "name": "name",
        "icon": "icon",
        "start_date": "start_date",
        "last_water_date": "last_water_date",
        "light": "light",
        "watering": "watering",
        "fertilizer": "fertilizer",
        "days": "days",
        "temp": "temp",
        "unique_id": "unique_id",
    }

    def __getitem__(self, key: str) -> Any:
        return getattr(self, self._KEY_MAP[key])

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, self._KEY_MAP[key], value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, self._KEY_MAP.get(key, key), default)

    def copy(self) -> dict[str, Any]:
        return self.to_dict()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "icon": self.icon,
            "start_date": self.start_date,
            "last_water_date": self.last_water_date,
            "light": self.light,
            "watering": self.watering,
            "fertilizer": self.fertilizer,
            "days": self.days,
            "temp": self.temp,
            "unique_id": self.unique_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Plant:
        fertilizer = data.get("fertilizer", FertilizerType.KP)
        if not isinstance(fertilizer, FertilizerType):
            fertilizer = FertilizerType(fertilizer)
        start_date = data.get("start_date")
        last_water_date = data.get("last_water_date")
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(last_water_date, str):
            last_water_date = datetime.fromisoformat(last_water_date)
        return cls(
            name=data["name"],
            icon=data["icon"],
            start_date=start_date,
            last_water_date=last_water_date,
            light=data["light"],
            watering=data["watering"],
            fertilizer=fertilizer,
            days=data["days"],
            temp=data["temp"],
            unique_id=data.get("unique_id", ""),
        )


@dataclass
class GardenState:
    config: GardenConfig = field(default_factory=GardenConfig)
    settings: AppSettings = field(default_factory=AppSettings)
    plants: list[Plant] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        config_data = self.config.to_dict()
        if isinstance(config_data["fertilizer"], FertilizerType):
            config_data["fertilizer"] = config_data["fertilizer"].value
        if isinstance(config_data["startDate"], datetime):
            config_data["startDate"] = config_data["startDate"].isoformat()

        plants_data = []
        for plant in self.plants:
            plant_data = plant.to_dict()
            if isinstance(plant_data["fertilizer"], FertilizerType):
                plant_data["fertilizer"] = plant_data["fertilizer"].value
            if isinstance(plant_data["start_date"], datetime):
                plant_data["start_date"] = plant_data["start_date"].isoformat()
            if isinstance(plant_data["last_water_date"], datetime):
                plant_data["last_water_date"] = plant_data["last_water_date"].isoformat()
            plants_data.append(plant_data)

        return {
            "config": config_data,
            "settings": self.settings.to_dict(),
            "plants": plants_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GardenState:
        return cls(
            config=GardenConfig.from_dict(data.get("config", {})),
            settings=AppSettings.from_dict(data.get("settings", {})),
            plants=[Plant.from_dict(item) for item in data.get("plants", [])],
        )
