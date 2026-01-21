import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import pyautogui
import math
import platform
import os

# Check if running on MacOS
IS_MAC = platform.system() == 'Darwin'

class AutoMouseSwitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Mouse & Switcher")
        self.root.geometry("220x50")
        
        # Removes the window frame (Close/Minimize buttons)
        self.root.overrideredirect(True)
        
        # Keep window on top
        self.root.wm_attributes("-topmost", True)
        self.root.configure(bg="black")

        self.running = False
        self.paused = False
        self.thread = None

        # --- UI Setup ---
        toolbar = tk.Frame(root, bg="black")
        toolbar.pack(expand=True, fill='both')

        self.btn_start = tk.Button(toolbar, text="▶", font=("Arial", 14), bg="black", fg="white", highlightbackground="black", borderwidth=0, command=self.start)
        self.btn_start.pack(side="left", expand=True, fill='both')

        self.btn_pause = tk.Button(toolbar, text="⏸", font=("Arial", 14), bg="black", fg="white", highlightbackground="black", borderwidth=0, command=self.pause, state='disabled')
        self.btn_pause.pack(side="left", expand=True, fill='both')

        self.btn_stop = tk.Button(toolbar, text="⏹", font=("Arial", 14), bg="black", fg="white", highlightbackground="black", borderwidth=0, command=self.stop, state='disabled')
        self.btn_stop.pack(side="left", expand=True, fill='both')

        self.btn_exit = tk.Button(toolbar, text="❌", font=("Arial", 12), bg="black", fg="red", highlightbackground="black", borderwidth=0, command=self.exit_app)
        self.btn_exit.pack(side="left", expand=True, fill='both')

        # --- Bindings ---
        # Allow moving the frameless window
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        # Right click menu
        self.root.bind("<Button-2>" if IS_MAC else "<Button-3>", self.show_menu) # Mac often uses Button-2 for context menus depending on mouse setup
        self.root.bind("<Control-Button-1>", self.show_menu) # Ctrl+Click for Mac users
        
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Exit", command=self.exit_app)

        # Hotkeys to quit
        self.root.bind("<Control-q>", lambda e: self.exit_app())
        self.root.bind("<Command-q>", lambda e: self.exit_app()) # Mac Standard

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def exit_app(self):
        self.stop()
        self.root.destroy()

    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{timestamp}] {message}"
        
        # Save log to User/Documents to avoid permission errors on Mac
        log_path = os.path.join(os.path.expanduser("~/Documents"), "automouse_log.txt")
        
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass # Fail silently if permissions deny writing

    def move_mouse(self):
        screen_width, screen_height = pyautogui.size()
        x0, y0 = pyautogui.position()
        choice = random.choice(['back_forth', 'circle', 'random'])

        if choice == 'back_forth':
            dx = random.randint(200, 400)
            dy = random.randint(-150, 150)
            # Ensure we don't go off screen
            target_x = max(0, min(screen_width, x0 + dx))
            target_y = max(0, min(screen_height, y0 + dy))
            
            pyautogui.moveTo(target_x, target_y, duration=0.3)
            time.sleep(0.2)
            pyautogui.moveTo(x0, y0, duration=0.3)
            time.sleep(0.2)
            self.log(f"Mouse back-and-forth from ({x0},{y0})")

        elif choice == 'circle':
            radius = random.randint(50, 150)
            steps = 20
            for i in range(steps):
                angle = 2 * math.pi * i / steps
                x = int(x0 + radius * math.cos(angle))
                y = int(y0 + radius * math.sin(angle))
                x = max(10, min(screen_width - 10, x))
                y = max(10, min(screen_height - 10, y))
                pyautogui.moveTo(x, y, duration=0.05)
            time.sleep(0.2)
            self.log(f"Mouse circular movement with radius {radius}")

        else:
            x = random.randint(10, screen_width - 10)
            y = random.randint(10, screen_height - 10)
            pyautogui.moveTo(x, y, duration=0.5)
            self.log(f"Mouse moved randomly to ({x}, {y})")

    def alt_tab_switch_multiple(self, times=3):
        # Determine the key based on OS
        modifier_key = 'command' if IS_MAC else 'alt'
        
        pyautogui.keyDown(modifier_key)
        for _ in range(times):
            pyautogui.press('tab')
            time.sleep(0.3)
        pyautogui.keyUp(modifier_key)
        
        self.log(f"Switched windows ({modifier_key}+Tab × {times})")

    def worker(self):
        self.log("Started.")
        while self.running:
            if self.paused:
                time.sleep(0.5)
                continue

            try:
                sleep_time = random.randint(1, 3)
                for _ in range(sleep_time):
                    if not self.running or self.paused:
                        break
                    time.sleep(1)
                if not self.running or self.paused:
                    continue

                self.move_mouse()

                if random.random() < 0.8:
                    self.alt_tab_switch_multiple(random.randint(1, 4))

            except Exception as e:
                self.log(f"❌ Error caught: {str(e)}")
                self.log("🔁 Retrying after 5 seconds...")
                time.sleep(5)
                continue

        self.log("Stopped.")

    def start(self):
        if self.running:
            return
        self.running = True
        self.paused = False
        self.btn_start.config(state='disabled')
        self.btn_pause.config(state='normal', text='⏸')
        self.btn_stop.config(state='normal')
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.btn_pause.config(text="▶")
            self.log("Paused.")
        else:
            self.btn_pause.config(text="⏸")
            self.log("Resumed.")

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.paused = False
        self.btn_start.config(state='normal')
        self.btn_pause.config(state='disabled', text="⏸")
        self.btn_stop.config(state='disabled')

    def on_closing(self):
        self.exit_app()

if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    root = tk.Tk()
    app = AutoMouseSwitcherApp(root)
    root.mainloop()
