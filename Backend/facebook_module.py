import os
import time
import pyautogui

from dotenv import dotenv_values

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from maintain_state import MaintainState
import threading
try:
    # Works in normal .py file
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    # Fallback for Jupyter / interactive
    BASE_DIR = os.path.abspath("..")

env_path = os.path.join(BASE_DIR, ".env")
env = dotenv_values(env_path)

class FacebookModule:
    scrolling = False
    
    speed_map = {
        1: (1, 0.01),
        2: (2, 0.008),
        3: (4, 0.005),
        4: (6, 0.003),
        5: (10, 0.001)
    }
    
    @staticmethod
    def open_facebook(driver):
        """Function to login into Facebook"""
        try:
            # Open new tab and navigate to Facebook
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            facebook_url = "https://www.facebook.com"
            driver.get(facebook_url)

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
                    driver.execute_script("arguments[0].click();", submit_button)  # safer than .click()
                    print("✅ Submit button clicked")
                except Exception:
                    print("❌ Submit button not found")
                    return False
                
                #little issue over here !! button not found
                try:
                    # Use XPath with [1] to pick the first matching element
                    save_info_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='OK']//span[text()='OK'][1]"))
                    )
                    save_info_button.click()
                    print("✅ Save info button clicked")
                except:
                    print("❌ No Save Info button found!")
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
            # Get or create driver using centralized state management
            driver = MaintainState.get_or_create_driver()
            
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
        driver = MaintainState.get_or_create_driver()
        try:
            videos_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//a[contains(@href,'/watch/')])[1]"))
            )
            driver.execute_script("arguments[0].click();", videos_button)  # safer click
            print("✅ Video clicked")
        except Exception:
            print("❌ Video button not found")
        
        # Fixed: Call the correct method name
        FacebookModule.mute_unmute_video()

        
    @staticmethod    
    def mute_unmute_video():
            driver = MaintainState.get_or_create_driver()
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
                    print("❌ Video Mute/Unmute button not found - trying keyboard shortcut")
                    # Fallback: Try 'M' key for mute
                    driver.find_element(By.TAG_NAME, 'body').send_keys('m')
                    print("✅ Video Muted/Unmuted (using M key)")
                    
            except Exception as e:
                print("❌ Video Mute/Unmute button not found:", e)
        
    @staticmethod
    def play_pause():
        driver = MaintainState.get_or_create_driver()
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
        print("Pressed Next Story")
        
    @staticmethod
    def prev_story():
        pyautogui.press("left")
        print("Pressed Previous story")
        
    
    @staticmethod
    def open_story():
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
            driver = MaintainState.get_or_create_driver()
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
                    print("❌ Story Mute/Unmute button not found - trying keyboard shortcut")
                    # Fallback: Try 'M' key for mute
                    driver.find_element(By.TAG_NAME, 'body').send_keys('m')
                    print("✅ Story Muted/Unmuted (using M key)")
                    
            except Exception as e:
                print("❌ Story Mute/Unmute button not found:", e)
        
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
    def to_home_page():
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
    driver = MaintainState.get_or_create_driver()
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
