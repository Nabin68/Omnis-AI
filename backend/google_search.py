import os
import time
import subprocess
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

try:
    # Works in normal .py file
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    # Fallback for Jupyter / interactive
    BASE_DIR = os.path.abspath("..")


class GoogleSearchModule:
    # Google-specific driver (not shared with other modules)
    _google_driver = None
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
            cls._google_driver = driver
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
            cls._google_driver = driver
            return driver
        except Exception as e:
            print(f"❌ Failed to create new Chrome instance: {e}")
            return None

    @classmethod
    def get_or_create_driver(cls):
        """Get existing Google driver or create new one if needed"""
        # If we already have a driver, return it
        if cls._google_driver:
            try:
                # Test if driver is still alive
                cls._google_driver.current_url
                print("✅ Using existing Google driver!")
                return cls._google_driver
            except:
                print("⚠️ Existing Google driver is dead, creating new one...")
                cls._google_driver = None

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

        print("✅ Google Chrome driver ready!")
        return driver

    @classmethod
    def cleanup_driver(cls):
        """Clean up the Google driver"""
        if cls._google_driver:
            try:
                cls._google_driver.quit()
            except:
                pass
            cls._google_driver = None
            cls._connected_to_existing = False

    @classmethod
    def get_driver_status(cls):
        """Get current Google driver status"""
        if cls._google_driver:
            try:
                cls._google_driver.current_url
                return "Active"
            except:
                return "Dead"
        return "None"
    
    @staticmethod
    def google_search(query):
        try:
            # Get or create Google-specific driver
            driver = GoogleSearchModule.get_or_create_driver()
            
            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False
            
            # Open new tab if connected to existing Chrome
            if GoogleSearchModule._connected_to_existing:
                print("🔄 Opening new tab for Google search...")
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
            
            # Navigate to Google
            google_url = "https://www.google.com"
            driver.get(google_url)
            print(f"✅ Navigated to Google")
            
            # Wait for page to load
            time.sleep(2)
            
            # Find search box - try multiple selectors
            search_box = None
            search_selectors = [
                (By.NAME, "q"),
                (By.XPATH, "//textarea[@name='q']"),
                (By.XPATH, "//input[@name='q']"),
                (By.CSS_SELECTOR, "textarea[name='q']"),
                (By.CSS_SELECTOR, "input[name='q']")
            ]
            
            for by, selector in search_selectors:
                try:
                    search_box = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except:
                    continue
            
            if not search_box:
                print("❌ Search box not found!")
                return False
            
            search_box.clear()
            search_box.send_keys(query)
            print(f"✅ Entered query: '{query}'")
            
            # Submit search (press Enter)
            search_box.send_keys(Keys.RETURN)
            print("✅ Search submitted")
            
            time.sleep(2)
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "search"))
                )
                print("🎉 Google search results loaded successfully!")
            except:
                print("⚠️ Results loaded but couldn't confirm search results element")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during Google search: {e}")
            return False


# Example usage
if __name__ == "__main__":
    query = "Python Selenium tutorial"
    result = GoogleSearchModule.google_search(query)
    
    if result:
        print(f"\n✅ Successfully searched for: '{query}'")
    else:
        print(f"\n❌ Failed to search for: '{query}'")
    
    time.sleep(10)
    
    # Optional: Perform another search
    GoogleSearchModule.google_search("Artificial Intelligence")
    time.sleep(10)