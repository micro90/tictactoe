"""Live Desktop Build Progress Stream Monitor.

Displays real-time build and development events on the desktop while the
Tic Tac Toe application and executable are being created and verified.
"""

import json
import os
import sys
import time
import tkinter as tk
from tkinter import ttk

EVENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_events.jsonl")


def emit_event(stage: str, message: str, progress: int, status: str = "IN_PROGRESS") -> None:
    """Append a structured progress event to build_events.jsonl and print to stdout."""
    event = {
        "timestamp": time.strftime("%H:%M:%S"),
        "stage": stage,
        "message": message,
        "progress": progress,
        "status": status,
    }
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    print(f"[{event['timestamp']}] [{progress:3d}%] [{stage}] {message}", flush=True)


class ProgressMonitorApp:
    """Desktop GUI window that streams live build progress events."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic Tac Toe - Live Build Event Stream")
        self.root.geometry("620x380+60+60")
        self.root.configure(bg="#1e1e2e")
        self.root.attributes("-topmost", True)

        header = tk.Label(
            root,
            text="⚡ Live Build & Verification Event Stream",
            font=("Segoe UI", 13, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e",
            anchor="w",
        )
        header.pack(fill="x", padx=16, pady=(14, 4))

        self.stage_label = tk.Label(
            root,
            text="Initializing build pipeline...",
            font=("Segoe UI", 10),
            fg="#cdd6f4",
            bg="#1e1e2e",
            anchor="w",
        )
        self.stage_label.pack(fill="x", padx=16, pady=(0, 6))

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Build.Horizontal.TProgressbar",
            troughcolor="#313244",
            background="#a6e3a1",
            thickness=16,
        )
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            root,
            variable=self.progress_var,
            maximum=100,
            style="Build.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 10))

        self.log_text = tk.Text(
            root,
            font=("Consolas", 9),
            bg="#181825",
            fg="#a6adc8",
            insertbackground="#cdd6f4",
            relief="flat",
            padx=10,
            pady=10,
            state="disabled",
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        self.last_pos = 0
        self.completed_at = None
        self.poll_events()

    def poll_events(self) -> None:
        """Read new lines from build_events.jsonl and update the UI."""
        if os.path.exists(EVENTS_FILE):
            try:
                with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                    f.seek(self.last_pos)
                    lines = f.readlines()
                    self.last_pos = f.tell()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    ts = data.get("timestamp", "")
                    stage = data.get("stage", "INFO")
                    msg = data.get("message", "")
                    prog = data.get("progress", 0)
                    status = data.get("status", "IN_PROGRESS")

                    self.progress_var.set(prog)
                    self.stage_label.config(text=f"[{prog}%] {stage}: {msg}")

                    self.log_text.config(state="normal")
                    self.log_text.insert("end", f"[{ts}] [{prog:3d}%] {stage}: {msg}\n")
                    self.log_text.see("end")
                    self.log_text.config(state="disabled")

                    if status == "COMPLETE" and self.completed_at is None:
                        self.completed_at = time.time()
            except Exception:
                pass

        if self.completed_at is not None and (time.time() - self.completed_at) > 4.0:
            self.root.destroy()
            return

        self.root.after(250, self.poll_events)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--emit":
        stage_arg = sys.argv[2]
        msg_arg = sys.argv[3]
        prog_arg = int(sys.argv[4]) if len(sys.argv) >= 5 else 0
        status_arg = sys.argv[5] if len(sys.argv) >= 6 else "IN_PROGRESS"
        emit_event(stage_arg, msg_arg, prog_arg, status_arg)
    else:
        app_root = tk.Tk()
        app = ProgressMonitorApp(app_root)
        app_root.mainloop()
