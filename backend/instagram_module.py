import os
import time
import threading
import subprocess
import psutil
import pyautogui
from dotenv import dotenv_values
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

env_path = os.path.join(BASE_DIR, ".env")
env = dotenv_values(env_path)

class InstagramModule:
    # Instagram-specific driver (not shared with other modules)
    _instagram_driver = None
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
            cls._instagram_driver = driver
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
            cls._instagram_driver = driver
            return driver
        except Exception as e:
            print(f"❌ Failed to create new Chrome instance: {e}")
            return None

    @classmethod
    def get_or_create_driver(cls):
        """Get existing Instagram driver or create new one if needed"""
        # If we already have a driver, return it
        if cls._instagram_driver:
            try:
                # Test if driver is still alive
                cls._instagram_driver.current_url
                print("✅ Using existing Instagram driver!")
                return cls._instagram_driver
            except:
                print("⚠️ Existing Instagram driver is dead, creating new one...")
                cls._instagram_driver = None

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

        print("✅ Instagram Chrome driver ready!")
        return driver

    @classmethod
    def cleanup_driver(cls):
        """Clean up the Instagram driver"""
        if cls._instagram_driver:
            try:
                cls._instagram_driver.quit()
            except:
                pass
            cls._instagram_driver = None
            cls._connected_to_existing = False

    @classmethod
    def get_driver_status(cls):
        """Get current Instagram driver status"""
        if cls._instagram_driver:
            try:
                cls._instagram_driver.current_url
                return "Active"
            except:
                return "Dead"
        return "None"
    
    @staticmethod
    def open_instagram(driver):
        """Function to login into Instagram"""
        try:
            # Open new tab and navigate to Instagram
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            instagram_url = "https://www.instagram.com"
            driver.get(instagram_url)
            
            # Wait for page to load
            time.sleep(3)

            # Check if login input is present
            if driver.find_elements(By.XPATH, "//input[@aria-label='Phone number, username, or email']"):
                print("🔑 Login required!")

                username = env.get("INSTAGRAM_ID")
                password = env.get("INSTAGRAM_PASSWORD")

                if not username or password:
                    print("❌ Username or password not found in .env")
                    return False

                # Username input
                id_input_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Phone number, username, or email']"))
                )
                id_input_box.clear()
                id_input_box.send_keys(username)

                # Password input
                try:
                    password_input_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Password']"))
                    )
                    password_input_box.clear()
                    password_input_box.send_keys(password)
                    print("✅ Password entered")
                except Exception:
                    print("❌ Password input box not found")
                    return False

                # Submit button
                try:
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                    )
                    driver.execute_script("arguments[0].click();", submit_button)
                    print("✅ Submit button clicked")
                    
                    # Wait for login to process
                    time.sleep(3)
                except Exception:
                    print("❌ Submit button not found")
                    return False
                
                # Handle save info popup
                try:
                    save_info_selectors = [
                        "button._aswp._aswr._aswu._asw_._asx2",
                        "//button[contains(text(), 'Not Now') or contains(text(), 'Save Info')]",
                        "//div[@role='button'][contains(text(), 'Not Now')]"
                    ]
                    
                    save_info_button = None
                    for selector in save_info_selectors:
                        try:
                            if selector.startswith("//"):
                                save_info_button = WebDriverWait(driver, 2).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                            else:
                                save_info_button = WebDriverWait(driver, 2).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                            break
                        except:
                            continue
                    
                    if save_info_button:
                        save_info_button.click()
                        print("✅ Save info button clicked")
                    else:
                        print("ℹ️ No Save Info button found (might not be needed)")
                        
                except Exception as e:
                    print(f"ℹ️ Save info handling: {e}")

            else:
                print("✅ Already logged in")

            return True

        except Exception as e:
            print(f"❌ Error logging into Instagram: {e}")
            return False
    
    @staticmethod
    def instagram():
        """Main entry to Instagram module"""
        try:
            # Get or create Instagram-specific driver
            driver = InstagramModule.get_or_create_driver()
            
            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False
            
            success = InstagramModule.open_instagram(driver)
            
            if success:
                print("🎉 Instagram login successful!")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
    @staticmethod
    def play_reels():
        driver = InstagramModule.get_or_create_driver()
        try:
            # Try multiple selectors for reels button
            reels_selectors = [
                "//a[@href='/reels/']",
                "//a[contains(@href, 'reels')]",
                "//span[text()='Reels']/parent::a"
            ]
            
            reels_button = None
            for selector in reels_selectors:
                try:
                    reels_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if reels_button:
                driver.execute_script("arguments[0].click();", reels_button)
                print("✅ Reels button clicked")
                time.sleep(2)
                InstagramModule.mute_unmute()
            else:
                print("❌ Reels button not found")
        except Exception as e:
            print(f"❌ Error opening reels: {e}")
        
    @staticmethod    
    def mute_unmute():
        try:
            pyautogui.click(x=1258, y=203)
            print("✅ Mute/Unmute button pressed")
        except Exception as e:
            print(f"❌ Mute/Unmute failed: {e}")
        
    @staticmethod
    def play_pause():
        driver = InstagramModule.get_or_create_driver()
        try:
            # Try using spacebar first (more reliable)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
            print("✅ Play/Pause toggled with spacebar")
        except Exception:
            try:
                # Fallback to clicking play/pause button
                play_pause_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "(//div[@role='button' and @tabindex='0' and @style='cursor: pointer;'])[1]"))
                )
                driver.execute_script("arguments[0].click();", play_pause_button)
                print("✅ Play/Pause button clicked")
            except Exception as e:
                print(f"❌ Play/Pause failed: {e}")
            
    @staticmethod        
    def scroll_up():
        try:
            pyautogui.press("up")
            print("✅ Scrolled up!")
        except Exception as e:
            print(f"❌ Scroll up failed: {e}")
        
    @staticmethod
    def scroll_down():
        try:
            pyautogui.press("down")
            print("✅ Scrolled down!")
        except Exception as e:
            print(f"❌ Scroll down failed: {e}")
    
    @staticmethod
    def next_story():
        try:
            pyautogui.press("right")
            print("✅ Pressed Next Story")
        except Exception as e:
            print(f"❌ Next story failed: {e}")
        
    @staticmethod
    def prev_story():
        try:
            pyautogui.press("left")
            print("✅ Pressed Previous story")
        except Exception as e:
            print(f"❌ Previous story failed: {e}")
        
    @staticmethod
    def open_story():
        driver = InstagramModule.get_or_create_driver()
        try:
            # Try multiple selectors for story
            story_selectors = [
                "//li[@class and contains(@class, '_acaz')]//div[@role='button' and @tabindex='0']",
                "//div[contains(@class, 'story')]//div[@role='button']",
                "//canvas[contains(@class, 'x1lliihq')]"
            ]
            
            first_story = None
            for selector in story_selectors:
                try:
                    first_story = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if first_story:
                first_story.click()
                print("✅ Story opened")
            else:
                print("❌ Story not found")
        except Exception as e:
            print(f"❌ Story opening failed: {e}")
            
    @staticmethod
    def close_story():
        driver = InstagramModule.get_or_create_driver()
        try:
            print("🔑 Closing story with ESC key...")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            print("✅ Story closed with ESC key")
            return True
        except Exception as e:
            print(f"❌ ESC key failed: {e}")
            return False
        
    @staticmethod
    def mute_unmute_story():
        try:
            pyautogui.press("m")
            print("✅ Story Mute/Unmute key pressed")
        except Exception as e:
            print(f"❌ Story mute/unmute failed: {e}")
        
    @staticmethod
    def play_pause_story():
        driver = InstagramModule.get_or_create_driver()
        try:
            print("🔑 Toggling story play/pause with SPACEBAR...")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
            print("✅ Story play/pause toggled with SPACEBAR")
            return True
        except Exception as e:
            print(f"❌ SPACEBAR failed: {e}")
            return False

    @staticmethod
    def scroll_feed_down(speed):
        """Scroll down the page at specified speed"""
        driver = InstagramModule.get_or_create_driver()
        InstagramModule.scrolling = True
        pixels, delay = InstagramModule.speed_map.get(speed, (1, 0.01))
        
        def run():
            while InstagramModule.scrolling:
                driver.execute_script(f"window.scrollBy(0, {pixels});")
                time.sleep(delay)
        
        threading.Thread(target=run, daemon=True).start()
        print("Scrolling down...")

    @staticmethod
    def scroll_feed_up(speed):
        """Scroll up the page at specified speed"""
        driver = InstagramModule.get_or_create_driver()
        InstagramModule.scrolling = True
        pixels, delay = InstagramModule.speed_map.get(speed, (1, 0.01))
        
        def run():
            while InstagramModule.scrolling:
                driver.execute_script(f"window.scrollBy(0, -{pixels});")
                time.sleep(delay)
        
        threading.Thread(target=run, daemon=True).start()
        print("Scrolling up...")
        
    @staticmethod
    def stop_scroll_feed():
        """Stop the scrolling"""
        InstagramModule.scrolling = False
        print("Scrolling stopped.")

  
if __name__ == "__main__":
    result = InstagramModule.instagram()
    time.sleep(5)
    InstagramModule.scroll_feed_down(1)
    time.sleep(3)
    InstagramModule.stop_scroll_feed()
    time.sleep(3)
    InstagramModule.scroll_feed_up(1)
    time.sleep(3)
    InstagramModule.stop_scroll_feed()
    time.sleep(3)
    InstagramModule.open_story()
    time.sleep(3)
    InstagramModule.mute_unmute_story()
    time.sleep(3)
    InstagramModule.mute_unmute_story()
    time.sleep(3)
    InstagramModule.next_story()
    time.sleep(2)
    InstagramModule.prev_story()
    time.sleep(2)
    InstagramModule.play_pause_story()
    time.sleep(3)
    InstagramModule.play_pause_story()
    time.sleep(3)
    InstagramModule.close_story()
    time.sleep(2)
    InstagramModule.play_reels()
    time.sleep(5)
    InstagramModule.mute_unmute()
    time.sleep(5)
    InstagramModule.play_pause()
    time.sleep(5)
    InstagramModule.play_pause()
    time.sleep(5)
    InstagramModule.scroll_down()
    time.sleep(5)
    InstagramModule.scroll_up()