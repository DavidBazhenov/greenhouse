from __future__ import annotations

import tkinter as tk

from application.services.garden_service import GardenService
from infrastructure.config.runtime_config import RuntimeConfig
from infrastructure.hardware.gpio_adapter import GardenHardware
from infrastructure.storage.json_state_store import JsonStateStore
from ui.tkinter_app import SmartGardenApp


def build_application() -> tuple[tk.Tk, SmartGardenApp]:
    root = tk.Tk()
    runtime_config = RuntimeConfig.from_env()
    hardware = GardenHardware(runtime_config)
    state_store = JsonStateStore(runtime_config.state_file)
    state = state_store.load()
    service = GardenService(
        state=state,
        hardware=hardware,
        runtime_config=runtime_config,
        state_store=state_store,
    )
    service.restore_runtime_state()
    app = SmartGardenApp(root, state=state, runtime_config=runtime_config, service=service)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    return root, app


def main() -> None:
    root, app = build_application()
    try:
        root.mainloop()
    finally:
        app.on_closing()
