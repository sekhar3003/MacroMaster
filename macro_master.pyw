#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacroMaster v3.1 - Compact Glass Edition
Native window | Optional tray | No presets | Small & bulletproof
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import os
import sys
import traceback

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_error.log")
def log_error(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

if sys.platform != "win32":
    print("This app requires Windows.")
    sys.exit(1)

import ctypes
from ctypes import wintypes
import queue

try:
    from pynput import mouse, keyboard
except ImportError as e:
    log_error(f"pynput missing: {e}")
    messagebox.showerror("MacroMaster", "pynput is not installed.\n\nOpen CMD as Admin and run:\npip install pynput")
    sys.exit(1)

# ==================== WINDOWS API ====================
user32 = ctypes.windll.user32
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG), ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("mi", MOUSEINPUT)]

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

# ==================== THEME ====================
BG = "#080a0c"
PANEL = "#0f1115"
FG = "#e6edf3"
FG_DIM = "#6b7280"
ACCENT = "#2dd4bf"
ACCENT_HOVER = "#5eead4"
ACCENT_DARK = "#134e4a"
DANGER = "#ef4444"
DANGER_HOVER = "#f87171"
SUCCESS = "#22c55e"
SUCCESS_HOVER = "#4ade80"
BORDER = "#1f2937"

# ==================== MACRO ACTION ====================
class MacroAction:
    def __init__(self, action_type="click", x=0, y=0, x2=0, y2=0, delay=0.5, duration=0.0, button="left"):
        self.action_type = action_type
        self.x = x; self.y = y; self.x2 = x2; self.y2 = y2
        self.delay = delay; self.duration = duration; self.button = button

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def __str__(self):
        t = self.action_type
        if t == "click":
            return f"Click [{self.button}]  ({self.x}, {self.y})  ·  {self.delay}s"
        elif t == "right_click":
            return f"Right Click  ({self.x}, {self.y})  ·  {self.delay}s"
        elif t == "middle_click":
            return f"Middle Click  ({self.x}, {self.y})  ·  {self.delay}s"
        elif t == "drag":
            return f"Drag [{self.button}]  ({self.x},{self.y})→({self.x2},{self.y2})  ·  {self.delay}s"
        elif t == "hold":
            return f"Hold [{self.button}]  ({self.x}, {self.y})  {self.duration}s  ·  {self.delay}s"
        elif t == "delay":
            return f"Wait  {self.duration}s"
        return t

# ==================== MOUSE ENGINE ====================
class MouseEngine:
    def __init__(self):
        self.screen_w = user32.GetSystemMetrics(0)
        self.screen_h = user32.GetSystemMetrics(1)
        self._stop = threading.Event()

    def get_cursor_pos(self):
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def _send_mouse(self, flags, dx=0, dy=0, data=0):
        mi = MOUSEINPUT(dx, dy, data, flags, 0, 0)
        inp = INPUT(INPUT_MOUSE, mi)
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def move_to(self, x, y):
        ax = int(x * 65535 / max(self.screen_w - 1, 1))
        ay = int(y * 65535 / max(self.screen_h - 1, 1))
        self._send_mouse(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ax, ay)

    def smooth_move(self, tx, ty, speed=0.5):
        sx, sy = self.get_cursor_pos()
        steps = max(int(speed * 60), 10)
        for i in range(1, steps + 1):
            if self._stop.is_set():
                break
            t = i / steps
            t = t * t * (3 - 2 * t)
            self.move_to(int(sx + (tx - sx) * t), int(sy + (ty - sy) * t))
            time.sleep(speed / steps)

    def click(self, button="left"):
        down = {"left": MOUSEEVENTF_LEFTDOWN, "right": MOUSEEVENTF_RIGHTDOWN, "middle": MOUSEEVENTF_MIDDLEDOWN}[button]
        up = {"left": MOUSEEVENTF_LEFTUP, "right": MOUSEEVENTF_RIGHTUP, "middle": MOUSEEVENTF_MIDDLEUP}[button]
        self._send_mouse(down)
        time.sleep(0.05)
        self._send_mouse(up)

    def mouse_down(self, button="left"):
        f = {"left": MOUSEEVENTF_LEFTDOWN, "right": MOUSEEVENTF_RIGHTDOWN, "middle": MOUSEEVENTF_MIDDLEDOWN}[button]
        self._send_mouse(f)

    def mouse_up(self, button="left"):
        f = {"left": MOUSEEVENTF_LEFTUP, "right": MOUSEEVENTF_RIGHTUP, "middle": MOUSEEVENTF_MIDDLEUP}[button]
        self._send_mouse(f)

    def stop(self):
        self._stop.set()
    def reset(self):
        self._stop.clear()

# ==================== RECORDER ====================
class MacroRecorder:
    def __init__(self, app):
        self.app = app
        self.recording = False
        self.actions = []
        self._listener = None
        self._last_time = None
        self._drag_start = None
        self.queue = queue.Queue()

    def is_over_app(self, x, y):
        try:
            r = self.app.root
            return r.winfo_x() <= x <= r.winfo_x() + r.winfo_width() and r.winfo_y() <= y <= r.winfo_y() + r.winfo_height()
        except:
            return False

    def on_click(self, x, y, button, pressed):
        if not self.recording:
            return
        if self.is_over_app(x, y):
            return
        now = time.time()
        btn = "left" if button == mouse.Button.left else "right" if button == mouse.Button.right else "middle"
        if pressed:
            self._drag_start = (x, y, now)
        else:
            if self._drag_start:
                dx = x - self._drag_start[0]
                dy = y - self._drag_start[1]
                delay = (now - self._last_time) if self._last_time else 0.0
                if abs(dx) > 8 or abs(dy) > 8:
                    act = MacroAction("drag", self._drag_start[0], self._drag_start[1], x, y, delay=max(0, delay), button=btn)
                else:
                    t = "right_click" if btn == "right" else "middle_click" if btn == "middle" else "click"
                    act = MacroAction(t, x, y, delay=max(0, delay), button=btn)
                self.actions.append(act)
                self.queue.put(act)
                self._last_time = now
                self._drag_start = None

    def start(self):
        self.recording = True
        self.actions = []
        self._last_time = None
        self._listener = mouse.Listener(on_click=self.on_click)
        self._listener.start()

    def stop(self):
        self.recording = False
        if self._listener:
            self._listener.stop()
            self._listener = None

# ==================== PLAYER ====================
class MacroPlayer:
    def __init__(self, engine):
        self.engine = engine
        self.playing = False
        self.loop = False
        self.loop_count = 1
        self.speed = 0.5

    def play_actions(self, actions, on_done=None):
        def _play():
            count = 0
            while True:
                if self.engine._stop.is_set():
                    break
                count += 1
                for act in actions:
                    if self.engine._stop.is_set():
                        break
                    time.sleep(act.delay)
                    if act.action_type == "click":
                        self.engine.smooth_move(act.x, act.y, self.speed); self.engine.click(act.button)
                    elif act.action_type == "right_click":
                        self.engine.smooth_move(act.x, act.y, self.speed); self.engine.click("right")
                    elif act.action_type == "middle_click":
                        self.engine.smooth_move(act.x, act.y, self.speed); self.engine.click("middle")
                    elif act.action_type == "drag":
                        self.engine.smooth_move(act.x, act.y, self.speed)
                        self.engine.mouse_down(act.button)
                        self.engine.smooth_move(act.x2, act.y2, max(act.duration, 0.3))
                        self.engine.mouse_up(act.button)
                    elif act.action_type == "hold":
                        self.engine.smooth_move(act.x, act.y, self.speed)
                        self.engine.mouse_down(act.button)
                        time.sleep(act.duration)
                        self.engine.mouse_up(act.button)
                    elif act.action_type == "delay":
                        time.sleep(act.duration)
                if not self.loop or self.engine._stop.is_set():
                    break
                if self.loop_count > 0 and count >= self.loop_count:
                    break
            self.playing = False
            if on_done:
                on_done()
        self.engine.reset()
        self.playing = True
        threading.Thread(target=_play, daemon=True).start()

    def stop(self):
        self.engine.stop()
        self.playing = False

# ==================== APP ====================
class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacroMaster")
        self.root.geometry("460x540")
        self.root.attributes("-alpha", 0.93)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self._exit_app)

        # Icon
        try:
            ip = resource_path("icon.ico")
            if os.path.exists(ip):
                self.root.iconbitmap(ip)
        except Exception as e:
            log_error(f"Icon load: {e}")

        # Center
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{int((sw-460)/2)}+{int((sh-540)/2)}")

        self.engine = MouseEngine()
        self.recorder = MacroRecorder(self)
        self.player = MacroPlayer(self.engine)
        self.actions = []
        self.has_tray = False

        self._build_ui()
        self._setup_tray()
        self._setup_hotkeys()
        self._poll_queue()

    # ----- UI helpers -----
    def _btn(self, parent, text, cmd, bg, fg, hover_bg, width=0):
        b = tk.Button(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"),
                     relief=tk.FLAT, bd=0, cursor="hand2", command=cmd, width=width,
                     activebackground=hover_bg, activeforeground=fg)
        b.bind("<Enter>", lambda e: b.config(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, pady=8)

    def _lbl(self, parent, text, fg=FG_DIM, size=9, bold=False):
        tk.Label(parent, text=text, bg=PANEL, fg=fg,
                font=("Segoe UI", size, "bold" if bold else "normal")).pack(anchor=tk.W, pady=(0, 4))

    # ----- Build -----
    def _build_ui(self):
        # Accent top line
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill=tk.X, padx=0, pady=0)

        # Main panel
        main = tk.Frame(self.root, bg=PANEL)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 10))

        # Playback
        self._lbl(main, "PLAYBACK", ACCENT, 9, True)
        row1 = tk.Frame(main, bg=PANEL)
        row1.pack(fill=tk.X, pady=(0, 2))

        self.btn_record = self._btn(row1, "Record", self._toggle_record, ACCENT_DARK, ACCENT, ACCENT, 8)
        self.btn_record.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_play = self._btn(row1, "Play", self._play, "#14532d", SUCCESS, SUCCESS_HOVER, 8)
        self.btn_play.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_stop = self._btn(row1, "Stop", self._stop, "#7f1d1d", DANGER, DANGER_HOVER, 8)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))
        self._btn(row1, "Hide", self._hide_to_tray, BORDER, FG_DIM, "#374151", 6).pack(side=tk.LEFT)

        # Loop
        row2 = tk.Frame(main, bg=PANEL)
        row2.pack(fill=tk.X, pady=(8, 0))
        self.loop_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row2, text="Loop", variable=self.loop_var, bg=PANEL, fg=FG_DIM,
                      selectcolor=PANEL, activebackground=PANEL, activeforeground=ACCENT,
                      font=("Segoe UI", 9), cursor="hand2").pack(side=tk.LEFT)
        tk.Label(row2, text="Count:", bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(12, 4))
        self.loop_count_var = tk.StringVar(value="1")
        tk.Entry(row2, textvariable=self.loop_count_var, width=5, bg=BG, fg=FG,
                insertbackground=ACCENT, relief=tk.FLAT, font=("Consolas", 10),
                highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT)

        self._sep(main)

        # Actions
        self._lbl(main, "ACTIONS", ACCENT, 9, True)
        list_frm = tk.Frame(main, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        list_frm.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        self.action_list = tk.Listbox(list_frm, bg=BG, fg=FG, selectbackground=ACCENT, selectforeground=BG,
                                     font=("Consolas", 10), borderwidth=0, highlightthickness=0,
                                     activestyle="none", height=8)
        self.action_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        sb = tk.Scrollbar(list_frm, bg=BG, troughcolor=BG, activebackground=ACCENT, relief=tk.FLAT, width=10)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_list.config(yscrollcommand=sb.set)
        sb.config(command=self.action_list.yview)

        row3 = tk.Frame(main, bg=PANEL)
        row3.pack(fill=tk.X, pady=(8, 0))
        self._btn(row3, "+ Add", self._add_action, BORDER, FG, "#374151", 7).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(row3, "Edit", self._edit_action, BORDER, FG, "#374151", 7).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(row3, "Delete", self._delete_action, BORDER, FG, "#374151", 7).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(row3, "Clear", self._clear_actions, BORDER, FG, "#374151", 7).pack(side=tk.LEFT)

        self._sep(main)

        # Settings
        self._lbl(main, "SETTINGS", ACCENT, 9, True)
        row4 = tk.Frame(main, bg=PANEL)
        row4.pack(fill=tk.X, pady=(0, 2))

        tk.Label(row4, text="Speed:", bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="0.5")
        ttk.Combobox(row4, textvariable=self.speed_var, values=["0.1", "0.3", "0.5", "0.8", "1.0", "1.5", "2.0"],
                    width=5, state="readonly", font=("Consolas", 10)).pack(side=tk.LEFT, padx=(6, 12))

        self._btn(row4, "Export", self._export_json, BORDER, FG_DIM, "#374151", 7).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(row4, "Import", self._import_json, BORDER, FG_DIM, "#374151", 7).pack(side=tk.LEFT)

        # Status
        self.status_label = tk.Label(main, text="Ready  ·  F6 Record  ·  F7 Stop  ·  F8 Play",
                                    bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9), anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    # ----- Tray -----
    def _setup_tray(self):
        try:
            from pystray import Icon, Menu, MenuItem
            from PIL import Image
            img = Image.open(resource_path("icon.ico"))
            menu = Menu(
                MenuItem("Show", self._tray_show),
                MenuItem("Exit", self._tray_exit)
            )
            self.tray_icon = Icon("MacroMaster", img, "MacroMaster", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.has_tray = True
        except Exception as e:
            log_error(f"Tray unavailable: {e}")
            self.has_tray = False

    def _hide_to_tray(self):
        if self.has_tray:
            self.root.withdraw()
        else:
            self.root.iconify()

    def _tray_show(self):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

    def _tray_exit(self):
        self.root.after(0, self._exit_app)

    def _exit_app(self):
        try:
            if self.has_tray and hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
        except:
            pass
        self.root.destroy()

    # ----- Playback -----
    def _toggle_record(self):
        if self.recorder.recording:
            self._stop_record()
        else:
            self._start_record()

    def _start_record(self):
        if self.player.playing:
            return
        self.recorder.start()
        self.btn_record.config(text="Stop Rec", bg=DANGER)
        self.status_label.config(text="RECORDING  ·  Click anywhere  ·  F7 to stop", fg=DANGER)

    def _stop_record(self):
        self.recorder.stop()
        self.btn_record.config(text="Record", bg=ACCENT_DARK)
        self.status_label.config(text=f"Recorded {len(self.actions)} actions  ·  Ready", fg=FG_DIM)
        self._refresh_list()

    def _play(self):
        if not self.actions or self.player.playing:
            return
        self.player.loop = self.loop_var.get()
        try:
            self.player.loop_count = int(self.loop_count_var.get())
        except:
            self.player.loop_count = 1
        try:
            self.player.speed = float(self.speed_var.get())
        except:
            pass
        self.status_label.config(text="PLAYING  ·  F7 to stop", fg=SUCCESS)
        self.player.play_actions(self.actions, on_done=lambda: self.root.after(0, self._on_done))

    def _on_done(self):
        self.status_label.config(text="Finished  ·  Ready", fg=FG_DIM)

    def _stop(self):
        self.player.stop()
        if self.recorder.recording:
            self._stop_record()
        self.status_label.config(text="Stopped  ·  Ready", fg=FG_DIM)

    # ----- List -----
    def _refresh_list(self):
        self.action_list.delete(0, tk.END)
        for i, act in enumerate(self.actions, 1):
            self.action_list.insert(tk.END, f"  {i:2d}    {act}")

    def _add_action(self):
        self._open_dialog()

    def _edit_action(self):
        sel = self.action_list.curselection()
        if not sel:
            return
        self._open_dialog(sel[0])

    def _delete_action(self):
        sel = self.action_list.curselection()
        if not sel:
            return
        del self.actions[sel[0]]
        self._refresh_list()

    def _clear_actions(self):
        if messagebox.askyesno("MacroMaster", "Clear all actions?"):
            self.actions.clear()
            self._refresh_list()

    # ----- JSON -----
    def _export_json(self):
        if not self.actions:
            messagebox.showwarning("MacroMaster", "No actions to export.")
            return
        self.root.attributes("-topmost", False)
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Export Macro")
        self.root.attributes("-topmost", True)
        if path:
            try:
                with open(path, "w") as f:
                    json.dump([a.to_dict() for a in self.actions], f, indent=2)
                self.status_label.config(text=f"Exported  ·  {os.path.basename(path)}", fg=SUCCESS)
            except Exception as e:
                messagebox.showerror("MacroMaster", str(e))

    def _import_json(self):
        self.root.attributes("-topmost", False)
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Import Macro")
        self.root.attributes("-topmost", True)
        if path:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                self.actions = [MacroAction.from_dict(d) for d in data]
                self._refresh_list()
                self.status_label.config(text=f"Imported  ·  {len(self.actions)} actions", fg=SUCCESS)
            except Exception as e:
                messagebox.showerror("MacroMaster", f"Import failed:\n{e}")

    # ----- Dialog -----
    def _open_dialog(self, edit_idx=None):
        dlg = tk.Toplevel(self.root)
        dlg.title("Edit Action" if edit_idx is not None else "Add Action")
        dlg.geometry("360x440")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=PANEL)
        dlg.resizable(False, False)

        dlg.update_idletasks()
        px = self.root.winfo_x() + (self.root.winfo_width() - dlg.winfo_width()) // 2
        py = self.root.winfo_y() + (self.root.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{px}+{py}")

        act = self.actions[edit_idx] if edit_idx is not None else None

        def lbl(text):
            tk.Label(dlg, text=text, bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=16, pady=(12, 4))

        def entry(var):
            e = tk.Entry(dlg, textvariable=var, bg=BG, fg=FG, insertbackground=ACCENT,
                        relief=tk.FLAT, font=("Consolas", 11), highlightthickness=1, highlightbackground=BORDER)
            e.pack(fill=tk.X, padx=16, pady=(0, 4))
            return e

        lbl("Action Type")
        type_var = tk.StringVar(value=act.action_type if act else "click")
        ttk.Combobox(dlg, textvariable=type_var, values=["click", "right_click", "middle_click", "drag", "hold", "delay"],
                    state="readonly", font=("Segoe UI", 11)).pack(fill=tk.X, padx=16, pady=(0, 4))

        # Position row
        pos = tk.Frame(dlg, bg=PANEL)
        pos.pack(fill=tk.X, padx=16, pady=(8, 0))

        x_var = tk.StringVar(value=str(act.x) if act else "0")
        y_var = tk.StringVar(value=str(act.y) if act else "0")

        tk.Label(pos, text="X:", bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Entry(pos, textvariable=x_var, width=8, bg=BG, fg=FG, insertbackground=ACCENT,
                relief=tk.FLAT, font=("Consolas", 11), highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT, padx=(4, 10))
        tk.Label(pos, text="Y:", bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Entry(pos, textvariable=y_var, width=8, bg=BG, fg=FG, insertbackground=ACCENT,
                relief=tk.FLAT, font=("Consolas", 11), highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT, padx=(4, 10))

        pick = tk.Button(pos, text="Pick", bg=BORDER, fg=ACCENT, font=("Segoe UI", 9, "bold"),
                        relief=tk.FLAT, bd=0, cursor="hand2", command=lambda: self._pick_pos(x_var, y_var, dlg))
        pick.pack(side=tk.LEFT, padx=(4, 0))

        # End position
        pos2 = tk.Frame(dlg, bg=PANEL)
        pos2.pack(fill=tk.X, padx=16, pady=(8, 0))

        x2_var = tk.StringVar(value=str(act.x2) if act else "0")
        y2_var = tk.StringVar(value=str(act.y2) if act else "0")

        tk.Label(pos2, text="X2:", bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Entry(pos2, textvariable=x2_var, width=8, bg=BG, fg=FG, insertbackground=ACCENT,
                relief=tk.FLAT, font=("Consolas", 11), highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT, padx=(4, 10))
        tk.Label(pos2, text="Y2:", bg=PANEL, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Entry(pos2, textvariable=y2_var, width=8, bg=BG, fg=FG, insertbackground=ACCENT,
                relief=tk.FLAT, font=("Consolas", 11), highlightthickness=1, highlightbackground=BORDER).pack(side=tk.LEFT, padx=(4, 10))

        pick2 = tk.Button(pos2, text="Pick", bg=BORDER, fg=ACCENT, font=("Segoe UI", 9, "bold"),
                         relief=tk.FLAT, bd=0, cursor="hand2", command=lambda: self._pick_pos(x2_var, y2_var, dlg))
        pick2.pack(side=tk.LEFT, padx=(4, 0))

        lbl("Delay Before (seconds)")
        delay_var = tk.StringVar(value=str(act.delay) if act else "0.5")
        entry(delay_var)

        lbl("Duration / Hold Time (seconds)")
        dur_var = tk.StringVar(value=str(act.duration) if act else "0.0")
        entry(dur_var)

        lbl("Mouse Button")
        btn_var = tk.StringVar(value=act.button if act else "left")
        ttk.Combobox(dlg, textvariable=btn_var, values=["left", "right", "middle"],
                    state="readonly", font=("Segoe UI", 11)).pack(fill=tk.X, padx=16, pady=(0, 4))

        # Buttons
        btns = tk.Frame(dlg, bg=PANEL)
        btns.pack(fill=tk.X, padx=16, pady=(16, 12))

        def do_save():
            try:
                new_act = MacroAction(
                    action_type=type_var.get(),
                    x=int(x_var.get()), y=int(y_var.get()),
                    x2=int(x2_var.get()), y2=int(y2_var.get()),
                    delay=float(delay_var.get()),
                    duration=float(dur_var.get()),
                    button=btn_var.get()
                )
                if edit_idx is not None:
                    self.actions[edit_idx] = new_act
                else:
                    self.actions.append(new_act)
                self._refresh_list()
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("MacroMaster", f"Invalid input: {e}")

        tk.Button(btns, text="Save", bg=ACCENT, fg=BG, font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, bd=0, cursor="hand2", command=do_save,
                 activebackground=ACCENT_HOVER, padx=20, pady=4).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btns, text="Cancel", bg=BORDER, fg=FG, font=("Segoe UI", 10),
                 relief=tk.FLAT, bd=0, cursor="hand2", command=dlg.destroy,
                 activebackground="#374151", padx=20, pady=4).pack(side=tk.LEFT)

        dlg.bind("<Return>", lambda e: do_save())

    def _pick_pos(self, x_var, y_var, dlg):
        dlg.withdraw()
        self.root.after(700, lambda: self._do_pick(x_var, y_var, dlg))

    def _do_pick(self, x_var, y_var, dlg):
        x, y = self.engine.get_cursor_pos()
        x_var.set(str(x))
        y_var.set(str(y))
        dlg.deiconify()
        dlg.lift()
        dlg.grab_set()

    # ----- Hotkeys -----
    def _setup_hotkeys(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f6:
                    self.root.after(0, self._toggle_record)
                elif key == keyboard.Key.f7:
                    self.root.after(0, self._stop)
                elif key == keyboard.Key.f8:
                    self.root.after(0, self._play)
            except:
                pass
        keyboard.Listener(on_press=on_press).start()

    def _poll_queue(self):
        try:
            while True:
                act = self.recorder.queue.get_nowait()
                self.actions.append(act)
                self.action_list.insert(tk.END, f"  {len(self.actions):2d}    {act}")
                self.action_list.see(tk.END)
                self.status_label.config(text=f"Recorded {act.action_type}  ·  ({act.x}, {act.y})", fg=ACCENT)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MacroApp(root)
        root.mainloop()
    except Exception as e:
        err = traceback.format_exc()
        log_error(err)
        messagebox.showerror("MacroMaster", f"Fatal error:\n\n{e}\n\nSee macro_error.log")
