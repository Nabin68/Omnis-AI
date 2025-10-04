from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from dotenv import dotenv_values
import os
import platform
import shutil
import time
import logging
import atexit
from pathlib import Path
from typing import Optional
import subprocess

try:
    import mtranslate as mt
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    mt = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpeechRecognitionManager:
    """Robust Speech Recognition Manager with comprehensive error handling."""
    
    def __init__(self):
        """Initialize the Speech Recognition Manager."""
        self.driver = None
        self.temp_dir_path = None
        self.html_file_path = None
        self.input_language = "en-US"  # Default
        self.recognition_timeout = 30  # seconds
        self.max_retries = 3
        
        # Register cleanup function
        atexit.register(self.cleanup)
        
        # Load configuration
        self._load_configuration()
        
        # Setup paths
        self._setup_paths()
        
        # Create HTML file
        self._create_html_file()
    
    def _load_configuration(self):
        """Load configuration from environment variables safely."""
        try:
            env_vars = dotenv_values(".env")
            self.input_language = env_vars.get("InputLanguage", "en-US")
            
            # Validate language format
            if not self.input_language or len(self.input_language) < 2:
                logger.warning("Invalid InputLanguage in .env, using default 'en-US'")
                self.input_language = "en-US"
                
            logger.info(f"Speech recognition language set to: {self.input_language}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.input_language = "en-US"
    
    def _setup_paths(self):
        """Setup required directories and paths."""
        try:
            # Get the directory of the current script (backend folder)
            script_dir = Path(__file__).parent.resolve()
            
            # Get the main folder (parent of backend folder)
            main_dir = script_dir.parent
            
            # Data directory is at the same level as backend folder
            data_dir = main_dir / "data"
            data_dir.mkdir(exist_ok=True)
            
            # Create temp directory for status files
            self.temp_dir_path = main_dir / "Frontend" / "Files"
            self.temp_dir_path.mkdir(parents=True, exist_ok=True)
            
            # HTML file path in data folder
            self.html_file_path = data_dir / "Voice.html"
            
            logger.info(f"Main directory: {main_dir}")
            logger.info(f"Data directory: {data_dir}")
            logger.info(f"HTML file will be saved at: {self.html_file_path}")
            logger.info("Paths setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error setting up paths: {e}")
            raise
    
    def _create_html_file(self):
        """Create HTML file for speech recognition."""
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speech Recognition</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        button {{ padding: 10px 20px; margin: 10px; font-size: 16px; }}
        #output {{ 
            border: 1px solid #ccc; 
            padding: 10px; 
            min-height: 100px; 
            margin-top: 20px;
            background-color: #f9f9f9;
        }}
        .status {{ margin: 10px 0; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Speech Recognition Interface</h1>
    <div class="status" id="status">Ready</div>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="stop" onclick="stopRecognition()">Stop Recognition</button>
    <button id="clear" onclick="clearOutput()">Clear</button>
    
    <div id="output"></div>
    
    <script>
        const output = document.getElementById('output');
        const status = document.getElementById('status');
        const startButton = document.getElementById('start');
        const stopButton = document.getElementById('stop');
        
        let recognition;
        let isRecognitionActive = false;
        let recognitionTimeout;
        
        // Check for speech recognition support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.textContent = 'Speech recognition not supported';
            status.style.color = 'red';
            startButton.disabled = true;
        }}
        
        function updateStatus(message, color = 'black') {{
            status.textContent = message;
            status.style.color = color;
        }}
        
        function startRecognition() {{
            try {{
                if (isRecognitionActive) {{
                    updateStatus('Recognition already active', 'orange');
                    return;
                }}
                
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = '{self.input_language}';
                recognition.continuous = false;  // Changed to false for better control
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;
                
                recognition.onstart = function() {{
                    isRecognitionActive = true;
                    updateStatus('Listening...', 'green');
                    startButton.disabled = true;
                    stopButton.disabled = false;
                    
                    // Set timeout for recognition
                    recognitionTimeout = setTimeout(() => {{
                        if (isRecognitionActive) {{
                            recognition.stop();
                            updateStatus('Recognition timeout', 'orange');
                        }}
                    }}, 30000); // 30 second timeout
                }};
                
                recognition.onresult = function(event) {{
                    const transcript = event.results[0][0].transcript;
                    const confidence = event.results[0][0].confidence;
                    
                    output.textContent = transcript.trim();
                    updateStatus(`Recognition complete (confidence: ${{(confidence * 100).toFixed(1)}}%)`, 'blue');
                    
                    // Clear timeout
                    if (recognitionTimeout) {{
                        clearTimeout(recognitionTimeout);
                    }}
                }};
                
                recognition.onerror = function(event) {{
                    updateStatus(`Recognition error: ${{event.error}}`, 'red');
                    isRecognitionActive = false;
                    startButton.disabled = false;
                    stopButton.disabled = true;
                    
                    if (recognitionTimeout) {{
                        clearTimeout(recognitionTimeout);
                    }}
                }};
                
                recognition.onend = function() {{
                    isRecognitionActive = false;
                    startButton.disabled = false;
                    stopButton.disabled = true;
                    
                    if (recognitionTimeout) {{
                        clearTimeout(recognitionTimeout);
                    }}
                    
                    if (status.textContent === 'Listening...') {{
                        updateStatus('Recognition ended', 'gray');
                    }}
                }};
                
                recognition.start();
                
            }} catch (error) {{
                updateStatus(`Error starting recognition: ${{error.message}}`, 'red');
                isRecognitionActive = false;
                startButton.disabled = false;
                stopButton.disabled = true;
            }}
        }}
        
        function stopRecognition() {{
            if (recognition && isRecognitionActive) {{
                recognition.stop();
                updateStatus('Recognition stopped by user', 'gray');
            }}
            
            if (recognitionTimeout) {{
                clearTimeout(recognitionTimeout);
            }}
        }}
        
        function clearOutput() {{
            output.textContent = '';
            updateStatus('Output cleared', 'gray');
        }}
        
        // Initialize button states
        stopButton.disabled = true;
    </script>
</body>
</html>'''
        
        try:
            with open(self.html_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML file created at: {self.html_file_path}")
        except Exception as e:
            logger.error(f"Error creating HTML file: {e}")
            raise
    
    def _find_chrome_executable(self):
        """Find Chrome executable across different platforms."""
        system = platform.system()
        
        try:
            if system == "Windows":
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
                    r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe",
                ]
                
            elif system == "Darwin":  # macOS
                chrome_paths = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
                ]
                
            elif system == "Linux":
                # For Linux, check if executables are in PATH
                for cmd in ["google-chrome", "google-chrome-stable", "chromium-browser"]:
                    if shutil.which(cmd):
                        return cmd
                return None
            else:
                logger.error(f"Unsupported operating system: {system}")
                return None
            
            # Check each path
            for path in chrome_paths:
                path_obj = Path(path)
                if path_obj.exists():
                    logger.info(f"Found Chrome at: {path_obj}")
                    return str(path_obj)
            
            logger.warning("Chrome executable not found in standard locations")
            return None
            
        except Exception as e:
            logger.error(f"Error finding Chrome executable: {e}")
            return None
    
    def _find_chromedriver(self):
        """Find ChromeDriver executable."""
        try:
            # First check if chromedriver is in PATH
            chromedriver_path = shutil.which("chromedriver")
            if chromedriver_path:
                logger.info(f"Found ChromeDriver in PATH: {chromedriver_path}")
                return chromedriver_path
            
            # Check common locations
            system = platform.system()
            common_paths = []
            
            if system == "Windows":
                common_paths = [
                    r"D:\chromedriver\chromedriver.exe",  # Your current path
                    r"C:\chromedriver\chromedriver.exe",
                    Path.home() / "chromedriver" / "chromedriver.exe",
                    Path.cwd() / "chromedriver.exe"
                ]
            else:
                common_paths = [
                    "/usr/local/bin/chromedriver",
                    "/usr/bin/chromedriver",
                    Path.home() / "chromedriver",
                    Path.cwd() / "chromedriver"
                ]
            
            for path in common_paths:
                path_obj = Path(path)
                if path_obj.exists():
                    logger.info(f"Found ChromeDriver at: {path_obj}")
                    return str(path_obj)
            
            logger.error("ChromeDriver not found. Please install ChromeDriver and ensure it's in PATH or a standard location.")
            return None
            
        except Exception as e:
            logger.error(f"Error finding ChromeDriver: {e}")
            return None
    
    def _setup_webdriver(self, headless=False):
        """Setup Chrome WebDriver with comprehensive options."""
        try:
            chrome_executable = self._find_chrome_executable()
            chromedriver_path = self._find_chromedriver()
            
            if not chromedriver_path:
                raise Exception("ChromeDriver not found")
            
            # Configure Chrome options
            chrome_options = Options()
            
            if chrome_executable:
                chrome_options.binary_location = chrome_executable
            
            # Essential options for speech recognition
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-file-access-from-files")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # BACKGROUND MODE OPTIONS - Key changes here!
            # Start minimized so it doesn't steal focus
            chrome_options.add_argument("--window-position=-2400,-2400")  # Position off-screen
            chrome_options.add_argument("--window-size=1,1")  # Minimize window size
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # This ensures Chrome doesn't grab focus
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Performance options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            
            # Create service with suppressed output
            service = Service(
                executable_path=chromedriver_path,
                log_output=os.devnull  # Suppress ChromeDriver logs
            )
            
            # Create WebDriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            # Minimize the window after creation (platform-specific)
            try:
                self.driver.minimize_window()
            except Exception as e:
                logger.debug(f"Could not minimize window: {e}")
            
            logger.info("WebDriver setup completed successfully (background mode)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            return False
    
    def set_assistant_status(self, status: str):
        """Set assistant status safely."""
        try:
            status_file = self.temp_dir_path / "Status.data"
            with open(status_file, "w", encoding='utf-8') as file:
                file.write(status)
            logger.debug(f"Status set to: {status}")
        except Exception as e:
            logger.error(f"Error setting assistant status: {e}")
    
    def query_modifier(self, query: str) -> str:
        """Modify query with proper punctuation and capitalization."""
        try:
            if not query or not query.strip():
                return ""
            
            new_query = query.lower().strip()
            query_words = new_query.split()
            
            if not query_words:
                return ""
            
            question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can", "could", "would", "should", "is", "are", "do", "does", "did"]
            
            # Check if it's a question
            is_question = any(new_query.startswith(word + " ") for word in question_words)
            
            # Remove existing punctuation
            if query_words[-1][-1] in ['.', '?', '!']:
                new_query = new_query[:-1]
            
            # Add appropriate punctuation
            if is_question:
                new_query += "?"
            else:
                new_query += "."
            
            # Capitalize first letter
            result = new_query.capitalize()
            logger.debug(f"Query modified: '{query}' -> '{result}'")
            return result
            
        except Exception as e:
            logger.error(f"Error modifying query: {e}")
            return query.capitalize() + "."
    
    def universal_translator(self, text: str) -> str:
        """Translate text to English safely."""
        try:
            if not TRANSLATION_AVAILABLE:
                logger.warning("Translation module not available, returning original text")
                return text
            
            if not text or not text.strip():
                return text
            
            # Check if already in English
            if self.input_language.lower().startswith('en'):
                return text
            
            self.set_assistant_status("Translating...")
            english_translation = mt.translate(text, "en", "auto")
            
            if english_translation and english_translation.strip():
                logger.info(f"Translated: '{text}' -> '{english_translation}'")
                return english_translation
            else:
                logger.warning("Translation returned empty result, using original text")
                return text
                
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text
    
    def wait_for_speech_result(self, timeout: int = 30) -> Optional[str]:
        """Wait for speech recognition result with timeout."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            start_time = time.time()
            
            # Click start button
            start_button = wait.until(EC.element_to_be_clickable((By.ID, "start")))
            start_button.click()
            logger.info("Speech recognition started")
            
            # Wait for result or timeout
            while time.time() - start_time < timeout:
                try:
                    # Check for output
                    output_element = self.driver.find_element(By.ID, "output")
                    text = output_element.text.strip()
                    
                    if text:
                        logger.info(f"Speech recognition result: {text}")
                        
                        # Stop recognition
                        try:
                            stop_button = self.driver.find_element(By.ID, "stop")
                            stop_button.click()
                        except:
                            pass
                        
                        return text
                    
                    # Check for errors
                    status_element = self.driver.find_element(By.ID, "status")
                    status_text = status_element.text.lower()
                    
                    if "error" in status_text or "not supported" in status_text:
                        logger.error(f"Speech recognition error: {status_text}")
                        return None
                    
                    time.sleep(0.5)  # Short delay between checks
                    
                except NoSuchElementException:
                    time.sleep(0.5)
                    continue
            
            logger.warning("Speech recognition timed out")
            
            # Try to stop recognition
            try:
                stop_button = self.driver.find_element(By.ID, "stop")
                stop_button.click()
            except:
                pass
            
            return None
            
        except TimeoutException:
            logger.error("Timeout waiting for speech recognition interface")
            return None
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return None
    
    def speech_recognition(self, max_retries: int = 3) -> Optional[str]:
        """Perform speech recognition with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Speech recognition attempt {attempt + 1}/{max_retries}")
                
                # Setup WebDriver if not already done
                if not self.driver:
                    if not self._setup_webdriver():
                        logger.error("Failed to setup WebDriver")
                        continue
                
                # Navigate to HTML file
                file_url = f"file:///{self.html_file_path.as_posix()}"
                self.driver.get(file_url)
                logger.info(f"Loaded speech recognition page: {file_url}")
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "start"))
                )
                
                # Wait for speech input
                text = self.wait_for_speech_result(self.recognition_timeout)
                
                if text:
                    # Process the text
                    if self.input_language.lower().startswith('en'):
                        result = self.query_modifier(text)
                    else:
                        translated = self.universal_translator(text)
                        result = self.query_modifier(translated)
                    
                    logger.info(f"Final processed result: {result}")
                    return result
                else:
                    logger.warning(f"No speech detected in attempt {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"Error in speech recognition attempt {attempt + 1}: {e}")
                
                # Try to recover by recreating WebDriver
                try:
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                except:
                    pass
                
                if attempt < max_retries - 1:
                    logger.info("Retrying speech recognition...")
                    time.sleep(2)  # Brief delay before retry
        
        logger.error("All speech recognition attempts failed")
        return None
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.driver:
                logger.info("Cleaning up WebDriver...")
                self.driver.quit()
                self.driver = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

# Singleton instance for backward compatibility
_speech_manager = None

def get_speech_manager():
    """Get or create speech recognition manager."""
    global _speech_manager
    if _speech_manager is None:
        _speech_manager = SpeechRecognitionManager()
    return _speech_manager

def SpeechRecognition() -> Optional[str]:
    """Main speech recognition function for backward compatibility."""
    try:
        manager = get_speech_manager()
        return manager.speech_recognition()
    except Exception as e:
        logger.error(f"Error in SpeechRecognition function: {e}")
        return None

# Legacy functions for backward compatibility
def SetAssistantStatus(status: str):
    """Set assistant status (legacy function)."""
    try:
        manager = get_speech_manager()
        manager.set_assistant_status(status)
    except Exception as e:
        logger.error(f"Error setting assistant status: {e}")

def QueryModifier(query: str) -> str:
    """Modify query (legacy function)."""
    try:
        manager = get_speech_manager()
        return manager.query_modifier(query)
    except Exception as e:
        logger.error(f"Error in QueryModifier: {e}")
        return query

def UniversalTranslator(text: str) -> str:
    """Translate text (legacy function)."""
    try:
        manager = get_speech_manager()
        return manager.universal_translator(text)
    except Exception as e:
        logger.error(f"Error in UniversalTranslator: {e}")
        return text

# Test function
def test_speech_recognition():
    """Test speech recognition functionality."""
    logger.info("Starting speech recognition test...")
    
    with SpeechRecognitionManager() as manager:
        result = manager.speech_recognition()
        if result:
            logger.info(f"Test successful! Result: {result}")
        else:
            logger.error("Test failed - no speech detected")
    
    return result

if __name__ == "__main__":
    # Test the speech recognition
    test_result = test_speech_recognition()
    print(f"Test result: {test_result}")






