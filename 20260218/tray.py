import os
from PIL import Image, ImageDraw
import pystray
import tkinter as tk

class TrayIcon:
    def __init__(self, on_exit_callback, on_settings_changed=None, config=None):
        self.on_exit_callback = on_exit_callback
        self.on_settings_changed = on_settings_changed
        self.config = config
        icon_image = self._load_icon("OCR.png")
        
        self.icon = pystray.Icon(
            "screenshot_tool",
            icon_image,
            "Screenshot Tool",
            menu=pystray.Menu(
                pystray.MenuItem("Settings", self._on_settings),
                pystray.MenuItem("Exit", self._on_exit)
            )
        )
        self.icon.run_detached()
    
    def _load_icon(self, icon_path):
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path).resize((64, 64), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Failed to load icon: {e}")
        
        img = Image.new('RGB', (64, 64), 'white')
        ImageDraw.Draw(img).ellipse((16, 16, 48, 48), fill='red')
        return img

    def _on_settings(self, icon, item):
        settings = {
            'screenshot_hotkey': self.config.get("hotkey", "-"),
            'OCRmode_hotkey': self.config.get("OCRmode_hotkey", "ctrl+q"),
            'screenshot_enabled': self.config.get("screenshot_enabled", True),
        }
        SettingsWindow(settings, self.on_settings_changed)

    def _on_exit(self, icon, item):
        self.icon.stop()
        self.on_exit_callback()


class SettingsWindow:
    def __init__(self, current_settings, on_save_callback):
        self.on_save_callback = on_save_callback
        self.win = tk.Toplevel()
        self.win.attributes('-topmost', True)
        self.win.title("Settings")
        self.win.geometry("320x400")
        self.win.resizable(False, False)
        self.mode = 0

        # === 截圖設定區 ===
        screenshot_frame = tk.LabelFrame(self.win, text="Screenshot", padx=10, pady=10)
        screenshot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # 截圖開關
        self.screenshot_enabled_var = tk.BooleanVar(value=current_settings['screenshot_enabled'])
        tk.Checkbutton(
            screenshot_frame, 
            text="Enable Screenshot", 
            variable=self.screenshot_enabled_var
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        

        # 模式選擇
        # tk.Label(self.win, text="Mode:").pack()
        # self.mode_var = tk.IntVar(value=self.mode)
        # tk.Radiobutton(self.win, text="only one time translate", variable=self.mode_var, value=0).pack()
        # tk.Radiobutton(self.win, text="Keeping translate same place", variable=self.mode_var, value=1).pack()

        # 進入OCR快捷鍵
        tk.Label(screenshot_frame, text="Hotkey:").grid(row=1, column=0, sticky="w", pady=5)
        self.OCRmode_hotkey_entry = tk.Entry(screenshot_frame, width=25)
        self.OCRmode_hotkey_entry.grid(row=1, column=1, pady=5)
        self.OCRmode_hotkey_entry.insert(0, current_settings['OCRmode_hotkey'])



        # 截圖快捷鍵
        tk.Label(screenshot_frame, text="Hotkey:").grid(row=2, column=0, sticky="w", pady=5)
        self.screenshot_hotkey_entry = tk.Entry(screenshot_frame, width=25)
        self.screenshot_hotkey_entry.grid(row=2, column=1, pady=5)
        self.screenshot_hotkey_entry.insert(0, current_settings['screenshot_hotkey'])

        
        # === 按鈕區域 ===
        btn_frame = tk.Frame(self.win)
        btn_frame.grid(row=3, column=0, pady=10)
        
        tk.Button(btn_frame, text="Save", command=self._save, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.win.destroy, width=10).pack(side="left", padx=5)
        
        self.win.focus_force()
    
    def _save(self):
        settings = {
            'screenshot_hotkey': self.screenshot_hotkey_entry.get().strip(),
            'OCRmode_hotkey': self.OCRmode_hotkey_entry.get().strip(),
            'screenshot_enabled': self.screenshot_enabled_var.get()
        }
        
        if self.on_save_callback:
            self.on_save_callback(settings)
        
        self.win.destroy()