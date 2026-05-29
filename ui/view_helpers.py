from __future__ import annotations

import tkinter as tk


def configure_modal(window: tk.Toplevel, root: tk.Misc, width: int, height: int, title: str) -> tk.Frame:
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.resizable(False, False)
    window.transient(root)
    window.grab_set()
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
    content = tk.Frame(window)
    content.pack(fill="both", expand=True, padx=20, pady=20)
    return content


def enable_touch_scroll(canvas: tk.Canvas, scrollable: tk.Widget) -> None:
    def on_press(event: tk.Event) -> None:
        canvas.scan_mark(
            event.x_root - canvas.winfo_rootx(),
            event.y_root - canvas.winfo_rooty(),
        )

    def on_drag(event: tk.Event) -> None:
        canvas.scan_dragto(
            event.x_root - canvas.winfo_rootx(),
            event.y_root - canvas.winfo_rooty(),
            gain=1,
        )

    def on_mousewheel(event: tk.Event) -> None:
        if getattr(event, "num", None) == 4:
            canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            canvas.yview_scroll(1, "units")
        else:
            delta = -1 if getattr(event, "delta", 0) > 0 else 1
            canvas.yview_scroll(delta, "units")

    def bind_recursive(widget: tk.Widget) -> None:
        widget.bind("<ButtonPress-1>", on_press, add="+")
        widget.bind("<B1-Motion>", on_drag, add="+")
        widget.bind("<MouseWheel>", on_mousewheel, add="+")
        widget.bind("<Button-4>", on_mousewheel, add="+")
        widget.bind("<Button-5>", on_mousewheel, add="+")
        for child in widget.winfo_children():
            bind_recursive(child)

    bind_recursive(scrollable)
