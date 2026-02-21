import pytesseract
from pynput import mouse
from pynput import keyboard as pynput_keyboard
import pyautogui
import keyboard
import threading

class ScreenOCR:
    def __init__(self, hotkey=""):
        self.hotkey = hotkey
        self.recording = False
        self.clicks = []
        self.last_text = ""
        self.region = None
        self.config = r"--psm 6 -l eng"
        # Grab the file path
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        pytesseract.pytesseract.tessdata_dir = r"C:\Program Files\Tesseract-OCR\tessdata"
        self._mouse_listener = None
        self._keyboard_listener = None
        # Lock program independent
        self._lock = threading.Lock()

    # ---------- public API ----------
    def start(self):
        keyboard.add_hotkey(self.hotkey, self._start_recording)
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._mouse_listener.start()
        self._keyboard_listener = pynput_keyboard.Listener(on_press=self._on_key_press)
        self._keyboard_listener.start()

    def set_language(self, lang):
        self.config = f"--psm 6 -l {lang}"

    # Output OCR text result here
    def get_text(self,mode=1):
        # Mode1 mean keeping scan in the same axis
        if self.region and mode==1:
            img = pyautogui.screenshot(region=self.region)
            img.save('output.jpg', 'JPEG', quality=85)
            config = self.config
            self.last_text = pytesseract.image_to_string(img, config=config)
        text = self.last_text
        self.last_text = ""
        return text

    # ---------- internal ----------
    # When use hotkey open recording mode(mean start capture clicks axis)
    def _start_recording(self):
        with self._lock:
            if not self.recording:
                self.recording = True
                self.clicks.clear()
                print("OCR started")
    # Recording two clciks action
    def _on_click(self, x, y, button, pressed):
        if not pressed:
            return
        with self._lock:
            if not self.recording:
                return
            self.clicks.append((x, y))
            print(f"Clicked: {x}, {y}")
            if len(self.clicks) == 2:
                self._do_ocr()
                self.recording = False
                self.clicks.clear()
    def _on_key_press(self, key):
        try:
            if key.char == 'q' and self.recording:
                with self._lock:
                    x, y = pyautogui.position()
                    self.clicks.append((x, y))
                    print(f"Pressed q: {x}, {y}")
                    if len(self.clicks) == 2:
                        self._do_ocr()
                        self.recording = False
                        self.clicks.clear()
        except AttributeError:
            pass  # Ignore non-character keys
    # Define OCR action is from top left to bottom right
    # Generate img
    def _do_ocr(self):
        (x1, y1), (x2, y2) = self.clicks
        self.region = (x1, y1, abs(x1 - x2), abs(y1 - y2))
        img = pyautogui.screenshot(region=self.region)
        # Setting in English mode
        config = self.config
        # Truely OCR action
        self.last_text = pytesseract.image_to_string(img, config=config)
        print(repr(self.last_text))

