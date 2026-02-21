import sys
import tkinter as tk
from OCR_tool import ScreenOCR
from base_translator import translate
import asyncio
import keyboard
from tray import TrayIcon
from config import Config
ocr = ScreenOCR(hotkey="ctrl+q")
ocr.start()
app = translate()
# 載入設定
config = Config()
class OCRViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OCR Result")
        self.root.geometry("400x200")
        self.text = tk.Text(self.root, wrap="word")
        self.text.pack(expand=True, fill="both")
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
        # Set to topmost window
        self.root.attributes('-topmost', True)
        self.mode = 0
        self.language = "eng"
        keyboard.add_hotkey("ctrl+shift+s", self.open_settings) 
    # Setting show text function
    def show_text(self, content):
        # Clear previous content
        self.text.delete("1.0", tk.END)
        # Insert new content
        self.text.insert(tk.END, content)
    def open_settings(self):
        settings = tk.Toplevel(self.root)
        settings.title("Settings")
        settings.geometry("300x250")
        settings.attributes('-topmost', True)
        tk.Label(settings, text="Mode:").pack()
        self.mode_var = tk.IntVar(value=self.mode)
        tk.Radiobutton(settings, text="only one time translate", variable=self.mode_var, value=0).pack()
        tk.Radiobutton(settings, text="Keeping translate same place", variable=self.mode_var, value=1).pack()
        tk.Label(settings, text="Language:").pack()
        self.lang_var = tk.StringVar(value=self.language)
        options = ["eng","jpn"]
        tk.OptionMenu(settings, self.lang_var, *options).pack()
        def save():
            self.mode = self.mode_var.get()
            self.language = self.lang_var.get()
            ocr.set_language(self.language)
            settings.destroy()
        tk.Button(settings, text="Save", command=save).pack()
        
    # Truely Result place
    def poll_ocr(self):
        # If mode=1 , keeping scan in the same axis
        text = ocr.get_text(mode=self.mode) 
        if text:
            result = asyncio.run(app.run(text))
            show_in_screen = f"{text}{result}"
            # Display OCR and translation result
            self.show_text(show_in_screen)
        # Repeat the loop after 200 ms
        self.root.after(200, self.poll_ocr)
    def run(self):
        self.poll_ocr()
        self.root.mainloop()

        # 設定變更處理
    def on_settings_changed(self, settings):
        config.set("hotkey", settings['screenshot_hotkey'])
        config.set("OCRmode_hotkey", settings['OCRmode_hotkey'])
        config.set("screenshot_enabled", settings['screenshot_enabled'])

    # 退出處理
    def exit_program(self):

        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def Tray(self):
        tray = TrayIcon(
            on_exit_callback=lambda: self.root.after(0, self.exit_program),
            on_settings_changed=lambda s: self.root.after(0, lambda: self.on_settings_changed(s)),
            config=config
        )

viewer = OCRViewer()
viewer.Tray()
viewer.run()
