import os
import subprocess
import psutil
import time
import pygetwindow as gw
import keyboard
import pyautogui
from datetime import datetime
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import wmi
import win32gui
import win32process


class SystemAutomation:
    def __init__(self):
        # Dictionary of apps with paths/commands
        self.apps = {
            "notepad": r"C:\Windows\System32\notepad.exe",
            "paint": r"C:\Windows\System32\mspaint.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "vscode": r"C:\Users\KIIT\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "settings": "ms-settings:",
            "camera": "microsoft.windows.camera:",
            "calculator": "calculator:",
            "mycomputer": "explorer.exe shell:MyComputerFolder",
            "explorer": "explorer.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "whatsapp": "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
            "controlpanel": r"C:\Windows\System32\control.exe"
        }
        
        # Initialize WMI for brightness control
        self.wmi_interface = wmi.WMI(namespace='wmi')
        self.brightness_methods = self.wmi_interface.WmiMonitorBrightnessMethods()[0]
        self.brightness_levels = self.wmi_interface.WmiMonitorBrightness()[0]
        
        # App tracking mappings
        self.APP_MAPPINGS = {
            "youtube": "Chrome - YouTube",
            "instagram": "Chrome - Instagram",
            "facebook": "Chrome - Facebook",
            "merolagani": "Chrome - Merolagani",
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

    # ==================== APP MANAGEMENT ====================
    
    def open_app(self, app_name):
        """Open an application"""
        app = self.apps.get(app_name.lower())
        if not app:
            print(f"App '{app_name}' not found in dictionary.")
            return

        try:
            # For URIs or shell commands
            if app.endswith(":") or app.lower().startswith("shell:") or app_name.lower() in ["cmd", "explorer", "mycomputer"]:
                os.system(f"start {app}")
            else:
                subprocess.Popen(app)
            print(f"{app_name} app opened")
        except Exception as e:
            print(f"Error opening {app_name}: {e}")

    def close_app(self, app_name):
        """Close an application"""
        app_name = app_name.lower()

        # Special case: UWP apps (Settings, Camera, Calculator)
        if app_name in ["settings", "camera", "calculator"]:
            os.system("taskkill /F /IM ApplicationFrameHost.exe")
            return

        # Special case: Explorer / This PC
        if app_name in ["explorer", "mycomputer"]:
            os.system("taskkill /F /IM explorer.exe")  # Close all Explorer windows
            time.sleep(1)
            os.system("start explorer.exe")  # Restart Windows shell safely
            return

        # Special case: Control Panel
        if app_name == "controlpanel":
            windows = gw.getWindowsWithTitle("Control Panel")
            if windows:
                for win in windows:
                    try:
                        win.close()  # Close the visible window
                    except:
                        pass
            else:
                # fallback if window not found
                os.system("taskkill /F /IM control.exe")
            return

        # Normal apps: try taskkill first
        try:
            os.system(f"taskkill /F /IM {app_name}.exe")
        except Exception:
            # Fallback to psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and app_name in proc.info['name'].lower():
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

    # ==================== WINDOW MANAGEMENT ====================
    
    def switch_apps(self, sub):
        """Switch to an application window by title"""
        wins = gw.getWindowsWithTitle(sub)
        if not wins:
            print(f"❌ No window found with title containing: {sub}")
            return False

        win = wins[0]
        was_max = win.isMaximized
        was_min = win.isMinimized

        try:
            if was_min:
                win.restore()
                time.sleep(0.2)
            
            win.activate()
        except:
            win.minimize()
            time.sleep(0.2)
            win.restore()
            if was_max:
                win.maximize()

        print(f"✅ Switched to: {sub}")
        return True

    def switch_chrome_tab(self, name):
        """Switch to a Chrome tab by name"""
        keyboard.send('ctrl+shift+a')
        time.sleep(0.3)
        pyautogui.typewrite(name, interval=0.02)
        time.sleep(0.2)
        keyboard.send('enter')
        print(f"Switched to {name}")

    def show_desktop(self):
        """Show desktop (minimize all windows)"""
        pyautogui.hotkey("win", "d")

    def minimize_active_window(self):
        """Find the active window and minimize it"""
        win = gw.getActiveWindow()
        if win:
            print(f"🟢 Active window: {win.title}")
            win.minimize()
            print("✅ Window minimized")
        else:
            print("❌ No active window detected")

    # ==================== SCREENSHOT ====================
    
    def take_screenshot(self, save_path=None):
        """Take a screenshot and save it"""
        script_dir = os.getcwd()
        screenshot_dir = os.path.join(script_dir, "data", "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        if save_path is None:
            save_path = os.path.join(screenshot_dir, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        else:
            save_path = os.path.join(screenshot_dir, save_path)

        img = pyautogui.screenshot()
        img.save(save_path)
        return save_path

    # ==================== AUDIO CONTROL ====================
    
    def _get_volume(self):
        """Return system audio endpoint volume object"""
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def set_volume(self, percent: float):
        """Set system volume (0-100)"""
        volume = self._get_volume()
        percent = max(0, min(100, percent))
        volume.SetMasterVolumeLevelScalar(percent / 100.0, None)

    def change_volume_by(self, delta_percent: float):
        """Increase or decrease system volume by delta_percent"""
        volume = self._get_volume()
        cur = volume.GetMasterVolumeLevelScalar()
        new = max(0.0, min(1.0, cur + delta_percent / 100.0))
        volume.SetMasterVolumeLevelScalar(new, None)

    def mute_system(self):
        """Mute system volume"""
        volume = self._get_volume()
        volume.SetMute(1, None)
        print("System sound Muted!")

    def unmute_system(self):
        """Unmute system volume"""
        volume = self._get_volume()
        volume.SetMute(0, None)
        print("System sound Unmuted!")

    # ==================== BRIGHTNESS CONTROL ====================
    
    def set_brightness(self, percent: int):
        """Set screen brightness (0-100)"""
        percent = max(0, min(100, percent))
        self.brightness_methods.WmiSetBrightness(percent, 0)
        print(f"Brightness set to {percent}%")

    def change_brightness_by(self, delta: int):
        """Increase or decrease brightness by delta"""
        current = self.brightness_levels.CurrentBrightness
        new = max(0, min(100, current + delta))
        self.set_brightness(new)

    def get_brightness(self):
        """Get current brightness level (0-100)"""
        return self.brightness_levels.CurrentBrightness

    # ==================== APP TRACKING ====================
    
    def get_foreground_app(self):
        """Return a friendly name of the currently active application"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name().lower()
            window_title = win32gui.GetWindowText(hwnd).lower()
            
            combined = f"{app_name} {window_title}"

            # Match against dictionary
            for keyword, friendly_name in self.APP_MAPPINGS.items():
                if keyword in combined:
                    return friendly_name

            # Default fallback
            return f"{process.name()} - {win32gui.GetWindowText(hwnd)}"
        except Exception as e:
            print(f"❌ Could not get foreground app: {e}")
            return None


# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    automation = SystemAutomation()
    
    # Open and close apps
    automation.open_app("controlpanel")
    time.sleep(2)
    automation.close_app("controlpanel")
    
    # Window management
    automation.switch_apps("settings")
    automation.switch_apps("Whatsapp")
    
    # Chrome tab switching
    time.sleep(3)
    automation.switch_chrome_tab("YouTube")
    
    # Screenshot
    print(f"Screenshot saved at: {automation.take_screenshot()}")
    
    # Volume control
    automation.set_volume(40)
    automation.change_volume_by(-20)
    automation.mute_system()
    time.sleep(3)
    automation.unmute_system()
    
    # Desktop and window control
    automation.show_desktop()
    time.sleep(3)
    automation.minimize_active_window()
    
    # Brightness control
    print("Current brightness:", automation.get_brightness())
    automation.set_brightness(50)
    time.sleep(2)
    automation.change_brightness_by(50)
    print("Current brightness:", automation.get_brightness())
    
    # App tracking
    time.sleep(2)
    print("Foreground app:", automation.get_foreground_app())