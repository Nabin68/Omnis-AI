#Mero Lagani is a Nepali platform that allows users to track and view the status of shares listed on NEPSE.

import time
import threading

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from maintain_state import MaintainState


class MerolaganiModule:
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
    
    @staticmethod
    def scroll_down(speed=1):
        """Scroll down the page at specified speed"""
        driver = MaintainState.get_or_create_driver()
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
        driver = MaintainState.get_or_create_driver()
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
        """Function to login into Merolagani"""
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
            print(f"❌ Error logging into Merolagani: {e}")
            return False
    
    
    @staticmethod
    def merolagani(query):
        """Main entry to Merolagani module"""
        try:
            # Get or create driver using centralized state management
            driver = MaintainState.get_or_create_driver()
            
            if not driver:
                print("❌ Failed to get Chrome driver!")
                return False
            
            success = MerolaganiModule.open_merolagani(query, driver)
            
            if success:
                print("🎉 Merolagani login successful!")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    


if __name__ == "__main__":
    driver = MaintainState.get_or_create_driver()
    MerolaganiModule.merolagani("HRL")
    MerolaganiModule.scroll_down(speed=2)  # start scrolling down
    time.sleep(3)          # scroll for 3 seconds
    MerolaganiModule.stop_scroll()           # stop scrolling
    time.sleep(1)
    MerolaganiModule.scroll_up(speed=3)      # start scrolling up
    time.sleep(2)
    MerolaganiModule.stop_scroll()           # stop scrolling

    # Close driver after scraping
    driver.quit()
