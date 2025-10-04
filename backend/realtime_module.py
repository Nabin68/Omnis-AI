# realtime-search.py
import os
import json
import time
import datetime
import traceback
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from groq import Groq

class RealtimeSearchModule:
    def __init__(self):
        # ---------- Find project root (omnis.ai) ----------
        self.BASE_DIR = self._find_project_root()
        print(f"[info] BASE_DIR detected: {self.BASE_DIR}")

        # ---------- Load .env ----------
        env_path = os.path.join(self.BASE_DIR, ".env")
        self.env = dotenv_values(env_path) if os.path.exists(env_path) else {}
        self.Username = self.env.get("Username", "User")
        self.Assistantname = self.env.get("Assistantname", "Assistant")
        self.GROQ_API_KEY = self.env.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not self.GROQ_API_KEY:
            raise ValueError("❌ No Groq API Key found. Put GROQ_API_KEY in .env")

        # ---------- Init Groq client ----------
        try:
            self.client = Groq(api_key=self.GROQ_API_KEY)
        except Exception as e:
            print("[error] Failed to initialize Groq client:", e)
            raise

        # ---------- Data folder & chatlog ----------
        self.data_dir = os.path.join(self.BASE_DIR, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.chatlog_path = os.path.join(self.data_dir, "ChatLog.json")
        self.messages = self._load_chatlog()

        # ---------- System message ----------
        self.system_message = (
            f"Hello, I am {self.Username}. You are a highly accurate and advanced AI chatbot named "
            f"{self.Assistantname} with access to real-time, up-to-date information from the internet.\n"
            "*** Provide a short, precise, and professional answer using proper grammar and punctuation. ***\n"
            "*** Use only the provided search results and real-time information. Do not include extra details unless necessary. ***\n"
            "*** Limit your answer to 1-2 concise sentences. ***"
        )

    def _find_project_root(self):
        """Find omnis.ai root folder"""
        try:
            start = os.path.abspath(os.path.dirname(__file__))
        except NameError:
            start = os.getcwd()
        path = start
        while True:
            if os.path.basename(path) == "omnis.ai" or (
                os.path.isdir(os.path.join(path, "backend")) and os.path.isdir(os.path.join(path, "data"))
            ):
                return path
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
        return os.path.abspath(os.path.join(start, ".."))

    def _load_chatlog(self):
        if os.path.exists(self.chatlog_path):
            try:
                with open(self.chatlog_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                print("[warning] Failed to parse chat log; starting fresh.")
                traceback.print_exc()
                try:
                    os.rename(self.chatlog_path, self.chatlog_path + ".broken")
                except Exception:
                    pass
        return []

    def bing_search(self, query, num_results=5):
        """Scrape Bing and return list of dicts {title, snippet}"""
        results_data = []
        chrome_options = Options()
        
        # Keep Chrome in background without headless mode
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Minimize window and prevent focus stealing
        chrome_options.add_argument("--window-position=-2400,-2400")  # Move window off-screen
        chrome_options.add_argument("--window-size=800,600")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        # Additional options to prevent focus
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")
        
        service = Service()
        driver = None

        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Minimize the window immediately after creation (backup method)
            try:
                driver.minimize_window()
            except:
                pass
            
            driver.get("https://www.bing.com")
            time.sleep(1.5)

            search_box = driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)

            results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
            for result in results[:num_results]:
                try:
                    title = result.find_element(By.TAG_NAME, "h2").text
                except:
                    title = "No title"
                try:
                    snippet = result.find_element(By.CSS_SELECTOR, "p").text.strip()
                except:
                    snippet = "No snippet"
                results_data.append({"title": title, "snippet": snippet})

        except Exception as e:
            print("[error] Bing scraping failed:", e)
            traceback.print_exc()
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        return results_data

    def get_datetime_info(self):
        now = datetime.datetime.now()
        return (
            f"Use This Real-time Information if needed:\n"
            f"Day: {now.strftime('%A')}\n"
            f"Date: {now.strftime('%d')}\n"
            f"Month: {now.strftime('%B')}\n"
            f"Year: {now.strftime('%Y')}\n"
            f"Time: {now.strftime('%H')} hours: {now.strftime('%M')} minutes: {now.strftime('%S')} seconds.\n"
        )

    def ask_groq(self, query, scraped_results):
        """Send query + scraped results + datetime to Groq"""
        search_context = "Search results (start):\n\n"
        for item in scraped_results:
            search_context += f"Title: {item['title']}\nSnippet: {item['snippet']}\n\n"
        search_context += "Search results (end)."

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "system", "content": search_context},
            {"role": "system", "content": self.get_datetime_info()},
            {"role": "user", "content": query},
        ]

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=512,
                temperature=0.0,
                top_p=1,
                stream=False,
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            print("[error] Groq API call failed:", e)
            traceback.print_exc()
            return "⚠️ Failed to get answer from Groq."

        # Save chat
        self.messages.append({"role": "user", "content": query})
        self.messages.append({"role": "assistant", "content": answer})
        try:
            with open(self.chatlog_path, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("[warning] Failed to save chat log:", e)
            traceback.print_exc()

        return answer

    def realtime_query(self, query, num_results=5):
        print(f"[info] Searching for: {query}")
        scraped = self.bing_search(query, num_results)
        print(f"[info] Retrieved {len(scraped)} result(s).")
        return self.ask_groq(query, scraped)


if __name__ == "__main__":
    engine = None
    try:
        engine = RealtimeSearchModule()
    except Exception as e:
        print("[fatal] Failed to initialize RealtimeSearchModule:", e)
        traceback.print_exc()
        raise SystemExit(1)

    print("RealtimeSearchModule ready. Type a query (Ctrl+C to exit).")
    while True:
        try:
            q = input("\nEnter your query: ").strip()
            if not q:
                continue
            result = engine.realtime_query(q, num_results=5)
            print("\n=== Answer ===\n")
            print(result)
            print("\n" + "="*60)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print("[error] Unexpected error while handling query:", e)
            traceback.print_exc()















