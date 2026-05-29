from pathlib import Path
import subprocess
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_arg = Path(script_name)
        self.script_path = self.script_arg.resolve()
        self.module_name = self._script_path_to_module(self.script_arg)
        self.process = None
        self.start_process()

    @staticmethod
    def _script_path_to_module(script_path: Path) -> str | None:
        if script_path.suffix != ".py":
            return None
        if script_path.is_absolute():
            try:
                script_path = script_path.relative_to(Path.cwd())
            except ValueError:
                return None
        parts = script_path.with_suffix("").parts
        if not parts:
            return None
        return ".".join(parts)

    def start_process(self):
        if self.process:
            self.process.terminate()
            time.sleep(0.5)
        if self.module_name:
            self.process = subprocess.Popen([sys.executable, "-m", self.module_name])
        else:
            self.process = subprocess.Popen([sys.executable, str(self.script_path)])
        print(f"[{time.strftime('%H:%M:%S')}] Перезапущен {self.script_path}")

    def on_modified(self, event):
        if Path(event.src_path).resolve() == self.script_path:
            print(f"\n📁 Изменён {self.script_path}, перезапускаем...")
            self.start_process()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python3 watch_and_run.py <скрипт.py>")
        sys.exit(1)

    script = sys.argv[1]
    event_handler = RestartHandler(script)
    observer = Observer()
    observer.schedule(event_handler, path=str(event_handler.script_path.parent), recursive=False)
    observer.start()

    print(f"Слежу за изменениями в {event_handler.script_path}. Нажмите Ctrl+C для выхода.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
