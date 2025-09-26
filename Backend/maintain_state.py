# maintain_state.py
import os
import time
import subprocess
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class MaintainState:
    """Centralized state management for all modules"""
    
    # Shared state variables
    _global_driver = None
    _connected_to_existing = False
    _profile_path = r"<your profile path here>"
    _debug_port = 9222
    
    @classmethod
    def get_global_driver(cls):
        """Get the shared Chrome driver instance"""
        return cls._global_driver
    
    @classmethod
    def set_global_driver(cls, driver):
        """Set the shared Chrome driver instance"""
        cls._global_driver = driver
    
    @classmethod
    def get_connected_to_existing(cls):
        """Check if connected to existing Chrome instance"""
        return cls._connected_to_existing
    
    @classmethod
    def set_connected_to_existing(cls, status):
        """Set the connection status"""
        cls._connected_to_existing = status
    
    @classmethod
    def get_profile_path(cls):
        """Get Chrome profile path"""
        return cls._profile_path
    
    @classmethod
    def get_debug_port(cls):
        """Get debug port"""
        return cls._debug_port
    
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
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  #replace it with your chrome path if not matched
        
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
            cls.set_connected_to_existing(True)
            cls.set_global_driver(driver)
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
            cls.set_connected_to_existing(False)
            cls.set_global_driver(driver)
            return driver
        except Exception as e:
            print(f"❌ Failed to create new Chrome instance: {e}")
            return None
    
    @classmethod
    def get_or_create_driver(cls):
        """Get existing driver or create new one if needed"""
        # If we already have a driver, return it
        if cls._global_driver:
            try:
                # Test if driver is still alive
                cls._global_driver.current_url
                print("✅ Using existing driver!")
                return cls._global_driver
            except:
                print("⚠️ Existing driver is dead, creating new one...")
                cls._global_driver = None
        
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
        
        print("✅ Chrome driver ready!")
        return driver
    
    @classmethod
    def cleanup_driver(cls):
        """Clean up the driver"""
        if cls._global_driver:
            try:
                cls._global_driver.quit()
            except:
                pass
            cls._global_driver = None
            cls._connected_to_existing = False
    
    @classmethod
    def get_driver_status(cls):
        """Get current driver status"""
        if cls._global_driver:
            try:
                cls._global_driver.current_url
                return "Active"
            except:
                return "Dead"
        return "None"
