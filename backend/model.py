import os
import cohere
from rich import print
from dotenv import dotenv_values

class ModelModule:
    def __init__(self):

        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"[info] BASE_DIR detected: {self.BASE_DIR}")

        # ---------- Load .env from main folder ----------
        env_path = os.path.join(self.BASE_DIR, ".env")
        if not os.path.exists(env_path):
            print(f"[warning] .env file not found at {env_path}")
            self.env = {}
        else:
            self.env = dotenv_values(env_path)
            print(f"[info] .env loaded from {env_path}")

        # ---------- Fetch configuration ----------
        self.Username = self.env.get("Username", "User")
        self.Assistantname = self.env.get("Assistantname", "Assistant")
        self.COHERE_API_KEY = self.env.get("COHERE_API_KEY") or os.environ.get("COHERE_API_KEY")
        if not self.COHERE_API_KEY:
            raise ValueError("❌ No Cohere API Key found. Put COHERE_API_KEY in .env")

        # ---------- Init Cohere client ----------
        try:
            self.co = cohere.Client(api_key=self.COHERE_API_KEY)
            print("[info] Cohere client initialized successfully")
        except Exception as e:
            print("[error] Failed to initialize Cohere client:", e)
            raise


        self.funcs = [
            "exit", "general", "realtime", "open", "close", "play",
            "generate image", "system", "content", "google search",
            "youtube search", "reminder", "automation"
        ]

        self.messages = []

        self.preamble = """
            You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
            You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
            *** Do not answer any query, just decide what kind of query is given to you. ***
            -> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
            -> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
            -> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
            -> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
            -> Respond with 'merolagani (share name)' if a query is asking to show the status of any share eg 'show me HRL shares in merolagani','show me the status of Trade Tower Limited' then respond like merolagani(Trade Tower Limited). but if the query is asking to do multiple shares, respond with 'merolagani 1st share, merolagani 2nd share', etc.
            -> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
            -> Respond with 'open (application name)' if a query is asking to open any system application like 'open settings', 'open whatsapp','open notepad', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
            -> Respond with 'close (application name)' if a query is asking to close any system application like 'close notepad', 'close chrome', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
            -> Respond with 'youtube search (topic)' if query asks to search YouTube or play songs. Examples: 'search python on youtube', 'play afsanay by ys', 'play let her go'. Multiple: 'youtube search topic1, youtube search topic2'.
            -> Respond with 'automation (action)' if query contains automation/control commands. Examples:
            - Social: 'open reels', 'open videos', 'show stories', 'next story', 'previous story', 'go to home page'
            - Media: 'mute', 'unmute', 'pause', 'play', 'mute reels', 'pause video', 'mute video', 'unmute video', 'full screen', 'seek forward', 'seek backward'
            - Scroll: 'scroll up', 'scroll down', 'scroll feed up', 'scroll feed down', 'stop scrolling', 'swipe left', 'swipe right'
            - Switch: 'minimize this' or 'minimize current window'→'minimize_active_window','switch to vs code' → 'automation switch_apps vscode', 'switch to chrome' → 'automation switch_apps chrome', 'switch to youtube tab' → 'automation switch_chrome_tab youtube', 'switch to instagram' → 'automation switch_chrome_tab instagram', 'switch to facebook' → 'automation switch_chrome_tab facebook', 'switch to merolagani' → 'automation switch_chrome_tab merolagani'
            - Window: 'minimize everything' → 'automation show_desktop', 'show desktop' → 'automation show_desktop', 'minimize chrome' → 'automation minimize_active_window chrome'
            - System: 'take screenshot' → 'automation take_screenshot', 'set volume to 50' → 'automation set_volume 50', 'increase volume by 30' → 'automation change_volume_by 30', 'decrease volume by 50' → 'automation change_volume_by -50', 'set brightness to 50' → 'automation set_brightness 50', 'increase brightness by 50' → 'automation change_brightness_by 50', 'decrease brightness by 50' → 'automation change_brightness_by -50'
            Multiple: 'automation action1, automation action2'.
            *** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
            *** If the user is saying goodbye or wants to end the conversation like 'bye Omnis.' respond with 'exit'.***
            *** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
            """
            
        # -> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.


        self.ChatHistory = [
            {"role": "User", "message": "how are you ?"},
            {"role": "Chatbot", "message": "general how are you ?"},
            {"role": "User", "message": "do you like pizza ?"},
            {"role": "Chatbot", "message": "general do you like pizza ?"},
            {"role": "User", "message": "how are you ?"},
            {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
            {"role": "Chatbot", "message": "automation chrome, general tell me about mahatma gandhi."},
            {"role": "User", "message": "open chrome and firefox"},
            {"role": "Chatbot", "message": "automation chrome, automation firefox"},
            {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th at 11pm "},
            {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
            {"role": "User", "message": "chat with me."},
            {"role": "Chatbot", "message": "general chat with me."},
            {"role": "User", "message": "scroll up"},
            {"role": "Chatbot", "message": "automation scroll up"},
            {"role": "User", "message": "play music on youtube"},
            {"role": "Chatbot", "message": "automation youtube music"},
            {"role": "User", "message": "mute the volume"},
            {"role": "Chatbot", "message": "automation mute"}
        ]

    def _find_project_root(self):
        """Find the project root directory by looking for 'omnis.ai' folder."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
            if os.path.basename(current_dir) == "omnis.ai":
                return current_dir
            current_dir = os.path.dirname(current_dir)
        # If not found, return the directory containing this script
        return os.path.dirname(os.path.abspath(__file__))

    def FirstLayerDMM(self, prompt: str = "test"):
        self.messages.append({"role": "user", "content": prompt})

        # ✅ Use chat_stream with 'message' instead of 'messages'
        stream = self.co.chat_stream(
            model="command-a-03-2025",
            message=prompt,  # <-- single message, not a list
            temperature=0.7,
            preamble=self.preamble
            # chat_history is NOT supported like before
        )

        response = ""

        for event in stream:
            if event.event_type == "text-generation":
                response += event.text
            elif event.event_type == "stream-end":
                break  # ✅ stop streaming when done

        response = response.replace("\n", "")
        response = [i.strip() for i in response.split(",")]

        # filter only known funcs
        response = [task for task in response if any(task.startswith(func) for func in self.funcs)]

        if not response or "(query)" in "".join(response):
            return ["general " + prompt]
        return response


if __name__ == "__main__":
    model = ModelModule()
    while True:
        user_input = input(">>> ")
        print(model.FirstLayerDMM(user_input))
        
        
        
        
# self.preamble = """
        #     You are a Query Classification System. Your ONLY job is to classify user queries into specific categories and return the appropriate command format.

        #     ⚠️ CRITICAL RULES:
        #     - DO NOT answer queries - only classify them
        #     - DO NOT engage in conversation - only output the classification
        #     - Always return the exact format specified for each category
        #     - For multi-task queries, separate commands with commas

        #     ═══════════════════════════════════════════════════════════════════

        #     📋 CLASSIFICATION CATEGORIES & FORMATS:

        #     1. GENERAL QUERIES → Format: "general (query)"
        #     Use when:
        #     • Query can be answered by an LLM without real-time data
        #     • Educational/informational questions (e.g., "what is photosynthesis?")
        #     • Advice/help requests (e.g., "how can I study better?")
        #     • Conversational responses (e.g., "thanks, I liked it")
        #     • Math/coding help (e.g., "help me with this problem")
        #     • Incomplete queries with pronouns (e.g., "who is he?", "tell me about it")
        #     • Time-related questions (e.g., "what's the time?", "what day is it?")
        #     • Historical facts (e.g., "who was Napoleon?")
            
        #     Examples:
        #     "how does gravity work?" → general how does gravity work?
        #     "thanks!" → general thanks!
        #     "who is he?" → general who is he?
        #     "what time is it?" → general what time is it?

        #     ───────────────────────────────────────────────────────────────────

        #     2. REALTIME QUERIES → Format: "realtime (query)"
        #     Use when:
        #     • Query requires current/up-to-date information
        #     • Asking about current events, news, or headlines
        #     • Questions about living people/current status (e.g., "who is the prime minister?")
        #     • Recent updates about products/services
        #     • Current statistics or trending topics
            
        #     Examples:
        #     "who is the Indian prime minister?" → realtime who is the Indian prime minister?
        #     "today's news about AI" → realtime today's news about AI
        #     "tell me about Facebook's latest update" → realtime tell me about Facebook's latest update
        #     "what's trending on Twitter?" → realtime what's trending on Twitter?

        #     ───────────────────────────────────────────────────────────────────

        #     3. GOOGLE SEARCH → Format: "google search (topic)"
        #     Use when:
        #     • Explicitly asking to search Google
        #     • Multiple searches: separate with commas
            
        #     Examples:
        #     "search Python on Google" → google search Python
        #     "google machine learning and AI" → google search machine learning, google search AI

        #     ───────────────────────────────────────────────────────────────────

        #     4. IMAGE GENERATION → Format: "generate image (prompt)"
        #     Use when:
        #     • Explicitly asking to create/generate an image
        #     • Multiple images: separate with commas
            
        #     Examples:
        #     "generate image of a sunset" → generate image a sunset
        #     "create images of a cat and a dog" → generate image a cat, generate image a dog

        #     ───────────────────────────────────────────────────────────────────

        #     5. MEROLAGANI SHARES → Format: "merolagani (share name)"
        #     Use when:
        #     • Asking for share/stock status on Merolagani
        #     • Multiple shares: separate with commas
            
        #     Examples:
        #     "show HRL shares in Merolagani" → merolagani HRL
        #     "check Trade Tower Limited" → merolagani Trade Tower Limited
        #     "show HRL and NTC shares" → merolagani HRL, merolagani NTC

        #     ───────────────────────────────────────────────────────────────────

        #     6. CONTENT WRITING → Format: "content (topic)"
        #     Use when:
        #     • Asking to write/create content (code, emails, applications, essays, etc.)
        #     • Multiple content pieces: separate with commas
            
        #     Examples:
        #     "write a Python script for web scraping" → content Python script for web scraping
        #     "write an email to my boss and a letter to HR" → content email to boss, content letter to HR

        #     ───────────────────────────────────────────────────────────────────

        #     7. OPEN APPLICATION → Format: "open (application name)"
        #     Use when:
        #     • Asking to open/launch system applications or websites
        #     • Multiple applications: separate with commas
            
        #     Examples:
        #     "open Chrome" → open Chrome
        #     "open Notepad and Calculator" → open Notepad, open Calculator
        #     "open Facebook" → open Facebook

        #     ───────────────────────────────────────────────────────────────────

        #     8. CLOSE APPLICATION → Format: "close (application name)"
        #     Use when:
        #     • Asking to close/exit applications or websites
        #     • Multiple applications: separate with commas
            
        #     Examples:
        #     "close Chrome" → close Chrome
        #     "close Notepad and Spotify" → close Notepad, close Spotify

        #     ───────────────────────────────────────────────────────────────────

        #     9. YOUTUBE SEARCH → Format: "youtube search (topic)"
        #     Use when:
        #     • Asking to search YouTube OR play songs/videos
        #     • Multiple searches: separate with commas
            
        #     Examples:
        #     "search Python tutorials on YouTube" → youtube search Python tutorials
        #     "play Despacito" → youtube search Despacito
        #     "play Bohemian Rhapsody and Stairway to Heaven" → youtube search Bohemian Rhapsody, youtube search Stairway to Heaven

        #     ───────────────────────────────────────────────────────────────────

        #     10. AUTOMATION COMMANDS → Format: "automation (action)"
        #         Use when query contains control/automation commands:
                
        #         🔹 SOCIAL MEDIA CONTROLS:
        #         • "open reels" → automation open_reels
        #         • "show stories" → automation show_stories
        #         • "next story" → automation next_story
        #         • "previous story" → automation previous_story
        #         • "go to home page" → automation go_to_home
                
        #         🔹 MEDIA CONTROLS:
        #         • "mute" → automation mute
        #         • "unmute" → automation unmute
        #         • "pause" → automation pause
        #         • "play" → automation play
        #         • "pause video" → automation pause_video
        #         • "full screen" → automation fullscreen
        #         • "seek forward" → automation seek_forward
        #         • "seek backward" → automation seek_backward
                
        #         🔹 SCROLLING CONTROLS:
        #         • "scroll up" → automation scroll_up
        #         • "scroll down" → automation scroll_down
        #         • "scroll feed down" → automation scroll_feed_down
        #         • "stop scrolling" → automation stop_scrolling
        #         • "swipe left" → automation swipe_left
        #         • "swipe right" → automation swipe_right
                
        #         🔹 WINDOW SWITCHING:
        #         • "switch to VS Code" → automation switch_apps vscode
        #         • "switch to Chrome" → automation switch_apps chrome
        #         • "switch to YouTube tab" → automation switch_chrome_tab youtube
        #         • "switch to Instagram" → automation switch_chrome_tab instagram
        #         • "switch to Facebook" → automation switch_chrome_tab facebook
                
        #         🔹 WINDOW MANAGEMENT:
        #         • "minimize everything" → automation show_desktop
        #         • "show desktop" → automation show_desktop
        #         • "minimize Chrome" → automation minimize_active_window chrome
                
        #         🔹 SYSTEM CONTROLS:
        #         • "take screenshot" → automation take_screenshot
        #         • "set volume to 50" → automation set_volume 50
        #         • "increase volume by 30" → automation change_volume_by 30
        #         • "decrease volume by 50" → automation change_volume_by -50
        #         • "set brightness to 70" → automation set_brightness 70
        #         • "increase brightness by 20" → automation change_brightness_by 20
        #         • "decrease brightness by 30" → automation change_brightness_by -30
                
        #         Multiple automation commands: separate with commas

        #     ───────────────────────────────────────────────────────────────────

        #     11. EXIT COMMAND → Format: "exit"
        #         Use when:
        #         • User wants to end conversation (e.g., "bye", "goodbye", "exit")
                
        #         Examples:
        #         "bye Omnis" → exit
        #         "goodbye" → exit

        #     ═══════════════════════════════════════════════════════════════════

        #     🎯 DECISION-MAKING PRIORITY ORDER:

        #     1. Check for EXIT commands first
        #     2. Check for AUTOMATION commands (specific control actions)
        #     3. Check for APPLICATION commands (open/close)
        #     4. Check for SERVICE-SPECIFIC commands (YouTube, Google, Merolagani, Images)
        #     5. Check for CONTENT WRITING requests
        #     6. Determine if REALTIME or GENERAL:
        #     • Has proper nouns + needs current info → REALTIME
        #     • Lacks proper nouns OR vague/incomplete → GENERAL
        #     • Can be answered with static knowledge → GENERAL

        #     ═══════════════════════════════════════════════════════════════════

        #     ⚠️ SPECIAL CASES:

        #     • Multi-task queries: Parse each task separately
        #     Example: "open Facebook, play Despacito, close Chrome"
        #     Output: open Facebook, youtube search Despacito, close Chrome

        #     • Ambiguous queries: Default to GENERAL
        #     Example: "tell me more" → general tell me more

        #     • Incomplete queries with pronouns: Always GENERAL
        #     Example: "who is she?" → general who is she?

        #     • Time/date questions: Always GENERAL
        #     Example: "what's today's date?" → general what's today's date?

        #     ═══════════════════════════════════════════════════════════════════

        #     ✅ OUTPUT FORMAT:
        #     - Single command: Just output the classified command
        #     - Multiple commands: Separate with commas (no extra spaces)
        #     - Always maintain the exact format specified for each category
        #     - Do not add explanations, acknowledgments, or extra text

        #     BEGIN CLASSIFICATION NOW.
        #     """

        # self.preamble = """
        #     You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
        #     You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
        #     *** Do not answer any query, just decide what kind of query is given to you. ***
        #     -> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
        #     -> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
        #     -> Respond with 'automation (action details)' if a query contains automation commands like 'open', 'mute', 'skip', 'next', 'previous', 'left', 'right', 'swipe left', 'swipe right', 'up', 'down', 'scroll up', 'scroll down', etc. For example: if the query is 'open instagram' respond with 'automation instagram', if the query is 'play music on youtube' respond with 'automation youtube music', if the query is 'scroll up' respond with 'automation scroll up', if the query is 'mute' respond with 'automation mute', if the query is 'next song' respond with 'automation next song', if the query is 'swipe left' respond with 'automation swipe left', etc.
        #     -> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
        #     -> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
        #     -> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
        #     -> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
        #     -> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
        #     -> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
        #     -> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
        #     -> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
        #     -> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
        #     *** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
        #     *** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
        #     *** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
        # """