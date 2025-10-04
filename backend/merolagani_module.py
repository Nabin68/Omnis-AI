import os
import time
import subprocess
import psutil
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class MerolaganiModule:
    # Merolagani-specific driver (not shared with other modules)
    _merolagani_driver = None
    _connected_to_existing = False
    
    # Shared Chrome profile settings (same for all modules)
    _profile_path = r"C:\Users\KIIT\AppData\Local\Google\Chrome\User Data\SeleniumProfile"
    _debug_port = 9222
    
    # Class-level variables for scroll control
    scrolling = False
    
    # Map speed to pixels per step and delay
    speed_map = {
        1: (1, 0.01),
        2: (2, 0.008),
        3: (4, 0.005),
        4: (6, 0.003),
        5: (10, 0.001)
    }
    
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
            cls._merolagani_driver = driver
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
            cls._merolagani_driver = driver
            return driver
        except Exception as e:
            print(f"❌ Failed to create new Chrome instance: {e}")
            return None

    @classmethod
    def get_or_create_driver(cls):
        """Get existing Merolagani driver or create new one if needed"""
        # If we already have a driver, return it
        if cls._merolagani_driver:
            try:
                # Test if driver is still alive
                cls._merolagani_driver.current_url
                print("✅ Using existing Merolagani driver!")
                return cls._merolagani_driver
            except:
                print("⚠️ Existing Merolagani driver is dead, creating new one...")
                cls._merolagani_driver = None

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

        print("✅ Merolagani Chrome driver ready!")
        return driver

    @classmethod
    def cleanup_driver(cls):
        """Clean up the Merolagani driver"""
        if cls._merolagani_driver:
            try:
                cls._merolagani_driver.quit()
            except:
                pass
            cls._merolagani_driver = None
            cls._connected_to_existing = False

    @classmethod
    def get_driver_status(cls):
        """Get current Merolagani driver status"""
        if cls._merolagani_driver:
            try:
                cls._merolagani_driver.current_url
                return "Active"
            except:
                return "Dead"
        return "None"
    
    @staticmethod
    def scroll_down(speed=1):
        """Scroll down the page at specified speed"""
        driver = MerolaganiModule.get_or_create_driver()
        MerolaganiModule.scrolling = True
        pixels, delay = MerolaganiModule.speed_map.get(speed, (1, 0.01))
        
        def run():
            while MerolaganiModule.scrolling:
                driver.execute_script(f"window.scrollBy(0, {pixels});")
                time.sleep(delay)
        
        threading.Thread(target=run, daemon=True).start()
        print("Scrolling down...")

    @staticmethod
    def scroll_up(speed=1):
        """Scroll up the page at specified speed"""
        driver = MerolaganiModule.get_or_create_driver()
        MerolaganiModule.scrolling = True
        pixels, delay = MerolaganiModule.speed_map.get(speed, (1, 0.01))
        
        def run():
            while MerolaganiModule.scrolling:
                driver.execute_script(f"window.scrollBy(0, -{pixels});")
                time.sleep(delay)
        
        threading.Thread(target=run, daemon=True).start()
        print("Scrolling up...")

    @staticmethod
    def stop_scroll():
        """Stop the scrolling"""
        MerolaganiModule.scrolling = False
        print("Scrolling stopped.")
        
    @staticmethod
    def open_merolagani(query, driver):
        """Function to open Merolagani and search"""
        try:
            # Open new tab and navigate to Merolagani
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            merolagani_url = "https://merolagani.com"
            driver.get(merolagani_url)
            print("✅ Mero Lagani Opened")
            
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='ctl00$AutoSuggest1$txtAutoSuggest']"))
                )
                search_box.send_keys(query)
                print("✅ Query entered")
            except:
                print("❌ Error finding search box")
                
            try:
                search_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@id='ctl00_lbtnSearch']"))
                )
                search_button.click()
                print("✅ Search button clicked")
            except:
                print("❌ Error finding search button to Enter")
            
            time.sleep(2)
            MerolaganiModule.scroll_down(speed=2)
            time.sleep(2)
            MerolaganiModule.stop_scroll()
            
            return True
        except Exception as e:
            print(f"❌ Error opening Merolagani: {e}")
            return False
    
    @staticmethod
    def merolagani(query):
        """Main entry to Merolagani module"""
        try:
            # Get or create Merolagani-specific driver
            driver = MerolaganiModule.get_or_create_driver()
            
            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False
            
            success = MerolaganiModule.open_merolagani(query, driver)
            
            if success:
                print("🎉 Merolagani opened successfully!")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False


if __name__ == "__main__":
    MerolaganiModule.merolagani("HRL")
    MerolaganiModule.scroll_down(speed=2)  # start scrolling down
    time.sleep(3)          # scroll for 3 seconds
    MerolaganiModule.stop_scroll()           # stop scrolling
    time.sleep(1)
    MerolaganiModule.scroll_up(speed=3)      # start scrolling up
    time.sleep(2)
    MerolaganiModule.stop_scroll()           # stop scrolling