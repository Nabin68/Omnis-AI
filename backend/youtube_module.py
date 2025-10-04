import os
import time
import subprocess
import psutil
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class YoutubeModule:
    """YouTube automation module for playing songs"""
    
    # YouTube-specific driver (not shared with other modules)
    _youtube_driver = None
    _connected_to_existing = False
    
    # Shared Chrome profile settings (same for all modules)
    _profile_path = r"C:\Users\KIIT\AppData\Local\Google\Chrome\User Data\SeleniumProfile"
    _debug_port = 9222
    
    @classmethod
    def is_chrome_profile_running(cls):
        """Check if Chrome is running with the specific profile"""
        profile_name = os.path.basename(cls._profile_path)
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    if proc.info['cmdline'] and any(profile_name in arg for arg in proc.info['cmdline']):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    @classmethod
    def start_chrome_with_remote_debugging(cls):
        """Start Chrome with remote debugging enabled"""
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        cmd = [
            chrome_path,
            f"--user-data-dir={cls._profile_path}",
            f"--remote-debugging-port={cls._debug_port}",
            "--no-first-run",
            "--no-default-browser-check"
        ]

        try:
            subprocess.Popen(cmd)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Failed to start Chrome: {e}")
            return False

    @classmethod
    def connect_to_existing_chrome(cls):
        """Connect to existing Chrome instance"""
        options = Options()
        options.add_experimental_option("debuggerAddress", f"localhost:{cls._debug_port}")

        try:
            driver = webdriver.Chrome(options=options)
            cls._connected_to_existing = True
            cls._youtube_driver = driver
            return driver
        except Exception as e:
            print(f"❌ Failed to connect to existing Chrome: {e}")
            return None

    @classmethod
    def create_new_chrome_instance(cls):
        """Create new Chrome instance (fallback method)"""
        options = Options()
        options.add_argument(f"--user-data-dir={cls._profile_path}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")

        try:
            driver = webdriver.Chrome(options=options)
            cls._connected_to_existing = False
            cls._youtube_driver = driver
            return driver
        except Exception as e:
            print(f"❌ Failed to create new Chrome instance: {e}")
            return None

    @classmethod
    def get_or_create_driver(cls):
        """Get existing YouTube driver or create new one if needed"""
        # If we already have a driver, return it
        if cls._youtube_driver:
            try:
                # Test if driver is still alive
                cls._youtube_driver.current_url
                print("✅ Using existing YouTube driver!")
                return cls._youtube_driver
            except:
                print("⚠️ Existing YouTube driver is dead, creating new one...")
                cls._youtube_driver = None

        # Try to get/create driver
        driver = None

        # Check if Chrome with our profile is already running
        if cls.is_chrome_profile_running():
            print("🔍 Chrome profile is already running, attempting to connect...")
            driver = cls.connect_to_existing_chrome()

            if driver:
                print("✅ Connected to existing Chrome instance!")
            else:
                print("⚠️ Could not connect to existing Chrome")
                print("🔄 Starting new Chrome instance with remote debugging...")

                if cls.start_chrome_with_remote_debugging():
                    driver = cls.connect_to_existing_chrome()

                if not driver:
                    print("🔄 Falling back to creating new Chrome instance...")
                    driver = cls.create_new_chrome_instance()
        else:
            print("🚀 No Chrome profile running, starting new instance...")

            if cls.start_chrome_with_remote_debugging():
                driver = cls.connect_to_existing_chrome()

            if not driver:
                print("🔄 Falling back to regular Chrome startup...")
                driver = cls.create_new_chrome_instance()

        if not driver:
            print("❌ Failed to create or connect to Chrome driver!")
            return None

        print("✅ YouTube Chrome driver ready!")
        return driver

    @classmethod
    def cleanup_driver(cls):
        """Clean up the YouTube driver"""
        if cls._youtube_driver:
            try:
                cls._youtube_driver.quit()
            except:
                pass
            cls._youtube_driver = None
            cls._connected_to_existing = False

    @classmethod
    def get_driver_status(cls):
        """Get current YouTube driver status"""
        if cls._youtube_driver:
            try:
                cls._youtube_driver.current_url
                return "Active"
            except:
                return "Dead"
        return "None"

    @staticmethod
    def play_youtube_song(driver, search_query):
        """Function to search and play YouTube song"""
        try:
            # Open new tab and navigate to YouTube
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])

            youtube_url = "https://www.youtube.com"
            driver.get(youtube_url)

            print(f"🎵 Searching for: {search_query}")

            # Find search box with multiple fallbacks
            try:
                searchbox = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input.ytSearchboxComponentInput.yt-searchbox-input.title"))
                )
            except:
                try:
                    searchbox = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input#search"))
                    )
                except:
                    searchbox = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='search_query']"))
                    )

            searchbox.clear()
            searchbox.send_keys(search_query)
            print("✅ Search box found and query entered!")

            # Click search button with multiple fallbacks
            try:
                searchbutton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytSearchboxComponentSearchButton.ytSearchboxComponentSearchButtonDark"))
                )
            except:
                try:
                    searchbutton = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Search']"))
                    )
                except:
                    searchbutton = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#search-icon-legacy"))
                    )

            searchbutton.click()
            print("✅ Search button clicked!")

            # Wait for results and click first video
            time.sleep(2)

            try:
                firstvideo = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "yt-formatted-string.style-scope.ytd-video-renderer"))
                )
            except:
                try:
                    firstvideo = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title"))
                    )
                except:
                    firstvideo = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "h3.title-and-badge a"))
                    )

            firstvideo.click()
            print("✅ First video clicked!")
            return True

        except Exception as e:
            print(f"❌ Error playing YouTube song: {e}")
            return False

    @staticmethod
    def youtube(search_query):
        """Main method to play YouTube song"""
        try:
            # Get or create YouTube-specific driver
            driver = YoutubeModule.get_or_create_driver()

            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False

            # Play the YouTube song
            success = YoutubeModule.play_youtube_song(driver, search_query)

            if success:
                print("🎵 Song is now playing!")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    @staticmethod
    def play():
        """Play the current video using keyboard shortcut"""
        pyautogui.press("k")
        print("▶️ Play/Pause toggled!")

    @staticmethod
    def pause():
        """Pause the current video using keyboard shortcut"""
        pyautogui.press("k")
        print("⏸️ Play/Pause toggled!")

    @staticmethod
    def mute_unmute():
        """Toggle mute/unmute using keyboard shortcut"""
        pyautogui.press("m")
        print("🔇 Mute/Unmute toggled!")

    @staticmethod
    def previous_video():
        """Go to previous video using keyboard shortcut"""
        pyautogui.hotkey("shift", "p")
        print("⏮️ Previous video!")

    @staticmethod
    def next_video():
        """Go to next video using keyboard shortcut"""
        pyautogui.hotkey("shift", "n")
        print("⏭️ Next video!")

    @staticmethod
    def volume_up():
        """Increase volume using keyboard shortcut"""
        pyautogui.press("up")
        print("🔊 Volume up!")

    @staticmethod
    def volume_down():
        """Decrease volume using keyboard shortcut"""
        pyautogui.press("down")
        print("🔉 Volume down!")

    @staticmethod
    def seek_forward():
        """Seek forward 10 seconds"""
        pyautogui.press("l")
        print("⏩ Seek forward 10s!")

    @staticmethod
    def seek_backward():
        """Seek backward 10 seconds"""
        pyautogui.press("j")
        print("⏪ Seek backward 10s!")

    @staticmethod
    def fullscreen():
        """Toggle fullscreen"""
        pyautogui.press("f")
        print("📺 Fullscreen toggled!")


if __name__ == "__main__":
    # Test the module
    result = YoutubeModule.youtube("Ganja bro")
    if result:
        print("✅ Successfully played the song!")

        # Test other functions with delays
        time.sleep(5)
        YoutubeModule.next_video()
        time.sleep(2)
        YoutubeModule.previous_video()
        time.sleep(2)
        YoutubeModule.volume_up()
        time.sleep(1)
        YoutubeModule.volume_down()
        time.sleep(2)
        YoutubeModule.pause()
        time.sleep(2)
        YoutubeModule.play()

    else:
        print("❌ Failed to play the song!")