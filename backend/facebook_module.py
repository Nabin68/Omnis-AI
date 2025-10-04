import os
import time
import subprocess
import psutil
import pyautogui
import threading
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

try:
    # Works in normal .py file
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    # Fallback for Jupyter / interactive
    BASE_DIR = os.path.abspath("..")

env_path = os.path.join(BASE_DIR, ".env")
env = dotenv_values(env_path)

class FacebookModule:
    # Facebook-specific driver (not shared with other modules)
    _facebook_driver = None
    _connected_to_existing = False
    _facebook_tab_handle = None  # Store the handle of our Facebook tab
    
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
            cls._facebook_driver = driver
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
            cls._facebook_driver = driver
            return driver
        except Exception as e:
            print(f"❌ Failed to create new Chrome instance: {e}")
            return None

    @classmethod
    def get_or_create_driver(cls):
        """Get existing Facebook driver or create new one if needed"""
        # If we already have a driver, return it
        if cls._facebook_driver:
            try:
                # Test if driver is still alive
                cls._facebook_driver.current_url
                print("✅ Using existing Facebook driver!")
                return cls._facebook_driver
            except:
                print("⚠️ Existing Facebook driver is dead, creating new one...")
                cls._facebook_driver = None
                cls._facebook_tab_handle = None

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

        print("✅ Facebook Chrome driver ready!")
        return driver

    @classmethod
    def cleanup_driver(cls):
        """Clean up the Facebook driver"""
        if cls._facebook_driver:
            try:
                cls._facebook_driver.quit()
            except:
                pass
            cls._facebook_driver = None
            cls._facebook_tab_handle = None
            cls._connected_to_existing = False

    @classmethod
    def get_driver_status(cls):
        """Get current Facebook driver status"""
        if cls._facebook_driver:
            try:
                cls._facebook_driver.current_url
                return "Active"
            except:
                return "Dead"
        return "None"
    
    @classmethod
    def switch_to_facebook_tab(cls):
        """Switch to the Facebook tab if it exists, return True if successful"""
        if cls._facebook_tab_handle and cls._facebook_driver:
            try:
                # Check if our tab handle still exists
                if cls._facebook_tab_handle in cls._facebook_driver.window_handles:
                    cls._facebook_driver.switch_to.window(cls._facebook_tab_handle)
                    print("✅ Switched to existing Facebook tab")
                    return True
                else:
                    print("⚠️ Facebook tab no longer exists")
                    cls._facebook_tab_handle = None
                    return False
            except:
                cls._facebook_tab_handle = None
                return False
        return False
    
    @staticmethod
    def open_facebook(driver):
        """Function to login into Facebook"""
        try:
            # Store current window handles before opening new tab
            existing_handles = driver.window_handles.copy()
            print(f"📋 Current tabs before opening: {len(existing_handles)}")
            
            # Check if we already have a Facebook tab
            if FacebookModule.switch_to_facebook_tab():
                print("✅ Already on Facebook tab, refreshing...")
                driver.refresh()
            else:
                # Open NEW tab using JavaScript
                driver.execute_script("window.open('about:blank', '_blank');")
                time.sleep(1)  # Give time for new tab to open
                
                # Get the new tab handle (the one that wasn't in existing_handles)
                new_handles = driver.window_handles
                new_tab_handle = None
                
                for handle in new_handles:
                    if handle not in existing_handles:
                        new_tab_handle = handle
                        break
                
                if new_tab_handle:
                    # Store this as our Facebook tab
                    FacebookModule._facebook_tab_handle = new_tab_handle
                    driver.switch_to.window(new_tab_handle)
                    print(f"✅ Opened NEW tab (Total tabs: {len(new_handles)})")
                else:
                    print("⚠️ Could not identify new tab, using last handle")
                    FacebookModule._facebook_tab_handle = driver.window_handles[-1]
                    driver.switch_to.window(FacebookModule._facebook_tab_handle)
            
            # Navigate to Facebook
            facebook_url = "https://www.facebook.com"
            driver.get(facebook_url)
            time.sleep(2)

            # Check if login input is present
            if driver.find_elements(By.XPATH, "//input[@placeholder='Email address or phone number']"):
                print("🔑 Login required!")

                username = env.get("FACEBOOK_ID")
                password = env.get("FACEBOOK_PASSWORD")

                if not username or not password:
                    print("❌ Username or password not found in .env")
                    return False

                # Username input
                id_input_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email address or phone number']"))
                )
                time.sleep(1)
                id_input_box.clear()
                id_input_box.send_keys(username)

                # Password input
                try:
                    password_input_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
                    )
                    time.sleep(1)
                    password_input_box.clear()
                    password_input_box.send_keys(password)
                    print("✅ Password entered")
                except Exception:
                    print("❌ Password input box not found")
                    return False

                # Submit button
                try:
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @name='login']"))
                    )
                    driver.execute_script("arguments[0].click();", submit_button)
                    print("✅ Submit button clicked")
                except Exception:
                    print("❌ Submit button not found")
                    return False
                
                # Handle save info popup
                try:
                    save_info_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='OK']//span[text()='OK'][1]"))
                    )
                    save_info_button.click()
                    print("✅ Save info button clicked")
                except:
                    print("ℹ️ No Save Info button found!")
            else:
                print("✅ Already logged in")

            return True

        except Exception as e:
            print(f"❌ Error logging into Facebook: {e}")
            return False
    
    @staticmethod
    def facebook():
        """Main entry to Facebook module"""
        try:
            # Get or create Facebook-specific driver
            driver = FacebookModule.get_or_create_driver()
            
            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False
            
            success = FacebookModule.open_facebook(driver)
            
            if success:
                print("🎉 Facebook login successful!")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
    @staticmethod
    def play_videos():
        driver = FacebookModule.get_or_create_driver()
        # Make sure we're on the Facebook tab
        FacebookModule.switch_to_facebook_tab()
        
        try:
            videos_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//a[contains(@href,'/watch/')])[1]"))
            )
            driver.execute_script("arguments[0].click();", videos_button)
            print("✅ Video clicked")
        except Exception:
            print("❌ Video button not found")
        
        FacebookModule.mute_unmute_video()

        
    @staticmethod    
    def mute_unmute_video():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            # Try multiple possible selectors for video mute/unmute button
            video_mute_selectors = [
                "//div[contains(@aria-label, 'Mute') or contains(@aria-label, 'Unmute')]",
                "//button[contains(@aria-label, 'Mute') or contains(@aria-label, 'Unmute')]",
                "//*[contains(@aria-label, 'volume') or contains(@aria-label, 'Volume')]",
                "//div[@role='button' and contains(@aria-label, 'sound')]",
                "//video/..//div[contains(@class, 'volume')]"
            ]
            
            video_mute_button = None
            for selector in video_mute_selectors:
                try:
                    video_mute_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
                    
            if video_mute_button:
                video_mute_button.click()
                print("✅ Video Muted/Unmuted")
            else:
                print("ℹ️ Video Mute/Unmute button not found - trying keyboard shortcut")
                # Fallback: Try 'M' key for mute
                driver.find_element(By.TAG_NAME, 'body').send_keys('m')
                print("✅ Video Muted/Unmuted (using M key)")
                
        except Exception as e:
            print("❌ Video Mute/Unmute button not found:", e)
        
    @staticmethod
    def play_pause():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            play_pause_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Play') or contains(@aria-label, 'Pause')]"))
            )
            driver.execute_script("arguments[0].click();", play_pause_button)
            print("✅ Video play/pause toggled")
        except Exception as e:
            print("❌ Play/Pause button not found:", e)
    
    @staticmethod
    def next_story():
        pyautogui.press("right")
        print("✅ Pressed Next Story")
        
    @staticmethod
    def prev_story():
        pyautogui.press("left")
        print("✅ Pressed Previous story")
        
    
    @staticmethod
    def open_story():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            first_story = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-type='hscroll-child'][2]"))
            )
            first_story.click()
            print("✅ Story Opened")
        except Exception as e:
            print("❌ Story not found:", e)
            
    @staticmethod
    def close_story():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            # Try multiple possible selectors for close button
            close_selectors = [
                "//a[@aria-label='Close']",
                "//div[@aria-label='Close']",
                "//button[@aria-label='Close']",
                "//*[contains(@aria-label, 'Close')]",
                "//div[contains(@class, 'close')]//a",
                "//*[@role='button' and contains(text(), 'Close')]"
            ]
            
            close_button = None
            for selector in close_selectors:
                try:
                    close_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
                    
            if close_button:
                close_button.click()
                print("✅ Story Closed")
            else:
                # Fallback: Try ESC key
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                print("✅ Story Closed (using ESC key)")
                
        except Exception as e:
            print("❌ Story close button not found:", e)
        
    @staticmethod
    def mute_unmute_story():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            # Try multiple possible selectors for mute/unmute button
            mute_selectors = [
                "//div[contains(@aria-label, 'Mute') or contains(@aria-label, 'Unmute')]",
                "//button[contains(@aria-label, 'Mute') or contains(@aria-label, 'Unmute')]",
                "//*[contains(@aria-label, 'volume') or contains(@aria-label, 'Volume')]",
                "//*[contains(@aria-label, 'sound') or contains(@aria-label, 'Sound')]",
                "//div[contains(@class, 'volume')]//div[@role='button']"
            ]
            
            mute_button = None
            for selector in mute_selectors:
                try:
                    mute_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
                    
            if mute_button:
                mute_button.click()
                print("✅ Story Muted/Unmuted")
            else:
                print("ℹ️ Story Mute/Unmute button not found - trying keyboard shortcut")
                # Fallback: Try 'M' key for mute
                driver.find_element(By.TAG_NAME, 'body').send_keys('m')
                print("✅ Story Muted/Unmuted (using M key)")
                
        except Exception as e:
            print("❌ Story Mute/Unmute button not found:", e)
        
    @staticmethod
    def play_pause_story():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            print("🔑 Toggling story play/pause with SPACEBAR...")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
            print("✅ Story play/pause toggled with SPACEBAR")
            return True
        except Exception as e:
            print(f"❌ SPACEBAR failed: {e}")
            return False
        
    @staticmethod
    def to_home_page():
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        try:
            to_home_page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Home']"))
            )
            to_home_page_button.click()
            print("✅ Directed to home page")
        except Exception as e:
            print("❌ Home page button not found:", e)

    @staticmethod
    def scroll_feed_up(speed):
        """Scroll up the page at specified speed"""
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        FacebookModule.scrolling = True
        pixels, delay = FacebookModule.speed_map.get(speed, (1, 0.01))
        
        def run():
            while FacebookModule.scrolling:
                driver.execute_script(f"window.scrollBy(0, -{pixels});")
                time.sleep(delay)
        
        threading.Thread(target=run, daemon=True).start()
        print("Scrolling up...")

    @staticmethod
    def scroll_feed_down(speed):
        """Scroll down the page at specified speed"""
        driver = FacebookModule.get_or_create_driver()
        FacebookModule.switch_to_facebook_tab()
        
        FacebookModule.scrolling = True
        pixels, delay = FacebookModule.speed_map.get(speed, (1, 0.01))
        
        def run():
            while FacebookModule.scrolling:
                driver.execute_script(f"window.scrollBy(0, {pixels});")
                time.sleep(delay)
        
        threading.Thread(target=run, daemon=True).start()
        print("Scrolling down...")

    @staticmethod
    def stop_scroll_feed():
        """Stop the scrolling"""
        FacebookModule.scrolling = False
        print("Scrolling stopped.")


if __name__ == "__main__":
    result = FacebookModule.facebook()
    time.sleep(5)
    FacebookModule.scroll_feed_down(2)
    time.sleep(3)
    FacebookModule.stop_scroll_feed()
    time.sleep(3)
    FacebookModule.scroll_feed_up(2)
    time.sleep(3)
    FacebookModule.stop_scroll_feed()
    time.sleep(3)
    FacebookModule.open_story()
    time.sleep(3)
    FacebookModule.mute_unmute_story()
    time.sleep(3)
    FacebookModule.mute_unmute_story()
    time.sleep(3)
    FacebookModule.play_pause_story()
    time.sleep(3)
    FacebookModule.play_pause_story()
    time.sleep(3)
    FacebookModule.next_story()
    time.sleep(2)
    FacebookModule.prev_story()
    time.sleep(3)
    FacebookModule.close_story()
    time.sleep(3)
    FacebookModule.play_videos()
    time.sleep(3)
    FacebookModule.to_home_page()