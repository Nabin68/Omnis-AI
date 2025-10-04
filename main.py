from Backend import (
    speech_to_text, 
    model,
    chatbot_module,
    text_to_speech,
    image_generation_module,
    realtime_module,
    google_search,
    content_writing_module,
    merolagani_module,
    core,
    youtube_module,
    instagram_module,
    facebook_module,
    system_automation
)
import threading
import queue
from time import sleep
from typing import List, Dict
import re
import pythoncom
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "OmnisAI")

# File paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)

# Initialize all modules
sound_manager = speech_to_text.SpeechRecognitionManager()
TTS = text_to_speech.TextToSpeech()
Chatbot_engine = chatbot_module.ChatBotEngine()
Imagegeneration_system = image_generation_module.ImageGenerationModule()
Realtime_Search_engine = realtime_module.RealtimeSearchModule()
google_search_engine = google_search.GoogleSearchModule()
content_writing_system = content_writing_module.ContentModule()
merolagani_server = merolagani_module.MerolaganiModule()
core_engine = core.Core()
youtube_engine = youtube_module.YoutubeModule()
instagram_engine = instagram_module.InstagramModule()
facebook_engine = facebook_module.FacebookModule()
system_automation_driver = system_automation.SystemAutomation()

# Task queue for concurrent execution
task_queue = queue.Queue()
response_queue = queue.Queue()
active_threads = []
run = True

# CRITICAL: Flags for mic control
is_speaking = threading.Event()
is_speaking.clear()

tasks_processing = threading.Event()
tasks_processing.clear()

# GUI Communication Functions
def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', 'w', encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(rf'{TempDirPath}\Mic.data', 'r', encoding='utf-8') as file:
            Status = file.read().strip()
        return Status
    except:
        return "False"

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
            Status = file.read()
        return Status
    except:
        return ""

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
        file.write(Text)

def GetQueryFromGUI():
    """Get query from text input in GUI"""
    try:
        with open(rf'{TempDirPath}\Query.data', 'r', encoding='utf-8') as file:
            query = file.read().strip()
        if query:
            # Clear the file after reading
            with open(rf'{TempDirPath}\Query.data', 'w', encoding='utf-8') as file:
                file.write('')
            return query
        return None
    except:
        return None

def AppendToChat(text):
    """Append new message to chat display"""
    try:
        with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
            current = file.read()
        
        if current:
            new_content = current + "\n" + text
        else:
            new_content = text
        
        with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
            file.write(new_content)
    except:
        ShowTextToScreen(text)

def InitializeFiles():
    """Initialize all required data files"""
    os.makedirs(TempDirPath, exist_ok=True)
    
    files_to_create = ['Mic.data', 'Status.data', 'Responses.data', 'Query.data']
    
    for filename in files_to_create:
        filepath = os.path.join(TempDirPath, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                if filename == 'Mic.data':
                    f.write('False')
                elif filename == 'Status.data':
                    f.write('Ready')
                else:
                    f.write('')

def clean_query(query: str) -> str:
    """Remove parentheses, extra spaces, and clean up query"""
    query = re.sub(r'[()]', '', query)
    query = ' '.join(query.split())
    return query.strip()

def should_speak(task_type: str) -> bool:
    """Determine if TTS should speak for this task type"""
    speak_types = ["general", "realtime"]
    return any(t in task_type.lower() for t in speak_types)

class TaskCategory:
    """Categories for different task types"""
    GENERAL = "general"
    REALTIME = "realtime"
    IMAGE_GEN = "generate image"
    AUTOMATION = "automation"
    OPEN = "open"
    CLOSE = "close"
    GOOGLE_SEARCH = "google search"
    YOUTUBE_SEARCH = "youtube search"
    CONTENT = "content"
    MEROLAGANI = "merolagani"
    EXIT = "exit"

def handle_general_query(query: str):
    """Handle general chatbot queries"""
    try:
        query = clean_query(query)
        response = Chatbot_engine.ask(query)
        print(f"[GENERAL] {response}")
        response_queue.put(("speak", response, "general"))
    except Exception as e:
        print(f"[ERROR] General query failed: {e}")

def handle_realtime_query(query: str):
    """Handle realtime search queries"""
    try:
        query = clean_query(query)
        response = Realtime_Search_engine.realtime_query(query, num_results=5)
        print(f"[REALTIME] {response}")
        response_queue.put(("speak", response, "realtime"))
    except Exception as e:
        print(f"[ERROR] Realtime query failed: {e}")

def handle_image_generation(query: str):
    """Handle image generation - non-blocking"""
    try:
        query = clean_query(query)
        print(f"[IMAGE] Generating image: {query}")
        Imagegeneration_system.generate(query)
        print(f"[IMAGE] ✅ Generation complete: {query}")
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")

def handle_google_search(query: str):
    """Handle Google search"""
    try:
        query = clean_query(query)
        google_search_engine.google_search(query)
        print(f"[GOOGLE] ✅ Searched: {query}")
    except Exception as e:
        print(f"[ERROR] Google search failed: {e}")

def handle_youtube_search(query: str):
    """Handle YouTube search"""
    try:
        query = clean_query(query)
        youtube_engine.youtube(query)
        print(f"[YOUTUBE] ✅ Playing: {query}")
    except Exception as e:
        print(f"[ERROR] YouTube search failed: {e}")

def handle_content_writing(query: str):
    """Handle content writing"""
    try:
        query = clean_query(query)
        content_writing_system.content(query)
        print(f"[CONTENT] ✅ Written: {query}")
    except Exception as e:
        print(f"[ERROR] Content writing failed: {e}")

def handle_merolagani(query: str):
    """Handle Merolagani queries"""
    try:
        query = clean_query(query)
        merolagani_server.merolagani(query)
        print(f"[MEROLAGANI] ✅ Status: {query}")
    except Exception as e:
        print(f"[ERROR] Merolagani failed: {e}")

def normalize_app_name(app_name: str) -> str:
    """Normalize app names to match dictionary keys"""
    app_name = clean_query(app_name).lower()
    
    app_mappings = {
        'vs code': 'vscode',
        'visual studio code': 'vscode',
        'code': 'vscode',
        'whats app': 'whatsapp',
        'what\'s app': 'whatsapp',
        'whatsapp desktop': 'whatsapp',
        'google chrome': 'chrome',
        'control panel': 'controlpanel',
        'my computer': 'mycomputer',
        'this pc': 'mycomputer',
        'file explorer': 'explorer',
        'command prompt': 'cmd',
        'power shell': 'powershell',
    }
    
    return app_mappings.get(app_name, app_name)

def handle_open_command(query: str):
    """Handle open commands"""
    try:
        query = clean_query(query)
        normalized_name = normalize_app_name(query)
        
        if "instagram" in query.lower():
            instagram_engine.instagram()
            print("[OPEN] ✅ Instagram")
        elif "facebook" in query.lower():
            facebook_engine.facebook()
            print("[OPEN] ✅ Facebook")
        elif "merolagani" in query.lower():
            merolagani_server.merolagani("TTL")
            print("[OPEN] ✅ Merolagani")
        elif "youtube" in query.lower():
            youtube_engine.youtube("Trending")
            print("[OPEN] ✅ YouTube")
        else:
            system_automation_driver.open_app(normalized_name)
            print(f"[OPEN] ✅ {normalized_name}")
    except Exception as e:
        print(f"[ERROR] Open command failed: {e}")

def handle_close_command(query: str):
    """Handle close commands"""
    try:
        query = clean_query(query)
        normalized_name = normalize_app_name(query)
        system_automation_driver.close_app(normalized_name)
        print(f"[CLOSE] ✅ {normalized_name}")
    except Exception as e:
        print(f"[ERROR] Close command failed: {e}")

def handle_automation(query: str):
    """Handle automation tasks based on foreground app"""
    try:
        pythoncom.CoInitialize()
        
        foreground_App = core_engine.get_foreground_app()
        query = clean_query(query).lower()
        
        print(f"[AUTOMATION] App: {foreground_App}, Command: {query}")
        
        if foreground_App == "Youtube":
            handle_youtube_automation(query)
        elif foreground_App == "MeroLagani":
            handle_merolagani_automation(query)
        elif foreground_App == "Instagram":
            handle_instagram_automation(query)
        elif foreground_App == "Facebook":
            handle_facebook_automation(query)
        else:
            handle_system_automation(query)
            
    except Exception as e:
        print(f"[ERROR] Automation failed: {e}")
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def handle_youtube_automation(query: str):
    """YouTube-specific automation"""
    if "next_video" in query or "next video" in query:
        youtube_engine.next_video()
        print("[YOUTUBE] ⏭️ Next video")
    elif "previous_video" in query or "prev video" in query:
        youtube_engine.previous_video()
        print("[YOUTUBE] ⏮️ Previous video")
    elif "play" in query:
        youtube_engine.play()
        print("[YOUTUBE] ▶️ Play")
    elif "fullscreen" in query:
        youtube_engine.fullscreen()
        print("[YOUTUBE] ⛶ Fullscreen")
    elif "mute" in query or "unmute" in query:
        youtube_engine.mute_unmute()
        print("[YOUTUBE] 🔇 Mute/Unmute")

def handle_merolagani_automation(query: str):
    """MeroLagani-specific automation"""
    if "scroll" in query:
        if "up" in query:
            merolagani_server.scroll_up()
            print("[MEROLAGANI] ⬆️ Scrolling up")
        elif "stop" in query:
            merolagani_server.stop_scroll()
            print("[MEROLAGANI] ⏸️ Scroll stopped")
        elif "down" in query:
            merolagani_server.scroll_down()
            print("[MEROLAGANI] ⬇️ Scrolling down")

def handle_instagram_automation(query: str):
    """Instagram-specific automation"""
    if "scroll_feed_down" in query or "scroll feed down" in query:
        instagram_engine.scroll_feed_down(1)
        print("[INSTAGRAM] ⬇️ Scroll feed down")
    elif "scroll_feed_up" in query or "scroll feed up" in query:
        instagram_engine.scroll_feed_up(1)
        print("[INSTAGRAM] ⬆️ Scroll feed up")
    elif "scroll_down" in query:
        instagram_engine.scroll_down()
        print("[INSTAGRAM] ⬇️ Scroll down")
    elif "scroll_up" in query:
        instagram_engine.scroll_up()
        print("[INSTAGRAM] ⬆️ Scroll up")
    elif "stop_scroll" in query or "stop scroll" in query:
        instagram_engine.stop_scroll_feed()
        print("[INSTAGRAM] ⏸️ Scroll stopped")
    elif "play_reels" in query or "play reels" in query:
        instagram_engine.play_reels()
        print("[INSTAGRAM] 🎬 Playing reels")
    elif "mute" in query or "unmute" in query:
        instagram_engine.mute_unmute()
        print("[INSTAGRAM] 🔇 Mute/Unmute")
    elif "pause" in query or "play" in query:
        instagram_engine.play_pause()
        print("[INSTAGRAM] ⏯️ Play/Pause")
    elif "next_story" in query or "next story" in query:
        instagram_engine.next_story()
        print("[INSTAGRAM] ⏭️ Next story")
    elif "prev_story" in query or "previous story" in query:
        instagram_engine.prev_story()
        print("[INSTAGRAM] ⏮️ Previous story")
    elif "open_story" in query or "open story" in query:
        instagram_engine.open_story()
        print("[INSTAGRAM] 📖 Story opened")
    elif "close_story" in query or "close story" in query:
        instagram_engine.close_story()
        print("[INSTAGRAM] ❌ Story closed")

def handle_facebook_automation(query: str):
    """Facebook-specific automation"""
    if "play_video" in query or "play video" in query:
        facebook_engine.play_videos()
        print("[FACEBOOK] ▶️ Playing video")
    elif "mute_video" in query or "unmute_video" in query:
        facebook_engine.mute_unmute_video()
        print("[FACEBOOK] 🔇 Mute/Unmute video")
    elif "pause_video" in query or "pause video" in query:
        facebook_engine.play_pause()
        print("[FACEBOOK] ⏸️ Pause")
    elif "show_stories" in query or "show stories" in query:
        facebook_engine.open_story()
        print("[FACEBOOK] 📖 Stories opened")
    elif "next_story" in query or "next story" in query:
        facebook_engine.next_story()
        print("[FACEBOOK] ⏭️ Next story")
    elif "prev_story" in query or "previous story" in query:
        facebook_engine.prev_story()
        print("[FACEBOOK] ⏮️ Previous story")
    elif "close_story" in query or "close story" in query:
        facebook_engine.close_story()
        print("[FACEBOOK] ❌ Story closed")
    elif "home_page" in query or "home page" in query:
        facebook_engine.to_home_page()
        print("[FACEBOOK] 🏠 Home page")
    elif "scroll_feed_up" in query or "scroll feed up" in query:
        facebook_engine.scroll_feed_up(1)
        print("[FACEBOOK] ⬆️ Scroll feed up")
    elif "scroll_feed_down" in query or "scroll feed down" in query:
        facebook_engine.scroll_feed_down(1)
        print("[FACEBOOK] ⬇️ Scroll feed down")
    elif "stop_scroll" in query or "stop scroll" in query:
        facebook_engine.stop_scroll_feed()
        print("[FACEBOOK] ⏸️ Scroll stopped")

def handle_system_automation(query: str):
    """System-level automation"""
    if "mute" in query and "unmute" not in query:
        system_automation_driver.mute_system()
        print("[SYSTEM] 🔇 Muted")
    elif "unmute" in query:
        system_automation_driver.unmute_system()
        print("[SYSTEM] 🔊 Unmuted")
    elif "switch_apps" in query or "switch app" in query or "switch to" in query:
        app_name = query.replace("switch_apps", "").replace("switch app", "").replace("switch to", "").strip()
        app_name = clean_query(app_name)
        
        if not system_automation_driver.switch_apps(app_name):
            normalized = normalize_app_name(app_name)
            system_automation_driver.switch_apps(normalized)
        print(f"[SYSTEM] ↔️ Switched to: {app_name}")
    elif "switch_chrome_tab" in query or "switch tab" in query:
        tab_name = query.replace("switch_chrome_tab", "").replace("switch tab", "").strip()
        system_automation_driver.switch_chrome_tab(tab_name)
        print(f"[SYSTEM] 🗂️ Tab: {tab_name}")
    elif "show desktop" in query or "minimize_everything" in query or "minimize everything" in query:
        system_automation_driver.show_desktop()
        print("[SYSTEM] 🖥️ Desktop shown")
    elif "minimize_active_window" in query or "minimize window" in query:
        system_automation_driver.minimize_active_window()
        print("[SYSTEM] ⬇️ Window minimized")
    elif "screenshot" in query or "take screenshot" in query:
        system_automation_driver.take_screenshot()
        print("[SYSTEM] 📸 Screenshot taken")
    elif "set_volume" in query or "set volume" in query:
        volume = ''.join(filter(str.isdigit, query))
        if volume:
            system_automation_driver.set_volume(int(volume))
            print(f"[SYSTEM] 🔊 Volume: {volume}%")
    elif "change_volume_by" in query or "volume up" in query or "volume down" in query:
        if "up" in query:
            system_automation_driver.change_volume_by(10)
            print("[SYSTEM] 🔊 Volume +10%")
        elif "down" in query:
            system_automation_driver.change_volume_by(-10)
            print("[SYSTEM] 🔉 Volume -10%")
    elif "set_brightness" in query or "set brightness" in query:
        brightness = ''.join(filter(str.isdigit, query))
        if brightness:
            system_automation_driver.set_brightness(int(brightness))
            print(f"[SYSTEM] ☀️ Brightness: {brightness}%")
    elif "change_brightness_by" in query or "brightness up" in query or "brightness down" in query:
        if "up" in query:
            system_automation_driver.change_brightness_by(10)
            print("[SYSTEM] ☀️ Brightness +10%")
        elif "down" in query:
            system_automation_driver.change_brightness_by(-10)
            print("[SYSTEM] 🌙 Brightness -10%")

def task_executor(task: str):
    """Execute individual tasks in separate threads"""
    try:
        task_lower = task.lower()
        
        if "general" in task_lower:
            query = task.replace("general", "", 1).strip()
            handle_general_query(query)
            
        elif "generate image" in task_lower:
            query = task.replace("generate image", "", 1).strip()
            handle_image_generation(query)
            
        elif "realtime" in task_lower:
            query = task.replace("realtime", "", 1).strip()
            handle_realtime_query(query)
            
        elif "google search" in task_lower:
            query = task.replace("google search", "", 1).strip()
            handle_google_search(query)
            
        elif "youtube search" in task_lower:
            query = task.replace("youtube search", "", 1).strip()
            handle_youtube_search(query)
            
        elif "content" in task_lower:
            query = task.replace("content", "", 1).strip()
            handle_content_writing(query)
            
        elif "merolagani" in task_lower:
            query = task.replace("merolagani", "", 1).strip()
            handle_merolagani(query)
            
        elif "close" in task_lower:
            query = task.replace("close", "", 1).strip()
            handle_close_command(query)
            
        elif "open" in task_lower:
            query = task.replace("open", "", 1).strip()
            handle_open_command(query)
            
        elif "automation" in task_lower:
            query = task.replace("automation", "", 1).strip()
            handle_automation(query)
            
        elif "exit" in task_lower:
            global run
            run = False
            response_queue.put(("speak", "Goodbye!", "exit"))
            
        else:
            print(f"[UNHANDLED] {task}")
            
    except Exception as e:
        print(f"[ERROR] Task execution failed: {e}")

def task_worker():
    """Worker thread that processes tasks from queue"""
    while run:
        try:
            if not task_queue.empty():
                task = task_queue.get()
                print(f"[WORKER] Processing: {task}")
                task_executor(task)
                task_queue.task_done()
            else:
                sleep(0.05)
        except Exception as e:
            print(f"[ERROR] Worker thread error: {e}")
            sleep(0.5)

def response_handler():
    """Handle responses and TTS only for general/realtime queries"""
    while run:
        try:
            if not response_queue.empty():
                item = response_queue.get()
                
                if len(item) == 3:
                    action, message, task_type = item
                else:
                    action, message = item
                    task_type = ""
                
                if action == "speak":
                    # Display on GUI first
                    AppendToChat(f"OmnisAI: {message}")
                    
                    if should_speak(task_type):
                        is_speaking.set()
                        SetAssistantStatus("Speaking...")
                        print("[MIC] 🔇 Microphone MUTED (Speaking...)")
                        
                        TTS.Speak(message)
                        
                        sleep(0.3)
                        
                        is_speaking.clear()
                        SetAssistantStatus("Ready")
                        print("[MIC] 🎤 Microphone ACTIVE (Listening...)")
                    else:
                        print(f"[NO SPEECH] Task type '{task_type}' - Silent mode")
                    
                response_queue.task_done()
            else:
                sleep(0.05)
        except Exception as e:
            print(f"[ERROR] Response handler error: {e}")
            is_speaking.clear()
            sleep(0.5)

def process_user_input(text: str):
    """Process user input and queue tasks concurrently"""
    try:
        print(f"\n{'='*60}")
        print(f"[USER] {text}")
        print(f"{'='*60}")
        
        # Display user message in GUI
        AppendToChat(f"{Username}: {text}")
        
        # Set flag that tasks are being processed
        tasks_processing.set()
        SetAssistantStatus("Thinking...")
        
        list_of_tasks = model.ModelModule().FirstLayerDMM(text)
        print(f"[TASKS] {list_of_tasks}\n")
        
        for task in list_of_tasks:
            task_queue.put(task)
            
        num_workers = min(len(list_of_tasks), 5)
        worker_threads = []
        for _ in range(num_workers):
            worker = threading.Thread(target=task_worker, daemon=True)
            worker.start()
            worker_threads.append(worker)
            active_threads.append(worker)
        
        # Wait for all tasks to complete in background thread
        def wait_for_completion():
            task_queue.join()
            response_queue.join()
            tasks_processing.clear()
            SetAssistantStatus("Ready")
            print("[TASKS] ✅ All tasks completed\n")
        
        completion_thread = threading.Thread(target=wait_for_completion, daemon=True)
        completion_thread.start()
            
    except Exception as e:
        print(f"[ERROR] Input processing failed: {e}")
        tasks_processing.clear()
        SetAssistantStatus("Error occurred")

def main():
    """Main execution loop"""
    print("\n" + "="*60)
    print("🤖 OMNISAI VOICE ASSISTANT STARTED")
    print("="*60)
    print("📌 Ready to listen...")
    print("💬 Say 'exit' to quit\n")
    
    # Initialize files
    InitializeFiles()
    
    # Start response handler thread
    response_thread = threading.Thread(target=response_handler, daemon=True)
    response_thread.start()
    
    while run:
        try:
            # Check for text input from GUI
            gui_query = GetQueryFromGUI()
            if gui_query:
                print(f"[GUI INPUT] {gui_query}")
                process_user_input(gui_query)
                sleep(0.1)
                continue
            
            # CRITICAL: Only listen if NOT speaking AND no tasks are processing
            if is_speaking.is_set() or tasks_processing.is_set():
                sleep(0.1)
                continue
            
            # Check microphone status from GUI
            mic_status = GetMicrophoneStatus()
            if mic_status.lower() != "true":
                sleep(0.1)
                continue
            
            # Listen for voice input
            SetAssistantStatus("Listening...")
            text = sound_manager.speech_recognition()
            
            if not text:
                sleep(0.05)
                continue
            
            if "exit" in text.lower():
                print("\n[SYSTEM] 👋 Shutting down...")
                is_speaking.set()
                AppendToChat(f"{Username}: {text}")
                AppendToChat("OmnisAI: Goodbye!")
                TTS.Speak("Goodbye!")
                sleep(0.5)
                break
            
            process_user_input(text)
            
            sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n[SYSTEM] 🛑 Interrupted by user")
            break
        except Exception as e:
            print(f"[ERROR] Main loop: {e}")
            SetAssistantStatus("Error occurred")
            sleep(1)
    
    print("\n" + "="*60)
    print("✅ OMNISAI VOICE ASSISTANT STOPPED")
    print("="*60)

if __name__ == "__main__":
    try:
        # Import GUI in separate thread
        from Frontend.GUI import GraphicalUserInterface
        
        # Start GUI in separate thread
        gui_thread = threading.Thread(target=GraphicalUserInterface, daemon=False)
        gui_thread.start()
        
        # Small delay to let GUI initialize
        sleep(1)
        
        # Start main loop
        main()
        
    except Exception as e:
        print(f"[FATAL] {e}")
    finally:
        run = False
        is_speaking.clear()
        tasks_processing.clear()
        print("[CLEANUP] Complete")

























# from Backend import (
#     speech_to_text, 
#     model,
#     chatbot_module,
#     text_to_speech,
#     image_generation_module,
#     realtime_module,
#     google_search,
#     content_writing_module,
#     merolagani_module,
#     core,
#     youtube_module,
#     instagram_module,
#     facebook_module,
#     system_automation
# )
# import threading
# import queue
# from time import sleep
# from typing import List, Dict
# import re
# import pythoncom  # For COM threading fix

# # Initialize all modules
# sound_manager = speech_to_text.SpeechRecognitionManager()
# TTS = text_to_speech.TextToSpeech()
# Chatbot_engine = chatbot_module.ChatBotEngine()
# Imagegeneration_system = image_generation_module.ImageGenerationModule()
# Realtime_Search_engine = realtime_module.RealtimeSearchModule()
# google_search_engine = google_search.GoogleSearchModule()
# content_writing_system = content_writing_module.ContentModule()
# merolagani_server = merolagani_module.MerolaganiModule()
# core_engine = core.Core()
# youtube_engine = youtube_module.YoutubeModule()
# instagram_engine = instagram_module.InstagramModule()
# facebook_engine = facebook_module.FacebookModule()
# system_automation_driver = system_automation.SystemAutomation()

# # Task queue for concurrent execution
# task_queue = queue.Queue()
# response_queue = queue.Queue()
# active_threads = []
# run = True

# # CRITICAL: Flags for mic control
# is_speaking = threading.Event()
# is_speaking.clear()  # Initially not speaking

# tasks_processing = threading.Event()
# tasks_processing.clear()  # Initially no tasks processing


# def clean_query(query: str) -> str:
#     """Remove parentheses, extra spaces, and clean up query"""
#     query = re.sub(r'[()]', '', query)
#     query = ' '.join(query.split())
#     return query.strip()


# def should_speak(task_type: str) -> bool:
#     """Determine if TTS should speak for this task type"""
#     speak_types = ["general", "realtime"]
#     return any(t in task_type.lower() for t in speak_types)


# class TaskCategory:
#     """Categories for different task types"""
#     GENERAL = "general"
#     REALTIME = "realtime"
#     IMAGE_GEN = "generate image"
#     AUTOMATION = "automation"
#     OPEN = "open"
#     CLOSE = "close"
#     GOOGLE_SEARCH = "google search"
#     YOUTUBE_SEARCH = "youtube search"
#     CONTENT = "content"
#     MEROLAGANI = "merolagani"
#     EXIT = "exit"


# def handle_general_query(query: str):
#     """Handle general chatbot queries"""
#     try:
#         query = clean_query(query)
#         response = Chatbot_engine.ask(query)
#         print(f"[GENERAL] {response}")
#         response_queue.put(("speak", response, "general"))
#     except Exception as e:
#         print(f"[ERROR] General query failed: {e}")


# def handle_realtime_query(query: str):
#     """Handle realtime search queries"""
#     try:
#         query = clean_query(query)
#         response = Realtime_Search_engine.realtime_query(query, num_results=5)
#         print(f"[REALTIME] {response}")
#         response_queue.put(("speak", response, "realtime"))
#     except Exception as e:
#         print(f"[ERROR] Realtime query failed: {e}")


# def handle_image_generation(query: str):
#     """Handle image generation - non-blocking"""
#     try:
#         query = clean_query(query)
#         print(f"[IMAGE] Generating image: {query}")
#         Imagegeneration_system.generate(query)
#         print(f"[IMAGE] ✅ Generation complete: {query}")
#     except Exception as e:
#         print(f"[ERROR] Image generation failed: {e}")


# def handle_google_search(query: str):
#     """Handle Google search"""
#     try:
#         query = clean_query(query)
#         google_search_engine.google_search(query)
#         print(f"[GOOGLE] ✅ Searched: {query}")
#     except Exception as e:
#         print(f"[ERROR] Google search failed: {e}")


# def handle_youtube_search(query: str):
#     """Handle YouTube search"""
#     try:
#         query = clean_query(query)
#         youtube_engine.youtube(query)
#         print(f"[YOUTUBE] ✅ Playing: {query}")
#     except Exception as e:
#         print(f"[ERROR] YouTube search failed: {e}")


# def handle_content_writing(query: str):
#     """Handle content writing"""
#     try:
#         query = clean_query(query)
#         content_writing_system.content(query)
#         print(f"[CONTENT] ✅ Written: {query}")
#     except Exception as e:
#         print(f"[ERROR] Content writing failed: {e}")


# def handle_merolagani(query: str):
#     """Handle Merolagani queries"""
#     try:
#         query = clean_query(query)
#         merolagani_server.merolagani(query)
#         print(f"[MEROLAGANI] ✅ Status: {query}")
#     except Exception as e:
#         print(f"[ERROR] Merolagani failed: {e}")


# def normalize_app_name(app_name: str) -> str:
#     """Normalize app names to match dictionary keys"""
#     app_name = clean_query(app_name).lower()
    
#     app_mappings = {
#         'vs code': 'vscode',
#         'visual studio code': 'vscode',
#         'code': 'vscode',
#         'whats app': 'whatsapp',
#         'what\'s app': 'whatsapp',
#         'whatsapp desktop': 'whatsapp',
#         'google chrome': 'chrome',
#         'control panel': 'controlpanel',
#         'my computer': 'mycomputer',
#         'this pc': 'mycomputer',
#         'file explorer': 'explorer',
#         'command prompt': 'cmd',
#         'power shell': 'powershell',
#     }
    
#     return app_mappings.get(app_name, app_name)


# def handle_open_command(query: str):
#     """Handle open commands"""
#     try:
#         query = clean_query(query)
#         normalized_name = normalize_app_name(query)
        
#         if "instagram" in query.lower():
#             instagram_engine.instagram()
#             print("[OPEN] ✅ Instagram")
#         elif "facebook" in query.lower():
#             facebook_engine.facebook()
#             print("[OPEN] ✅ Facebook")
#         elif "merolagani" in query.lower():
#             merolagani_server.merolagani("TTL")
#             print("[OPEN] ✅ Merolagani")
#         elif "youtube" in query.lower():
#             youtube_engine.youtube("Trending")
#             print("[OPEN] ✅ YouTube")
#         else:
#             system_automation_driver.open_app(normalized_name)
#             print(f"[OPEN] ✅ {normalized_name}")
#     except Exception as e:
#         print(f"[ERROR] Open command failed: {e}")


# def handle_close_command(query: str):
#     """Handle close commands"""
#     try:
#         query = clean_query(query)
#         normalized_name = normalize_app_name(query)
#         system_automation_driver.close_app(normalized_name)
#         print(f"[CLOSE] ✅ {normalized_name}")
#     except Exception as e:
#         print(f"[ERROR] Close command failed: {e}")


# def handle_automation(query: str):
#     """Handle automation tasks based on foreground app"""
#     try:
#         # Initialize COM for this thread
#         pythoncom.CoInitialize()
        
#         foreground_App = core_engine.get_foreground_app()
#         query = clean_query(query).lower()
        
#         print(f"[AUTOMATION] App: {foreground_App}, Command: {query}")
        
#         if foreground_App == "Youtube":
#             handle_youtube_automation(query)
#         elif foreground_App == "MeroLagani":
#             handle_merolagani_automation(query)
#         elif foreground_App == "Instagram":
#             handle_instagram_automation(query)
#         elif foreground_App == "Facebook":
#             handle_facebook_automation(query)
#         else:
#             handle_system_automation(query)
            
#     except Exception as e:
#         print(f"[ERROR] Automation failed: {e}")
#     finally:
#         # Uninitialize COM
#         try:
#             pythoncom.CoUninitialize()
#         except:
#             pass


# def handle_youtube_automation(query: str):
#     """YouTube-specific automation"""
#     if "next_video" in query or "next video" in query:
#         youtube_engine.next_video()
#         print("[YOUTUBE] ⏭️ Next video")
#     elif "previous_video" in query or "prev video" in query:
#         youtube_engine.previous_video()
#         print("[YOUTUBE] ⏮️ Previous video")
#     elif "play" in query:
#         youtube_engine.play()
#         print("[YOUTUBE] ▶️ Play")
#     elif "fullscreen" in query:
#         youtube_engine.fullscreen()
#         print("[YOUTUBE] ⛶ Fullscreen")
#     elif "mute" in query or "unmute" in query:
#         youtube_engine.mute_unmute()
#         print("[YOUTUBE] 🔇 Mute/Unmute")


# def handle_merolagani_automation(query: str):
#     """MeroLagani-specific automation"""
#     if "scroll" in query:
#         if "up" in query:
#             merolagani_server.scroll_up()
#             print("[MEROLAGANI] ⬆️ Scrolling up")
#         elif "stop" in query:
#             merolagani_server.stop_scroll()
#             print("[MEROLAGANI] ⏸️ Scroll stopped")
#         elif "down" in query:
#             merolagani_server.scroll_down()
#             print("[MEROLAGANI] ⬇️ Scrolling down")


# def handle_instagram_automation(query: str):
#     """Instagram-specific automation"""
#     if "scroll_feed_down" in query or "scroll feed down" in query:
#         instagram_engine.scroll_feed_down(1)
#         print("[INSTAGRAM] ⬇️ Scroll feed down")
#     elif "scroll_feed_up" in query or "scroll feed up" in query:
#         instagram_engine.scroll_feed_up(1)
#         print("[INSTAGRAM] ⬆️ Scroll feed up")
#     elif "scroll_down" in query:
#         instagram_engine.scroll_down()
#         print("[INSTAGRAM] ⬇️ Scroll down")
#     elif "scroll_up" in query:
#         instagram_engine.scroll_up()
#         print("[INSTAGRAM] ⬆️ Scroll up")
#     elif "stop_scroll" in query or "stop scroll" in query:
#         instagram_engine.stop_scroll_feed()
#         print("[INSTAGRAM] ⏸️ Scroll stopped")
#     elif "play_reels" in query or "play reels" in query:
#         instagram_engine.play_reels()
#         print("[INSTAGRAM] 🎬 Playing reels")
#     elif "mute" in query or "unmute" in query:
#         instagram_engine.mute_unmute()
#         print("[INSTAGRAM] 🔇 Mute/Unmute")
#     elif "pause" in query or "play" in query:
#         instagram_engine.play_pause()
#         print("[INSTAGRAM] ⏯️ Play/Pause")
#     elif "next_story" in query or "next story" in query:
#         instagram_engine.next_story()
#         print("[INSTAGRAM] ⏭️ Next story")
#     elif "prev_story" in query or "previous story" in query:
#         instagram_engine.prev_story()
#         print("[INSTAGRAM] ⏮️ Previous story")
#     elif "open_story" in query or "open story" in query:
#         instagram_engine.open_story()
#         print("[INSTAGRAM] 📖 Story opened")
#     elif "close_story" in query or "close story" in query:
#         instagram_engine.close_story()
#         print("[INSTAGRAM] ❌ Story closed")


# def handle_facebook_automation(query: str):
#     """Facebook-specific automation"""
#     if "play_video" in query or "play video" in query:
#         facebook_engine.play_videos()
#         print("[FACEBOOK] ▶️ Playing video")
#     elif "mute_video" in query or "unmute_video" in query:
#         facebook_engine.mute_unmute_video()
#         print("[FACEBOOK] 🔇 Mute/Unmute video")
#     elif "pause_video" in query or "pause video" in query:
#         facebook_engine.play_pause()
#         print("[FACEBOOK] ⏸️ Pause")
#     elif "show_stories" in query or "show stories" in query:
#         facebook_engine.open_story()
#         print("[FACEBOOK] 📖 Stories opened")
#     elif "next_story" in query or "next story" in query:
#         facebook_engine.next_story()
#         print("[FACEBOOK] ⏭️ Next story")
#     elif "prev_story" in query or "previous story" in query:
#         facebook_engine.prev_story()
#         print("[FACEBOOK] ⏮️ Previous story")
#     elif "close_story" in query or "close story" in query:
#         facebook_engine.close_story()
#         print("[FACEBOOK] ❌ Story closed")
#     elif "home_page" in query or "home page" in query:
#         facebook_engine.to_home_page()
#         print("[FACEBOOK] 🏠 Home page")
#     elif "scroll_feed_up" in query or "scroll feed up" in query:
#         facebook_engine.scroll_feed_up(1)
#         print("[FACEBOOK] ⬆️ Scroll feed up")
#     elif "scroll_feed_down" in query or "scroll feed down" in query:
#         facebook_engine.scroll_feed_down(1)
#         print("[FACEBOOK] ⬇️ Scroll feed down")
#     elif "stop_scroll" in query or "stop scroll" in query:
#         facebook_engine.stop_scroll_feed()
#         print("[FACEBOOK] ⏸️ Scroll stopped")


# def handle_system_automation(query: str):
#     """System-level automation"""
#     if "mute" in query and "unmute" not in query:
#         system_automation_driver.mute_system()
#         print("[SYSTEM] 🔇 Muted")
#     elif "unmute" in query:
#         system_automation_driver.unmute_system()
#         print("[SYSTEM] 🔊 Unmuted")
#     elif "switch_apps" in query or "switch app" in query or "switch to" in query:
#         app_name = query.replace("switch_apps", "").replace("switch app", "").replace("switch to", "").strip()
#         app_name = clean_query(app_name)
        
#         if not system_automation_driver.switch_apps(app_name):
#             normalized = normalize_app_name(app_name)
#             system_automation_driver.switch_apps(normalized)
#         print(f"[SYSTEM] ↔️ Switched to: {app_name}")
#     elif "switch_chrome_tab" in query or "switch tab" in query:
#         tab_name = query.replace("switch_chrome_tab", "").replace("switch tab", "").strip()
#         system_automation_driver.switch_chrome_tab(tab_name)
#         print(f"[SYSTEM] 🗂️ Tab: {tab_name}")
#     elif "show desktop" in query or "minimize_everything" in query or "minimize everything" in query:
#         system_automation_driver.show_desktop()
#         print("[SYSTEM] 🖥️ Desktop shown")
#     elif "minimize_active_window" in query or "minimize window" in query:
#         system_automation_driver.minimize_active_window()
#         print("[SYSTEM] ⬇️ Window minimized")
#     elif "screenshot" in query or "take screenshot" in query:
#         system_automation_driver.take_screenshot()
#         print("[SYSTEM] 📸 Screenshot taken")
#     elif "set_volume" in query or "set volume" in query:
#         volume = ''.join(filter(str.isdigit, query))
#         if volume:
#             system_automation_driver.set_volume(int(volume))
#             print(f"[SYSTEM] 🔊 Volume: {volume}%")
#     elif "change_volume_by" in query or "volume up" in query or "volume down" in query:
#         if "up" in query:
#             system_automation_driver.change_volume_by(10)
#             print("[SYSTEM] 🔊 Volume +10%")
#         elif "down" in query:
#             system_automation_driver.change_volume_by(-10)
#             print("[SYSTEM] 🔉 Volume -10%")
#     elif "set_brightness" in query or "set brightness" in query:
#         brightness = ''.join(filter(str.isdigit, query))
#         if brightness:
#             system_automation_driver.set_brightness(int(brightness))
#             print(f"[SYSTEM] ☀️ Brightness: {brightness}%")
#     elif "change_brightness_by" in query or "brightness up" in query or "brightness down" in query:
#         if "up" in query:
#             system_automation_driver.change_brightness_by(10)
#             print("[SYSTEM] ☀️ Brightness +10%")
#         elif "down" in query:
#             system_automation_driver.change_brightness_by(-10)
#             print("[SYSTEM] 🌙 Brightness -10%")


# def task_executor(task: str):
#     """Execute individual tasks in separate threads"""
#     try:
#         task_lower = task.lower()
        
#         if "general" in task_lower:
#             query = task.replace("general", "", 1).strip()
#             handle_general_query(query)
            
#         elif "generate image" in task_lower:
#             query = task.replace("generate image", "", 1).strip()
#             handle_image_generation(query)
            
#         elif "realtime" in task_lower:
#             query = task.replace("realtime", "", 1).strip()
#             handle_realtime_query(query)
            
#         elif "google search" in task_lower:
#             query = task.replace("google search", "", 1).strip()
#             handle_google_search(query)
            
#         elif "youtube search" in task_lower:
#             query = task.replace("youtube search", "", 1).strip()
#             handle_youtube_search(query)
            
#         elif "content" in task_lower:
#             query = task.replace("content", "", 1).strip()
#             handle_content_writing(query)
            
#         elif "merolagani" in task_lower:
#             query = task.replace("merolagani", "", 1).strip()
#             handle_merolagani(query)
            
#         elif "close" in task_lower:
#             query = task.replace("close", "", 1).strip()
#             handle_close_command(query)
            
#         elif "open" in task_lower:
#             query = task.replace("open", "", 1).strip()
#             handle_open_command(query)
            
#         elif "automation" in task_lower:
#             query = task.replace("automation", "", 1).strip()
#             handle_automation(query)
            
#         elif "exit" in task_lower:
#             global run
#             run = False
#             response_queue.put(("speak", "Goodbye!", "exit"))
            
#         else:
#             print(f"[UNHANDLED] {task}")
            
#     except Exception as e:
#         print(f"[ERROR] Task execution failed: {e}")


# def task_worker():
#     """Worker thread that processes tasks from queue"""
#     while run:
#         try:
#             if not task_queue.empty():
#                 task = task_queue.get()
#                 print(f"[WORKER] Processing: {task}")
#                 task_executor(task)
#                 task_queue.task_done()
#             else:
#                 sleep(0.05)
#         except Exception as e:
#             print(f"[ERROR] Worker thread error: {e}")
#             sleep(0.5)


# def response_handler():
#     """Handle responses and TTS only for general/realtime queries"""
#     while run:
#         try:
#             if not response_queue.empty():
#                 item = response_queue.get()
                
#                 if len(item) == 3:
#                     action, message, task_type = item
#                 else:
#                     action, message = item
#                     task_type = ""
                
#                 if action == "speak":
#                     if should_speak(task_type):
#                         is_speaking.set()
#                         print("[MIC] 🔇 Microphone MUTED (Speaking...)")
                        
#                         TTS.Speak(message)
                        
#                         sleep(0.3)
                        
#                         is_speaking.clear()
#                         print("[MIC] 🎤 Microphone ACTIVE (Listening...)")
#                     else:
#                         print(f"[NO SPEECH] Task type '{task_type}' - Silent mode")
                    
#                 response_queue.task_done()
#             else:
#                 sleep(0.05)
#         except Exception as e:
#             print(f"[ERROR] Response handler error: {e}")
#             is_speaking.clear()
#             sleep(0.5)


# def process_user_input(text: str):
#     """Process user input and queue tasks concurrently"""
#     try:
#         print(f"\n{'='*60}")
#         print(f"[USER] {text}")
#         print(f"{'='*60}")
        
#         # Set flag that tasks are being processed
#         tasks_processing.set()
        
#         list_of_tasks = model.ModelModule().FirstLayerDMM(text)
#         print(f"[TASKS] {list_of_tasks}\n")
        
#         for task in list_of_tasks:
#             task_queue.put(task)
            
#         num_workers = min(len(list_of_tasks), 5)
#         worker_threads = []
#         for _ in range(num_workers):
#             worker = threading.Thread(target=task_worker, daemon=True)
#             worker.start()
#             worker_threads.append(worker)
#             active_threads.append(worker)
        
#         # Wait for all tasks to complete in background thread
#         def wait_for_completion():
#             task_queue.join()  # Wait for all tasks to finish
#             response_queue.join()  # Wait for all responses to finish
#             tasks_processing.clear()  # Clear the flag
#             print("[TASKS] ✅ All tasks completed\n")
        
#         completion_thread = threading.Thread(target=wait_for_completion, daemon=True)
#         completion_thread.start()
            
#     except Exception as e:
#         print(f"[ERROR] Input processing failed: {e}")
#         tasks_processing.clear()


# def main():
#     """Main execution loop"""
#     print("\n" + "="*60)
#     print("🎙️  VOICE ASSISTANT STARTED")
#     print("="*60)
#     print("📌 Ready to listen...")
#     print("💬 Say 'exit' to quit\n")
    
#     response_thread = threading.Thread(target=response_handler, daemon=True)
#     response_thread.start()
    
#     while run:
#         try:
#             # CRITICAL: Only listen if NOT speaking AND no tasks are processing
#             if is_speaking.is_set() or tasks_processing.is_set():
#                 sleep(0.1)
#                 continue
            
#             text = sound_manager.speech_recognition()
            
#             if not text:
#                 sleep(0.05)
#                 continue
            
#             if "exit" in text.lower():
#                 print("\n[SYSTEM] 👋 Shutting down...")
#                 is_speaking.set()
#                 TTS.Speak("Goodbye!")
#                 sleep(0.5)
#                 break
            
#             process_user_input(text)
            
#             sleep(0.1)
            
#         except KeyboardInterrupt:
#             print("\n[SYSTEM] 🛑 Interrupted by user")
#             break
#         except Exception as e:
#             print(f"[ERROR] Main loop: {e}")
#             sleep(1)
    
#     print("\n" + "="*60)
#     print("✅ VOICE ASSISTANT STOPPED")
#     print("="*60)


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(f"[FATAL] {e}")
#     finally:
#         run = False
#         is_speaking.clear()
#         tasks_processing.clear()
#         print("[CLEANUP] Complete")























# from Backend import (
#     speech_to_text, 
#     model,
#     chatbot_module,
#     text_to_speech,
#     image_generation_module,
#     realtime_module,
#     google_search,
#     content_writing_module,
#     merolagani_module,
#     core,
#     youtube_module,
#     instagram_module,
#     facebook_module,
#     system_automation
# )
# import threading
# import queue
# from time import sleep
# from typing import List, Dict
# import re

# # Initialize all modules
# sound_manager = speech_to_text.SpeechRecognitionManager()
# TTS = text_to_speech.TextToSpeech()
# Chatbot_engine = chatbot_module.ChatBotEngine()
# Imagegeneration_system = image_generation_module.ImageGenerationModule()
# Realtime_Search_engine = realtime_module.RealtimeSearchModule()
# google_search_engine = google_search.GoogleSearchModule()
# content_writing_system = content_writing_module.ContentModule()
# merolagani_server = merolagani_module.MerolaganiModule()
# core_engine = core.Core()
# youtube_engine = youtube_module.YoutubeModule()
# instagram_engine = instagram_module.InstagramModule()
# facebook_engine = facebook_module.FacebookModule()
# system_automation_driver = system_automation.SystemAutomation()

# # Task queue for concurrent execution
# task_queue = queue.Queue()
# response_queue = queue.Queue()
# active_threads = []
# run = True

# # CRITICAL: Flag to prevent mic from listening while speaking
# is_speaking = threading.Event()
# is_speaking.clear()  # Initially not speaking


# def clean_query(query: str) -> str:
#     """Remove parentheses, extra spaces, and clean up query"""
#     # Remove parentheses
#     query = re.sub(r'[()]', '', query)
#     # Remove extra spaces
#     query = ' '.join(query.split())
#     return query.strip()


# def should_speak(task_type: str) -> bool:
#     """Determine if TTS should speak for this task type"""
#     speak_types = ["general", "realtime"]
#     return any(t in task_type.lower() for t in speak_types)


# class TaskCategory:
#     """Categories for different task types"""
#     GENERAL = "general"
#     REALTIME = "realtime"
#     IMAGE_GEN = "generate image"
#     AUTOMATION = "automation"
#     OPEN = "open"
#     CLOSE = "close"
#     GOOGLE_SEARCH = "google search"
#     YOUTUBE_SEARCH = "youtube search"
#     CONTENT = "content"
#     MEROLAGANI = "merolagani"
#     EXIT = "exit"


# def handle_general_query(query: str):
#     """Handle general chatbot queries"""
#     try:
#         query = clean_query(query)
#         response = Chatbot_engine.ask(query)
#         print(f"[GENERAL] {response}")
#         response_queue.put(("speak", response))
#     except Exception as e:
#         print(f"[ERROR] General query failed: {e}")


# def handle_realtime_query(query: str):
#     """Handle realtime search queries"""
#     try:
#         query = clean_query(query)
#         response = Realtime_Search_engine.realtime_query(query, num_results=5)
#         print(f"[REALTIME] {response}")
#         response_queue.put(("speak", response))
#     except Exception as e:
#         print(f"[ERROR] Realtime query failed: {e}")


# def handle_image_generation(query: str):
#     """Handle image generation - non-blocking"""
#     try:
#         query = clean_query(query)
#         print(f"[IMAGE] Generating image: {query}")
#         Imagegeneration_system.generate(query)
#         print(f"[IMAGE] ✅ Generation complete: {query}")
#     except Exception as e:
#         print(f"[ERROR] Image generation failed: {e}")


# def handle_google_search(query: str):
#     """Handle Google search"""
#     try:
#         query = clean_query(query)
#         google_search_engine.google_search(query)
#         print(f"[GOOGLE] ✅ Searched: {query}")
#     except Exception as e:
#         print(f"[ERROR] Google search failed: {e}")


# def handle_youtube_search(query: str):
#     """Handle YouTube search"""
#     try:
#         query = clean_query(query)
#         youtube_engine.youtube(query)
#         print(f"[YOUTUBE] ✅ Playing: {query}")
#     except Exception as e:
#         print(f"[ERROR] YouTube search failed: {e}")


# def handle_content_writing(query: str):
#     """Handle content writing"""
#     try:
#         query = clean_query(query)
#         content_writing_system.content(query)
#         print(f"[CONTENT] ✅ Written: {query}")
#     except Exception as e:
#         print(f"[ERROR] Content writing failed: {e}")


# def handle_merolagani(query: str):
#     """Handle Merolagani queries"""
#     try:
#         query = clean_query(query)
#         merolagani_server.merolagani(query)
#         print(f"[MEROLAGANI] ✅ Status: {query}")
#     except Exception as e:
#         print(f"[ERROR] Merolagani failed: {e}")


# def normalize_app_name(app_name: str) -> str:
#     """Normalize app names to match dictionary keys"""
#     app_name = clean_query(app_name).lower()
    
#     # Mapping variations to standard names
#     app_mappings = {
#         'vs code': 'vscode',
#         'visual studio code': 'vscode',
#         'code': 'vscode',
#         'whats app': 'whatsapp',
#         'what\'s app': 'whatsapp',
#         'whatsapp desktop': 'whatsapp',
#         'google chrome': 'chrome',
#         'control panel': 'controlpanel',
#         'my computer': 'mycomputer',
#         'this pc': 'mycomputer',
#         'file explorer': 'explorer',
#         'command prompt': 'cmd',
#         'power shell': 'powershell',
#     }
    
#     return app_mappings.get(app_name, app_name)


# def handle_open_command(query: str):
#     """Handle open commands"""
#     try:
#         query = clean_query(query)
#         normalized_name = normalize_app_name(query)
        
#         # Special cases for web apps
#         if "instagram" in query.lower():
#             instagram_engine.instagram()
#             print("[OPEN] ✅ Instagram")
#         elif "facebook" in query.lower():
#             facebook_engine.facebook()
#             print("[OPEN] ✅ Facebook")
#         elif "merolagani" in query.lower():
#             merolagani_server.merolagani("TTL")
#             print("[OPEN] ✅ Merolagani")
#         elif "youtube" in query.lower():
#             youtube_engine.youtube("Trending")
#             print("[OPEN] ✅ YouTube")
#         else:
#             system_automation_driver.open_app(normalized_name)
#             print(f"[OPEN] ✅ {normalized_name}")
#     except Exception as e:
#         print(f"[ERROR] Open command failed: {e}")


# def handle_close_command(query: str):
#     """Handle close commands"""
#     try:
#         query = clean_query(query)
#         normalized_name = normalize_app_name(query)
#         system_automation_driver.close_app(normalized_name)
#         print(f"[CLOSE] ✅ {normalized_name}")
#     except Exception as e:
#         print(f"[ERROR] Close command failed: {e}")


# def handle_automation(query: str):
#     """Handle automation tasks based on foreground app"""
#     try:
#         foreground_App = core_engine.get_foreground_app()
#         query = clean_query(query).lower()
        
#         print(f"[AUTOMATION] App: {foreground_App}, Command: {query}")
        
#         if foreground_App == "Youtube":
#             handle_youtube_automation(query)
#         elif foreground_App == "MeroLagani":
#             handle_merolagani_automation(query)
#         elif foreground_App == "Instagram":
#             handle_instagram_automation(query)
#         elif foreground_App == "Facebook":
#             handle_facebook_automation(query)
#         else:
#             handle_system_automation(query)
            
#     except Exception as e:
#         print(f"[ERROR] Automation failed: {e}")


# def handle_youtube_automation(query: str):
#     """YouTube-specific automation"""
#     if "next_video" in query or "next video" in query:
#         youtube_engine.next_video()
#         print("[YOUTUBE] ⏭️ Next video")
#     elif "previous_video" in query or "prev video" in query:
#         youtube_engine.previous_video()
#         print("[YOUTUBE] ⏮️ Previous video")
#     elif "play" in query:
#         youtube_engine.play()
#         print("[YOUTUBE] ▶️ Play")
#     elif "fullscreen" in query:
#         youtube_engine.fullscreen()
#         print("[YOUTUBE] ⛶ Fullscreen")
#     elif "mute" in query or "unmute" in query:
#         youtube_engine.mute_unmute()
#         print("[YOUTUBE] 🔇 Mute/Unmute")


# def handle_merolagani_automation(query: str):
#     """MeroLagani-specific automation"""
#     if "scroll" in query:
#         if "up" in query:
#             merolagani_server.scroll_up()
#             print("[MEROLAGANI] ⬆️ Scrolling up")
#         elif "stop" in query:
#             merolagani_server.stop_scroll()
#             print("[MEROLAGANI] ⏸️ Scroll stopped")
#         elif "down" in query:
#             merolagani_server.scroll_down()
#             print("[MEROLAGANI] ⬇️ Scrolling down")


# def handle_instagram_automation(query: str):
#     """Instagram-specific automation"""
#     if "scroll_feed_down" in query or "scroll feed down" in query:
#         instagram_engine.scroll_feed_down(1)
#         print("[INSTAGRAM] ⬇️ Scroll feed down")
#     elif "scroll_feed_up" in query or "scroll feed up" in query:
#         instagram_engine.scroll_feed_up(1)
#         print("[INSTAGRAM] ⬆️ Scroll feed up")
#     elif "scroll_down" in query:
#         instagram_engine.scroll_down()
#         print("[INSTAGRAM] ⬇️ Scroll down")
#     elif "scroll_up" in query:
#         instagram_engine.scroll_up()
#         print("[INSTAGRAM] ⬆️ Scroll up")
#     elif "stop_scroll" in query or "stop scroll" in query:
#         instagram_engine.stop_scroll_feed()
#         print("[INSTAGRAM] ⏸️ Scroll stopped")
#     elif "play_reels" in query or "play reels" in query:
#         instagram_engine.play_reels()
#         print("[INSTAGRAM] 🎬 Playing reels")
#     elif "mute" in query or "unmute" in query:
#         instagram_engine.mute_unmute()
#         print("[INSTAGRAM] 🔇 Mute/Unmute")
#     elif "pause" in query or "play" in query:
#         instagram_engine.play_pause()
#         print("[INSTAGRAM] ⏯️ Play/Pause")
#     elif "next_story" in query or "next story" in query:
#         instagram_engine.next_story()
#         print("[INSTAGRAM] ⏭️ Next story")
#     elif "prev_story" in query or "previous story" in query:
#         instagram_engine.prev_story()
#         print("[INSTAGRAM] ⏮️ Previous story")
#     elif "open_story" in query or "open story" in query:
#         instagram_engine.open_story()
#         print("[INSTAGRAM] 📖 Story opened")
#     elif "close_story" in query or "close story" in query:
#         instagram_engine.close_story()
#         print("[INSTAGRAM] ❌ Story closed")


# def handle_facebook_automation(query: str):
#     """Facebook-specific automation"""
#     if "play_video" in query or "play video" in query:
#         facebook_engine.play_videos()
#         print("[FACEBOOK] ▶️ Playing video")
#     elif "mute_video" in query or "unmute_video" in query:
#         facebook_engine.mute_unmute_video()
#         print("[FACEBOOK] 🔇 Mute/Unmute video")
#     elif "pause_video" in query or "pause video" in query:
#         facebook_engine.play_pause()
#         print("[FACEBOOK] ⏸️ Pause")
#     elif "show_stories" in query or "show stories" in query:
#         facebook_engine.open_story()
#         print("[FACEBOOK] 📖 Stories opened")
#     elif "next_story" in query or "next story" in query:
#         facebook_engine.next_story()
#         print("[FACEBOOK] ⏭️ Next story")
#     elif "prev_story" in query or "previous story" in query:
#         facebook_engine.prev_story()
#         print("[FACEBOOK] ⏮️ Previous story")
#     elif "close_story" in query or "close story" in query:
#         facebook_engine.close_story()
#         print("[FACEBOOK] ❌ Story closed")
#     elif "home_page" in query or "home page" in query:
#         facebook_engine.to_home_page()
#         print("[FACEBOOK] 🏠 Home page")
#     elif "scroll_feed_up" in query or "scroll feed up" in query:
#         facebook_engine.scroll_feed_up(1)
#         print("[FACEBOOK] ⬆️ Scroll feed up")
#     elif "scroll_feed_down" in query or "scroll feed down" in query:
#         facebook_engine.scroll_feed_down(1)
#         print("[FACEBOOK] ⬇️ Scroll feed down")
#     elif "stop_scroll" in query or "stop scroll" in query:
#         facebook_engine.stop_scroll_feed()
#         print("[FACEBOOK] ⏸️ Scroll stopped")


# def handle_system_automation(query: str):
#     """System-level automation"""
#     if "mute" in query and "unmute" not in query:
#         system_automation_driver.mute_system()
#         print("[SYSTEM] 🔇 Muted")
#     elif "unmute" in query:
#         system_automation_driver.unmute_system()
#         print("[SYSTEM] 🔊 Unmuted")
#     elif "switch_apps" in query or "switch app" in query or "switch to" in query:
#         # Extract app name after switch command
#         app_name = query.replace("switch_apps", "").replace("switch app", "").replace("switch to", "").strip()
#         app_name = clean_query(app_name)
        
#         # Try direct window switch first
#         if not system_automation_driver.switch_apps(app_name):
#             # Try normalized name
#             normalized = normalize_app_name(app_name)
#             system_automation_driver.switch_apps(normalized)
#         print(f"[SYSTEM] ↔️ Switched to: {app_name}")
#     elif "switch_chrome_tab" in query or "switch tab" in query:
#         tab_name = query.replace("switch_chrome_tab", "").replace("switch tab", "").strip()
#         system_automation_driver.switch_chrome_tab(tab_name)
#         print(f"[SYSTEM] 🗂️ Tab: {tab_name}")
#     elif "show desktop" in query or "minimize_everything" in query or "minimize everything" in query:
#         system_automation_driver.show_desktop()
#         print("[SYSTEM] 🖥️ Desktop shown")
#     elif "minimize_active_window" in query or "minimize window" in query:
#         system_automation_driver.minimize_active_window()
#         print("[SYSTEM] ⬇️ Window minimized")
#     elif "screenshot" in query or "take screenshot" in query:
#         system_automation_driver.take_screenshot()
#         print("[SYSTEM] 📸 Screenshot taken")
#     elif "set_volume" in query or "set volume" in query:
#         volume = ''.join(filter(str.isdigit, query))
#         if volume:
#             system_automation_driver.set_volume(int(volume))
#             print(f"[SYSTEM] 🔊 Volume: {volume}%")
#     elif "change_volume_by" in query or "volume up" in query or "volume down" in query:
#         if "up" in query:
#             system_automation_driver.change_volume_by(10)
#             print("[SYSTEM] 🔊 Volume +10%")
#         elif "down" in query:
#             system_automation_driver.change_volume_by(-10)
#             print("[SYSTEM] 🔉 Volume -10%")
#     elif "set_brightness" in query or "set brightness" in query:
#         brightness = ''.join(filter(str.isdigit, query))
#         if brightness:
#             system_automation_driver.set_brightness(int(brightness))
#             print(f"[SYSTEM] ☀️ Brightness: {brightness}%")
#     elif "change_brightness_by" in query or "brightness up" in query or "brightness down" in query:
#         if "up" in query:
#             system_automation_driver.change_brightness_by(10)
#             print("[SYSTEM] ☀️ Brightness +10%")
#         elif "down" in query:
#             system_automation_driver.change_brightness_by(-10)
#             print("[SYSTEM] 🌙 Brightness -10%")


# def task_executor(task: str):
#     """Execute individual tasks in separate threads"""
#     try:
#         task_lower = task.lower()
#         task_type = ""
        
#         # Identify task type for TTS decision
#         if "general" in task_lower:
#             task_type = "general"
#             query = task.replace("general", "", 1).strip()
#             handle_general_query(query)
            
#         elif "generate image" in task_lower:
#             task_type = "image"
#             query = task.replace("generate image", "", 1).strip()
#             handle_image_generation(query)
            
#         elif "realtime" in task_lower:
#             task_type = "realtime"
#             query = task.replace("realtime", "", 1).strip()
#             handle_realtime_query(query)
            
#         elif "google search" in task_lower:
#             task_type = "search"
#             query = task.replace("google search", "", 1).strip()
#             handle_google_search(query)
            
#         elif "youtube search" in task_lower:
#             task_type = "youtube"
#             query = task.replace("youtube search", "", 1).strip()
#             handle_youtube_search(query)
            
#         elif "content" in task_lower:
#             task_type = "content"
#             query = task.replace("content", "", 1).strip()
#             handle_content_writing(query)
            
#         elif "merolagani" in task_lower:
#             task_type = "merolagani"
#             query = task.replace("merolagani", "", 1).strip()
#             handle_merolagani(query)
            
#         elif "close" in task_lower:
#             task_type = "close"
#             query = task.replace("close", "", 1).strip()
#             handle_close_command(query)
            
#         elif "open" in task_lower:
#             task_type = "open"
#             query = task.replace("open", "", 1).strip()
#             handle_open_command(query)
            
#         elif "automation" in task_lower:
#             task_type = "automation"
#             query = task.replace("automation", "", 1).strip()
#             handle_automation(query)
            
#         elif "exit" in task_lower:
#             global run
#             run = False
#             response_queue.put(("speak", "Goodbye!"))
            
#         else:
#             print(f"[UNHANDLED] {task}")
            
#     except Exception as e:
#         print(f"[ERROR] Task execution failed: {e}")


# def task_worker():
#     """Worker thread that processes tasks from queue"""
#     while run:
#         try:
#             if not task_queue.empty():
#                 task = task_queue.get()
#                 print(f"[WORKER] Processing: {task}")
#                 task_executor(task)
#                 task_queue.task_done()
#             else:
#                 sleep(0.05)
#         except Exception as e:
#             print(f"[ERROR] Worker thread error: {e}")
#             sleep(0.5)


# def response_handler():
#     """Handle responses and TTS only for general/realtime queries"""
#     while run:
#         try:
#             if not response_queue.empty():
#                 action, message = response_queue.get()
#                 if action == "speak":
#                     # Set speaking flag BEFORE starting to speak
#                     is_speaking.set()
#                     print("[MIC] 🔇 Microphone MUTED (Speaking...)")
                    
#                     # Speak the message
#                     TTS.Speak(message)
                    
#                     # Add small delay to ensure speech completes
#                     sleep(0.5)
                    
#                     # Clear speaking flag AFTER speaking is done
#                     is_speaking.clear()
#                     print("[MIC] 🎤 Microphone ACTIVE (Listening...)")
                    
#                 response_queue.task_done()
#             else:
#                 sleep(0.05)
#         except Exception as e:
#             print(f"[ERROR] Response handler error: {e}")
#             is_speaking.clear()  # Ensure flag is cleared on error
#             sleep(0.5)


# def process_user_input(text: str):
#     """Process user input and queue tasks concurrently"""
#     try:
#         print(f"\n{'='*60}")
#         print(f"[USER] {text}")
#         print(f"{'='*60}")
        
#         # Get list of tasks from model
#         list_of_tasks = model.ModelModule().FirstLayerDMM(text)
#         print(f"[TASKS] {list_of_tasks}\n")
        
#         # Queue all tasks for concurrent execution
#         for task in list_of_tasks:
#             task_queue.put(task)
            
#         # Start worker threads for each task (max 5 concurrent)
#         num_workers = min(len(list_of_tasks), 5)
#         for _ in range(num_workers):
#             worker = threading.Thread(target=task_worker, daemon=True)
#             worker.start()
#             active_threads.append(worker)
            
#     except Exception as e:
#         print(f"[ERROR] Input processing failed: {e}")


# def main():
#     """Main execution loop"""
#     print("\n" + "="*60)
#     print("🎙️  VOICE ASSISTANT STARTED")
#     print("="*60)
#     print("📌 Ready to listen...")
#     print("💬 Say 'exit' to quit\n")
    
#     # Start response handler thread
#     response_thread = threading.Thread(target=response_handler, daemon=True)
#     response_thread.start()
    
#     while run:
#         try:
#             # CRITICAL: Only listen if NOT speaking
#             if is_speaking.is_set():
#                 # System is currently speaking, skip listening
#                 sleep(0.1)
#                 continue
            
#             # Listen for speech input
#             text = sound_manager.speech_recognition()
            
#             if not text:
#                 sleep(0.05)
#                 continue
            
#             # Check for exit command early
#             if "exit" in text.lower():
#                 print("\n[SYSTEM] 👋 Shutting down...")
#                 is_speaking.set()
#                 TTS.Speak("Goodbye!")
#                 sleep(0.5)
#                 break
            
#             # Process the input
#             process_user_input(text)
            
#             # Small delay to prevent overwhelming
#             sleep(0.1)
            
#         except KeyboardInterrupt:
#             print("\n[SYSTEM] 🛑 Interrupted by user")
#             break
#         except Exception as e:
#             print(f"[ERROR] Main loop: {e}")
#             sleep(1)
    
#     print("\n" + "="*60)
#     print("✅ VOICE ASSISTANT STOPPED")
#     print("="*60)


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(f"[FATAL] {e}")
#     finally:
#         run = False
#         is_speaking.clear()
#         print("[CLEANUP] Complete")











# from Backend import (
#     speech_to_text, 
#     model,
#     chatbot_module,
#     text_to_speech,
#     image_generation_module,
#     realtime_module,
#     google_search,
#     content_writing_module,
#     merolagani_module,
#     core,
#     youtube_module,
#     instagram_module,
#     facebook_module,
#     system_automation
# )

# sound_manager = speech_to_text.SpeechRecognitionManager()
# TTS = text_to_speech.TextToSpeech()
# Chatbot_engine = chatbot_module.ChatBotEngine()
# Imagegeneration_system=image_generation_module.ImageGenerationModule()
# Realtime_Search_engine=realtime_module.RealtimeSearchModule()
# google_search_engine=google_search.GoogleSearchModule()
# content_writing_system=content_writing_module.ContentModule()
# merolagani_server=merolagani_module.MerolaganiModule()
# core_engine=core.Core()
# youtube_engine=youtube_module.YoutubeModule()
# instagram_engine=instagram_module.InstagramModule()
# facebook_engine=facebook_module.FacebookModule()
# system_automation_driver=system_automation.SystemAutomation()

# run = True
# while run:
#     text = sound_manager.speech_recognition()
#     if not text:   # skip if nothing detected
#         continue

#     print(f"User Input: {text}")

#     if "exit" in text.lower():  # early exit check
#         run = False
#         break

#     list_of_tasks = model.ModelModule().FirstLayerDMM(text)
#     print(list_of_tasks)

#     for task in list_of_tasks:
#         if "general" in task:
#             query = task.replace("general ", "", 1)
#             response = Chatbot_engine.ask(query)
#             print(response)
#             TTS.Speak(response)
            
#         elif "generate image" in task:
#             query=task.replace("generate image","",1)
#             response =Imagegeneration_system.generate(query)
#             print(f"Generating image of {query}")
#             TTS.Speak("Generating image of" +query)
            
#         elif "realtime" in task:
#             query=task.replace("realtime","",1)
#             response=Realtime_Search_engine.realtime_query(query,num_results=5)
#             print(response)
#             TTS.Speak(response)
            
#         elif "google search" in task:
#             query=task.replace("google search","",1)
#             google_search_engine.google_search(query)
#             print("Searching in google")
#             TTS.Speak("Searched in google")
            
#         elif "content" in task:
#             query=task.replace("content","",1)
#             content_writing_system.content(query)
#             print(f"writing {query}")
#             TTS.Speak("Writing"+query)
            
#         elif "merolagani" in task:
#             query=task.replace("merolagani","",1)
#             merolagani_server.merolagani(query)
#             print(f"Showing the status of{query} in Mero lagani")
#             TTS.Speak("Showing the status of"+query+"in Mero lagani")
            
#         elif "youtube search" in task:
#             query=task.replace("youtube search","",1)
#             TTS.Speak("Playing "+query+" On youtube")
#             youtube_engine.youtube(query)
#             print(f"Playing{query} in Youtube")
            
#         elif "open" in task:
#             query=task.replace("open","",1)
#             if "instagram" in query:
#                 print("Opening Instagram")
#                 TTS.Speak("Opening Instagram")
#                 instagram_engine.instagram()
#                 print("Instagram Opened")
            
#             elif "facebook" in query:
#                 print("Opening Facebook")
#                 TTS.Speak("Opening Facebook")
#                 facebook_engine.facebook()
#                 print("Facebook Opened")
                
#             elif "merolagani" in query:
#                 merolagani_server.merolagani("TTL")
                
#             elif "youtube" in query:
#                 youtube_engine.youtube("Ganja bro")
            
#             else:
#                 system_automation_driver.open_app(query)
                  
        
#         elif "automation" in task:
#             foreground_App=core_engine.get_foreground_app()
#             query=task.replace("automation","",1)
#             if foreground_App=="Youtube":
#                 if "next_video" in query :
#                     youtube_engine.next_video()
#                     print("Next video played in youtube")
                    
#                 elif "previous_video" in query:
#                     youtube_engine.previous_video()
                    
#                 elif "play_video" in query:
#                     youtube_engine.play()
                    
#                 elif "fullscreen" in query:
#                     youtube_engine.fullscreen()
                    
#                 elif "mute_video" in query:
#                     youtube_engine.mute_unmute()
                    
#                 elif "unmute_video" in query:
#                     youtube_engine.mute_unmute()
                    
#             elif foreground_App=="MeroLagani":
#                 if "scroll" in query:
#                     if "up" in query:
#                         merolagani_server.scroll_up()
#                         print("Scrolling up in MeroLagani Site")
                        
#                     if "stop" in query:
#                         merolagani_server.stop_scroll()
#                         print("Scroll Stopped in MeroLagani Site")
                            
#                     if "down" in query:
#                         merolagani_server.scroll_down()
#                         print("Scrolling down in MeroLagani Site")
                        
#             elif foreground_App=="Instagram":
#                 if "scroll_feed_down" in query:
#                     instagram_engine.scroll_feed_down(1)
#                 elif "scroll_feed_up" in query:
#                     instagram_engine.scroll_feed_up(1)
#                 elif "scroll_down" in query:
#                     instagram_engine.scroll_down()
#                 elif "scroll_up" in query:
#                     instagram_engine.scroll_up()
#                 elif "stop_scrolling_feed" in query or "stop_scroll_feed":
#                     instagram_engine.stop_scroll_feed()
#                 elif "play_reels" in query:
#                     instagram_engine.play_reels()
#                 elif "mute reels" in query or "unmute reels" in query:
#                     instagram_engine.mute_unmute()
#                 elif "pause" in query or "play" in query:
#                     instagram_engine.play_pause()
#                 elif "next_story" in query:
#                     instagram_engine.next_story()
#                 elif "previous_story" in query:
#                     instagram_engine.prev_story()
#                 elif "open_story" in query:
#                     instagram_engine.open_story()
#                 elif "close_story" in query:
#                     instagram_engine.close_story()
#                 elif "mute_story" in query or "unmute_story" in query:
#                     instagram_engine.mute_unmute_story()
#                 elif "pause" in query or "play" in query:
#                     instagram_engine.play_pause_story()
                         
#             elif foreground_App=="Facebook":
#                 if "play_video" in query:
#                     facebook_engine.play_videos()
#                 elif "mute_video" in query or "unmute_video" in query:
#                     facebook_engine.mute_unmute_video()
#                 elif "pause_video" in query or "play_video" in query:
#                     facebook_engine.play_pause()
#                 elif "show_stories" in query:
#                     facebook_engine.open_story()
#                 elif "next_story" in query:
#                     facebook_engine.next_story()
#                 elif "previous_story" in query:
#                     facebook_engine.prev_story()
#                 elif "close_story" in query:
#                     facebook_engine.close_story()
#                 elif "mute_story" in query or "unmute_story" in query:
#                     facebook_engine.mute_unmute_story()
#                 elif "go_to_home_page" in query:
#                     facebook_engine.to_home_page()
#                 elif "play_story" in query or "pause" in query or "pause_story" in query:
#                     facebook_engine.play_pause_story()
#                 elif "scroll_feed_up" in query:
#                     facebook_engine.scroll_feed_up(1)
#                 elif "scroll_feed_down" in query:
#                     facebook_engine.scroll_feed_down(1)  
#                 elif "stop_scrolling" in query:
#                     facebook_engine.stop_scroll_feed()      
            
#             elif "mute" in query:
#                 system_automation_driver.mute_system()
                
#             elif "unmute" in query:
#                 system_automation_driver.unmute_system()
            
#             elif "switch_apps" in query:
#                 app_name=query.replace("switch_apps","",1)
#                 system_automation_driver.switch_apps(app_name)
            
#             elif "switch_chrome_tab" in query:
#                 tab_name=query.replace("switch_chrome_tab","",1)
#                 system_automation_driver.switch_chrome_tab(tab_name)
                
#             elif "show desktop" in query or "minimize_everything" in query:
#                 system_automation_driver.show_desktop()
                
#             elif "minimize_active_window" in query:
#                 system_automation_driver.minimize_active_window()
            
#             elif "take_screenshot" in query:
#                 system_automation_driver.take_screenshot()
                
#             elif "set_volume" in query:
#                 volume=query.replace("set_volume","",1)
#                 system_automation_driver.set_volume(volume)
                
#             elif "change_volume_by" in query:
#                 volume=query.replace("change_volume_by","",1)
#                 system_automation_driver.change_volume_by(volume)
                
#             elif "set_brightness" in query:
#                 brightness_value=query.replace("set_brightness","",1)
#                 system_automation_driver.set_brightness(brightness_value)
                
#             elif "change_brightness_by" in query:
#                 brightness_value=query.replace("change_brightness_by","",1)
#                 system_automation_driver.change_brightness_by(brightness_value)
                
#         else:
#             print(f"Unhandled task: {task}")
