# Greenbox

Greenbox is a small Python application for smart-garden control on Raspberry Pi with a Tkinter UI and a hardware adapter boundary.

## Structure

```text
greenbox/
├── application/
│   └── services/
│       └── garden_service.py
├── backend/
│   └── hardware_controller.py
├── domain/
│   └── models.py
├── frontend/
│   ├── main.py
│   └── project.py
├── infrastructure/
│   ├── config/
│   │   └── runtime_config.py
│   └── hardware/
│       └── gpio_adapter.py
├── runtime/
│   └── bootstrap.py
├── ui/
│   └── tkinter_app.py
├── scripts/
│   ├── blink_emulator.py
│   └── watch_and_run.py
├── requirements.txt
├── README.md
├── .gitignore
└── .python-version
```

## Requirements

- Python 3.11
- macOS for local development
- Raspberry Pi for deployment

## Setup

Create and activate a virtual environment from the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Launch

Start the application from the repository root:

```bash
python -m frontend.main
```

Alternative entrypoint:

```bash
python -m runtime.bootstrap
```

Run the GPIO emulator:

```bash
python scripts/blink_emulator.py
```

Watch and restart a module on changes:

```bash
python scripts/watch_and_run.py frontend/main.py
```

## Notes For Raspberry Pi

- `gpiozero` is isolated behind the hardware adapter.
- The adapter falls back to a safe no-op GPIO implementation when real hardware is unavailable.
- Pin mapping and runtime defaults live in `infrastructure/config/runtime_config.py`.

## Architecture Snapshot

- `ui` owns Tkinter screens and user interaction.
- `application/services` coordinates use cases.
- `domain/models` contains typed state and presets.
- `infrastructure/hardware` owns GPIO access.
- `infrastructure/config` owns runtime settings and pin mapping.
- `runtime/bootstrap` wires the app together.
