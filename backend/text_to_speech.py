
import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Get the absolute path of the parent directory (MainFolder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(BASE_DIR, ".env")

# Load .env from MainFolder
env_vars = dotenv_values(env_path)
AssistantGender = env_vars.get("AssistantGender", "Male")  # Default one

# Voice map
VOICE_MAP = {
    "Male": "en-GB-RyanNeural",  
    "Female": "en-US-AriaNeural"
}
AssistantVoice = VOICE_MAP.get(AssistantGender, "en-GB-RyanNeural")


class TextToSpeech:
    
    @staticmethod
    async def TextToAudioFile(text) -> None:
        file_path = os.path.join(BASE_DIR, "Data", "speech.mp3")

        # Ensure Data folder exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            os.remove(file_path)

        # Pitch & Rate depending on gender
        if AssistantGender == "Male":
            pitch = "-2Hz"   
            rate = "+2%"     
        else:  # Female
            pitch = "+4Hz"   
            rate = "+5%" 

        communicate = edge_tts.Communicate(text, AssistantVoice, pitch=pitch, rate=rate)
        await communicate.save(file_path)

    @staticmethod
    def TTS(Text, func=lambda r=None: True):
        while True:
            try:
                asyncio.run(TextToSpeech.TextToAudioFile(Text))

                pygame.mixer.init()
                file_path = os.path.join(BASE_DIR, "Data", "speech.mp3")
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()

                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    if not func():
                        break
                    clock.tick(10)

                return True
            except Exception as e:
                print(f"Error in TTS : {e}")

            finally:
                try:
                    if pygame.mixer.get_init():
                        func(False)
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                except Exception as e:
                    print(f"Error in finally block: {e}")

    @staticmethod
    def DefaultMessage(func=lambda r=None: True):
        """Speaks the default startup message from beginning to end without interruption"""
        Data = """Good morning, Sir. The current time is 7:03 AM.  
            The weather today is clear with a temperature of 72 degrees Fahrenheit and light winds from the west.  
            Your next meeting is scheduled at 9:00 AM with Pepper Potts regarding the Stark Industries project.  
            Traffic on your usual route is light; estimated travel time to the office is 18 minutes.  
            The stock market opened positively today. The S&P 500 is up by 1.2 percent, and Tesla shares have increased by 2.3 percent.  
            All security systems are online and functioning normally. No unusual activity has been detected overnight.  
            The coffee machine is ready and has brewed your preferred blend.  
            Sir, your suit diagnostics are complete. All systems are functioning within normal parameters.  
            Have a productive and efficient day, Sir. Would you like me to review your agenda for today?"""
        
        TextToSpeech.TTS(Data, func)

    @staticmethod
    def Speak(Text, func=lambda r=None: True):
        Data = str(Text).split(".")

        responses = [
            "The rest of the result has been printed to the chat screen, kindly check it out sir.",
            "The rest of the text is now on the chat screen, sir, please check it.",
            "You can see the rest of the text on the chat screen, sir.",
            "The remaining part of the text is now on the chat screen, sir.",
            "Sir, you'll find more text on the chat screen for you to see.",
            "The rest of the answer is now on the chat screen, sir.",
            "Sir, please look at the chat screen, the rest of the answer is there.",
            "You'll find the complete answer on the chat screen, sir.",
            "The next part of the text is on the chat screen, sir.",
            "Sir, please check the chat screen for more information.",
            "There's more text on the chat screen for you, sir.",
            "Sir, take a look at the chat screen for additional text.",
            "You'll find more to read on the chat screen, sir.",
            "Sir, check the chat screen for the rest of the text.",
            "The chat screen has the rest of the text, sir.",
            "There's more to see on the chat screen, sir, please look.",
            "Sir, the chat screen holds the continuation of the text.",
            "You'll find the complete answer on the chat screen, kindly check it out sir.",
            "Please review the chat screen for the rest of the text, sir.",
            "Sir, look at the chat screen for the complete answer."
        ]

        if len(Data) > 4 and len(Text) >= 250:
            TextToSpeech.TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
        else:
            TextToSpeech.TTS(Text, func)


if __name__ == "__main__":
    print(f"[info] Running in {AssistantGender} mode (Voice: {AssistantVoice})")
    TextToSpeech.DefaultMessage()
    while True:
        TextToSpeech.Speak(input("Enter the text : "))


#works well but it dont contain default message method

# import pygame
# import random
# import asyncio
# import edge_tts
# import os
# from dotenv import dotenv_values

# # Get the absolute path of the parent directory (MainFolder)
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# env_path = os.path.join(BASE_DIR, ".env")

# # Load .env from MainFolder
# env_vars = dotenv_values(env_path)
# AssistantGender = env_vars.get("AssistantGender", "Male")  # "Male" or "Female"

# # Voice map
# VOICE_MAP = {
#     "Male": "en-GB-RyanNeural",     # Young but serious (JARVIS style)
#     "Female": "en-US-AriaNeural"   # Cute, gentle, seductive (FRIDAY style)
# }
# AssistantVoice = VOICE_MAP.get(AssistantGender, "en-GB-RyanNeural")


# async def TextToAudioFile(text) -> None:
#     file_path = os.path.join(BASE_DIR, "Data", "speech.mp3")

#     # Ensure Data folder exists
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     if os.path.exists(file_path):
#         os.remove(file_path)

#     # Pitch & Rate depending on gender
#     if AssistantGender == "Male":
#         pitch = "-2Hz"   # deeper, serious
#         rate = "+2%"     # slower
#     else:  # Female
#         pitch = "+4Hz"   # softer, sweeter
#         rate = "+5%"     # slightly slower, gentle


#     communicate = edge_tts.Communicate(text, AssistantVoice, pitch=pitch, rate=rate)
#     await communicate.save(file_path)


# def TTS(Text, func=lambda r=None: True):
#     while True:
#         try:
#             asyncio.run(TextToAudioFile(Text))

#             pygame.mixer.init()
#             file_path = os.path.join(BASE_DIR, "Data", "speech.mp3")
#             pygame.mixer.music.load(file_path)
#             pygame.mixer.music.play()

#             clock = pygame.time.Clock()
#             while pygame.mixer.music.get_busy():
#                 if not func():
#                     break
#                 clock.tick(10)

#             return True
#         except Exception as e:
#             print(f"Error in TTS : {e}")

#         finally:
#             try:
#                 if pygame.mixer.get_init():
#                     func(False)
#                     pygame.mixer.music.stop()
#                     pygame.mixer.quit()
#             except Exception as e:
#                 print(f"Error in finally block: {e}")


# def TextToSpeech(Text, func=lambda r=None: True):
#     Data = str(Text).split(".")

#     responses = [
#         "The rest of the result has been printed to the chat screen, kindly check it out sir.",
#         "The rest of the text is now on the chat screen, sir, please check it.",
#         "You can see the rest of the text on the chat screen, sir.",
#         "The remaining part of the text is now on the chat screen, sir.",
#         "Sir, you'll find more text on the chat screen for you to see.",
#         "The rest of the answer is now on the chat screen, sir.",
#         "Sir, please look at the chat screen, the rest of the answer is there.",
#         "You'll find the complete answer on the chat screen, sir.",
#         "The next part of the text is on the chat screen, sir.",
#         "Sir, please check the chat screen for more information.",
#         "There's more text on the chat screen for you, sir.",
#         "Sir, take a look at the chat screen for additional text.",
#         "You'll find more to read on the chat screen, sir.",
#         "Sir, check the chat screen for the rest of the text.",
#         "The chat screen has the rest of the text, sir.",
#         "There's more to see on the chat screen, sir, please look.",
#         "Sir, the chat screen holds the continuation of the text.",
#         "You'll find the complete answer on the chat screen, kindly check it out sir.",
#         "Please review the chat screen for the rest of the text, sir.",
#         "Sir, look at the chat screen for the complete answer."
#     ]

#     if len(Data) > 4 and len(Text) >= 250:
#         TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
#     else:
#         TTS(Text, func)


# if __name__ == "__main__":
#     print(f"[info] Running in {AssistantGender} mode (Voice: {AssistantVoice})")
#     while True:
#         TextToSpeech(input("Enter the text : "))





# import pygame
# import random
# import asyncio
# import edge_tts
# import os
# from dotenv import dotenv_values

# # Get the absolute path of the parent directory (MainFolder)
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# env_path = os.path.join(BASE_DIR, ".env")

# # Load .env from MainFolder
# env_vars = dotenv_values(env_path)
# AssistantVoice = env_vars.get("AssistantVoice", "en-US-AriaNeural")  # fallback voice

# async def TextToAudioFile(text) -> None:
#     file_path = os.path.join(BASE_DIR, "Data", "speech.mp3")

#     # Ensure Data folder exists
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     if os.path.exists(file_path):
#         os.remove(file_path)

#     communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
#     await communicate.save(file_path)

# def TTS(Text, func=lambda r=None: True):
#     while True:
#         try:
#             asyncio.run(TextToAudioFile(Text))

#             pygame.mixer.init()
#             file_path = os.path.join(BASE_DIR, "Data", "speech.mp3")
#             pygame.mixer.music.load(file_path)
#             pygame.mixer.music.play()

#             clock = pygame.time.Clock()

#             while pygame.mixer.music.get_busy():
#                 if not func():
#                     break
#                 clock.tick(10)

#             return True
#         except Exception as e:
#             print(f"Error in TTS : {e}")

#         finally:
#             try:
#                 if pygame.mixer.get_init():
#                     func(False)
#                     pygame.mixer.music.stop()
#                     pygame.mixer.quit()
#             except Exception as e:
#                 print(f"Error in finally block: {e}")

# def TextToSpeech(Text, func=lambda r=None: True):
#     Data = str(Text).split(".")

    # responses = [
    #     "The rest of the result has been printed to the chat screen, kindly check it out sir.",
    #     "The rest of the text is now on the chat screen, sir, please check it.",
    #     "You can see the rest of the text on the chat screen, sir.",
    #     "The remaining part of the text is now on the chat screen, sir.",
    #     "Sir, you'll find more text on the chat screen for you to see.",
    #     "The rest of the answer is now on the chat screen, sir.",
    #     "Sir, please look at the chat screen, the rest of the answer is there.",
    #     "You'll find the complete answer on the chat screen, sir.",
    #     "The next part of the text is on the chat screen, sir.",
    #     "Sir, please check the chat screen for more information.",
    #     "There's more text on the chat screen for you, sir.",
    #     "Sir, take a look at the chat screen for additional text.",
    #     "You'll find more to read on the chat screen, sir.",
    #     "Sir, check the chat screen for the rest of the text.",
    #     "The chat screen has the rest of the text, sir.",
    #     "There's more to see on the chat screen, sir, please look.",
    #     "Sir, the chat screen holds the continuation of the text.",
    #     "You'll find the complete answer on the chat screen, kindly check it out sir.",
    #     "Please review the chat screen for the rest of the text, sir.",
    #     "Sir, look at the chat screen for the complete answer."
    # ]

#     if len(Data) > 4 and len(Text) >= 250:
#         TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
#     else:
#         TTS(Text, func)

# if __name__ == "__main__":
#     while True:
#         TextToSpeech(input("Enter the text : "))


