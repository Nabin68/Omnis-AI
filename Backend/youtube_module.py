# youtube_module.py
import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from maintain_state import MaintainState

class YoutubeModule:
    """YouTube automation module for playing songs"""
    
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
            # Get or create driver using centralized state management
            driver = MaintainState.get_or_create_driver()
            
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



