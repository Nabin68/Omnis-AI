import os
import time
import subprocess
import psutil
import win32gui
import win32process

class Core():
    # Mapping dictionary: keyword (lowercase) → friendly name
    APP_MAPPINGS = {
        "youtube": "YouTube",
        "instagram": "Instagram",
        "facebook": "Facebook",
        "merolagani": "Merolagani",
        "chrome": "Google Chrome",
        "code": "Visual Studio Code",
        "explorer": "File Explorer",
        "control panel": "Control Panel",
        "settings": "Settings",
        "whatsapp": "WhatsApp",
        "notepad": "Notepad",
        "word": "Microsoft Word",
        "excel": "Microsoft Excel",
        "powerpnt": "Microsoft PowerPoint",
    }

    @staticmethod
    def get_foreground_app():
        """Return a friendly name of the currently active (foreground) application"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name().lower()  # e.g., chrome.exe, code.exe
            window_title = win32gui.GetWindowText(hwnd)  # original case

            combined = f"{app_name} {window_title.lower()}"

            # Match against dictionary
            for keyword, friendly_name in Core.APP_MAPPINGS.items():
                if keyword in combined:
                    # Special handling for Chrome to show site
                    if keyword == "chrome":
                        if " - " in window_title:
                            site = window_title.split(" - ")[0]
                            return f"Chrome - {site}"
                        else:
                            return "Google Chrome"
                    return friendly_name

            # Default fallback
            return f"{process.name()} - {window_title}"
        except Exception as e:
            print(f"❌ Could not get foreground app: {e}")
            return None

if __name__ == "__main__":
    model = Core()
    time.sleep(2)
    print(model.get_foreground_app())
