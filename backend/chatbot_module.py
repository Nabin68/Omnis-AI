import os
import json
import datetime
import requests
from dotenv import dotenv_values
from groq import Groq

class ChatBotEngine:
    def __init__(self):
        # ---------- Find project root ----------
        self.BASE_DIR = self._find_project_root()
        print(f"[info] BASE_DIR detected: {self.BASE_DIR}")

        # ---------- Load .env ----------
        env_path = os.path.join(self.BASE_DIR, ".env")
        if os.path.isfile(env_path):
            self.env = dotenv_values(env_path)
            print(f"[info] .env loaded from {env_path}")
        else:
            print("[warning] .env not found, trying environment variables")
            self.env = {}

        # ---------- Load credentials ----------
        self.Username = self.env.get("Username", os.environ.get("Username", "User"))
        self.Assistantname = self.env.get("Assistantname", os.environ.get("Assistantname", "Omnis"))
        self.GROQ_API_KEY = self.env.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))
        if not self.GROQ_API_KEY:
            raise ValueError("❌ No Groq API Key found. Set GROQ_API_KEY in .env or environment variables.")

        # ---------- Init Groq client ----------
        self.client = Groq(api_key=self.GROQ_API_KEY)

        # ---------- Data folder & chatlog ----------
        self.data_dir = os.path.join(self.BASE_DIR, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.chatlog_path = os.path.join(self.data_dir, "ChatLog.json")

        # Load or initialize chat log
        if os.path.exists(self.chatlog_path):
            try:
                with open(self.chatlog_path, "r", encoding="utf-8") as f:
                    self.messages = json.load(f)
            except Exception:
                print("[warning] Chat log exists but failed to parse; initializing empty chat log.")
                self.messages = []
        else:
            self.messages = []
            with open(self.chatlog_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

        # ---------- System prompt ----------
        self.system_message = f"""Hello, I am {self.Username}. You are a very accurate and advanced AI chatbot named {self.Assistantname} which has real-time up-to-date information from the internet.
            *** Do not tell time until asked. Answer concisely and professionally. ***
            *** Reply in English only. ***
            *** Use proper grammar and punctuation. Do not provide notes or mention training data. ***
            """
        self.system_chatbot = [{"role": "system", "content": self.system_message}]

    def _find_project_root(self):
        """Detect the main project directory (omnis.ai or parent folder containing data)."""
        path = os.getcwd()
        while True:
            if os.path.isdir(os.path.join(path, "data")):
                return path
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
        return os.getcwd()  # fallback

    def get_realtime_info(self):
        now = datetime.datetime.now()
        info = f"Please use this real-time information if needed:\n"
        info += f"Day: {now.strftime('%A')}\n"
        info += f"Date: {now.strftime('%d')}\n"
        info += f"Month: {now.strftime('%B')}\n"
        info += f"Year: {now.strftime('%Y')}\n"
        info += f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
        return info

    def answer_modifier(self, answer):
        lines = answer.split('\n')
        return '\n'.join([line for line in lines if line.strip()])

    def ask(self, query):
        try:
            # Load latest chat history
            if os.path.exists(self.chatlog_path):
                with open(self.chatlog_path, "r", encoding="utf-8") as f:
                    self.messages = json.load(f)

            self.messages.append({"role": "user", "content": query})

            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=self.system_chatbot + [{"role": "system", "content": self.get_realtime_info()}] + self.messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            answer = answer.replace("</s>", "").strip()
            self.messages.append({"role": "assistant", "content": answer})

            # Save chat log
            with open(self.chatlog_path, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, indent=4, ensure_ascii=False)

            return self.answer_modifier(answer)

        except requests.exceptions.RequestException as e:
            print(f"[error] Connection error: {e}")
            return "Connection error, please try again."
        except Exception as e:
            print(f"[error] Unexpected error: {e}")
            return "An error occurred, please try again."


if __name__ == "__main__":
    engine = ChatBotEngine()
    print("ChatBot ready. Type your question (Ctrl+C to exit).")
    while True:
        try:
            user_input = input("\nEnter Your Question: ").strip()
            if not user_input:
                continue
            response = engine.ask(user_input)
            print(response)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
