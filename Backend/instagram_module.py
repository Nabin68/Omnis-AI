import os
import time
import threading
import pyautogui
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from maintain_state import MaintainState  


scroll_active = False
scroll_thread = None
    
try:
    # Works in normal .py file
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    # Fallback for Jupyter / interactive
    BASE_DIR = os.path.abspath("..")

env_path = os.path.join(BASE_DIR, ".env")
env = dotenv_values(env_path)

class InstagramModule:
    
    @staticmethod
    def open_instagram(driver, query):
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
                    driver.execute_script("arguments[0].click();", submit_button)  # safer than .click()
                    print("✅ Submit button clicked")
                    
                    # Wait for login to process
                    time.sleep(3)
                except Exception:
                    print("❌ Submit button not found")
                    return False
                
                # Handle save info popup (improved selector)
                try:
                    # Try multiple selectors for save info button
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
    def instagram(query):
        """Main entry to Instagram module"""
        try:
            # Get or create driver using centralized state management
            driver = MaintainState.get_or_create_driver()
            
            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False
            
            success = InstagramModule.open_instagram(driver, query)
            
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
        driver = MaintainState.get_or_create_driver()
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
                driver.execute_script("arguments[0].click();", reels_button)  # safer click
                print("✅ Reels button clicked")
                time.sleep(2)  # Wait for reels to load
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
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
        """Start scrolling Instagram feed upward"""
        global scroll_active, scroll_thread
        direction = "up"

        # Stop any existing scroll first
        if scroll_active:
            InstagramModule.stop_scroll_feed()
            time.sleep(0.3)

        try:
            scroll_active = True
            scroll_thread = threading.Thread(
                target=InstagramModule._scroll_worker,
                args=(direction, speed)
            )
            scroll_thread.daemon = True
            scroll_thread.start()
            print(f"✅ Feed scrolling {direction} at speed {speed}")
            return True
        except Exception as e:
            scroll_active = False
            print(f"❌ Failed to start scrolling: {e}")
            return False

    @staticmethod
    def scroll_feed_up(speed):
        """Start scrolling Instagram feed downward"""
        global scroll_active, scroll_thread
        direction = "down"

        if scroll_active:
            InstagramModule.stop_scroll_feed()
            time.sleep(0.3)

        try:
            scroll_active = True
            scroll_thread = threading.Thread(
                target=InstagramModule._scroll_worker,
                args=(direction, speed)
            )
            scroll_thread.daemon = True
            scroll_thread.start()
            print(f"✅ Feed scrolling {direction} at speed {speed}")
            return True
        except Exception as e:
            scroll_active = False
            print(f"❌ Failed to start scrolling: {e}")
            return False

    @staticmethod
    def stop_scroll_feed():
        """Stop any active feed scrolling"""
        global scroll_active, scroll_thread
        
        if scroll_active:
            scroll_active = False
            if scroll_thread and scroll_thread.is_alive():
                scroll_thread.join(timeout=1)
            print("🛑 Feed scrolling stopped")
            return True
        else:
            print("ℹ️ No active scrolling to stop")
            return False

    @staticmethod
    def _scroll_worker(direction, speed):
        """Internal function that handles smooth, human-like scrolling"""
        global scroll_active
        
        driver = MaintainState.get_or_create_driver()

        # Much smaller scroll increments for smoothness
        if direction == "up":
            scroll_amount = -20  # Small upward scroll
        else:
            scroll_amount = 20   # Small downward scroll

        # Speed settings - smaller delays for smoother scrolling
        speed_delays = {
            1: 0.08,   # Slowest - very smooth
            2: 0.06,   # Slow
            3: 0.04,   # Medium
            4: 0.03,   # Fast
            5: 0.02    # Fastest
        }
        delay = speed_delays.get(speed, 0.04)

        while scroll_active:
            try:
                # Use smooth scrolling with smaller increments
                scroll_script = f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});"
                driver.execute_script(scroll_script)
                time.sleep(delay)
            except Exception as e:
                print(f"❌ Scroll error: {e}")
                break
            
if __name__ == "__main__":  #For testing purposes, I wrote these code 
    result = InstagramModule.instagram("reels")
    time.sleep(5)
    InstagramModule.scroll_feed_up(1)
    time.sleep(3)
    InstagramModule.stop_scroll_feed()
    time.sleep(3)
    InstagramModule.scroll_feed_down(1)
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
    
