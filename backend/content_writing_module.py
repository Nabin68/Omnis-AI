import os
import platform
import subprocess
from pathlib import Path
from groq import Groq
from rich import print
from dotenv import dotenv_values


class ContentModule:
    def __init__(self):
        # Setup base directory
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"[info] BASE_DIR detected: {self.BASE_DIR}")

        # Load .env file
        env_path = os.path.join(self.BASE_DIR, ".env")
        if not os.path.exists(env_path):
            print(f"[warning] .env file not found at {env_path}")
            self.env = {}
        else:
            self.env = dotenv_values(env_path)
            print(f"[info] .env loaded from {env_path}")

        # Get configuration
        self.Username = self.env.get("Username", "User")
        self.Assistantname = self.env.get("Assistantname", "Assistant")
        self.GROQ_API_KEY = self.env.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        
        if not self.GROQ_API_KEY:
            raise ValueError("❌ No Groq API Key found. Put GROQ_API_KEY in .env")

        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.GROQ_API_KEY)
            print("[info] Groq client initialized successfully")
        except Exception as e:
            print(f"[error] Failed to initialize Groq client: {e}")
            raise

        # Updated system prompt for clean, runnable code
        self.system_prompt = f"""Hello, I am {self.Username}, a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, emails, articles, and more.

            IMPORTANT RULES FOR CODE:
            - When writing code, provide ONLY clean, runnable code
            - Put ALL explanations, overviews, and descriptions as comments within the code
            - DO NOT include markdown formatting like ```python or ### headings
            - DO NOT include separate explanation sections outside the code
            - The code should be immediately executable without any modifications
            - Use # comments for explanations, documentation, and notes
            - Include docstrings for functions and classes
            - Add inline comments to explain complex logic

            For non-code content (letters, emails, essays, poems):
            - Write in proper format without markdown code blocks
            - Make it clear, well-structured, and ready to use"""

    def generate_content(self, query: str) -> str:
        """Generate content using Groq API."""
        if not query or not query.strip():
            return "Error: Empty query provided"

        try:
            print(f"[info] Generating content for: {query}")
            
            # Create chat completion
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=2048,
                top_p=1,
                stream=True
            )

            # Collect streamed response
            content = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content

            content = content.strip()
            
            # Clean up markdown code blocks if AI still includes them
            content = self.clean_code_output(content)
            
            if content:
                print("[info] Content generated successfully")
                return content
            else:
                return "Error: Empty response from AI"

        except Exception as e:
            error_msg = f"Error: Unable to generate content - {str(e)}"
            print(f"[error] {error_msg}")
            return error_msg

    def clean_code_output(self, content: str) -> str:
        """Remove markdown code blocks and unnecessary formatting from code output."""
        lines = content.split('\n')
        cleaned_lines = []
        in_code_block = False
        
        for line in lines:
            # Skip markdown code block delimiters
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Skip markdown headers that aren't part of code
            if line.strip().startswith('###') or line.strip().startswith('####'):
                # Convert to comment if it looks important
                header_text = line.strip().lstrip('#').strip()
                if header_text and not in_code_block:
                    cleaned_lines.append(f"# {header_text}")
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def is_code(self, content: str, topic: str) -> tuple:
        """Detect if content is code and determine file extension."""
        topic_lower = topic.lower()
        
        # Check for code keywords in topic
        code_keywords = {
            'python': '.py',
            'java': '.java',
            'javascript': '.js',
            'typescript': '.ts',
            'html': '.html',
            'css': '.css',
            'c++': '.cpp',
            'c programming': '.c',
            'react': '.jsx',
            'php': '.php',
            'ruby': '.rb',
            'go': '.go',
            'rust': '.rs',
            'sql': '.sql',
            'bash': '.sh',
            'code': '.txt',
            'function': '.txt',
            'script': '.txt',
            'program': '.txt'
        }
        
        # Check topic for programming language
        for keyword, ext in code_keywords.items():
            if keyword in topic_lower:
                return True, ext
        
        # Check content for code patterns
        code_patterns = ['def ', 'function ', 'class ', 'import ', 'const ', 'let ', 
                        'var ', 'public ', 'private ', '#include', 'package ', '<?php']
        
        for pattern in code_patterns:
            if pattern in content[:200]:  # Check first 200 chars
                # Try to guess extension from content
                if 'def ' in content or 'import ' in content:
                    return True, '.py'
                elif 'function ' in content or 'const ' in content:
                    return True, '.js'
                elif 'public class' in content or 'private ' in content:
                    return True, '.java'
                else:
                    return True, '.txt'
        
        return False, '.txt'

    def save_and_open_content(self, content: str, topic: str) -> bool:
        """Save content to file and open in VS Code or Notepad."""
        try:
            # Navigate to data/content folder from backend
            # backend -> omnisai -> data -> content
            content_dir = Path(self.BASE_DIR) / "data" / "content"
            content_dir.mkdir(parents=True, exist_ok=True)
            print(f"[info] Content directory ready at: {content_dir}")

            # Detect if it's code
            is_code_content, file_ext = self.is_code(content, topic)

            # Create safe filename from topic
            clean_topic = topic.replace("content", "").strip()
            safe_filename = "".join(
                c for c in clean_topic.lower().replace(' ', '_') 
                if c.isalnum() or c in ('_', '-')
            )[:50]
            
            if not safe_filename:
                safe_filename = "generated_content"

            filepath = content_dir / f"{safe_filename}{file_ext}"

            # Write content to file
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"[info] Content saved to: {filepath}")

            # Open in VS Code if it's code, otherwise Notepad
            if is_code_content:
                self.open_vscode(str(filepath))
            else:
                self.open_notepad(str(filepath))
            return True

        except Exception as e:
            print(f"[error] Failed to save/open content: {e}")
            return False

    def open_vscode(self, filepath: str):
        """Open file in VS Code."""
        try:
            # Try to open in VS Code
            subprocess.run(["code", filepath], check=True)
            print(f"[info] Opened file in VS Code")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"[warning] VS Code not found, opening in default editor")
            self.open_notepad(filepath)

    def open_notepad(self, filepath: str):
        """Open file in Notepad (cross-platform)."""
        try:
            system = platform.system()
            
            if system == "Windows":
                os.startfile(filepath)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", filepath])
            else:  # Linux
                subprocess.run(["xdg-open", filepath])
                
            print(f"[info] Opened file in default editor")
        except Exception as e:
            print(f"[warning] Could not open file automatically: {e}")
            print(f"[info] File saved at: {filepath}")

    def content(self, query: str) -> bool:
        """Main function to generate and save content."""
        if not query or not query.strip():
            print("[warning] Empty query provided")
            return False

        # Generate content
        generated_content = self.generate_content(query)

        # Check if generation failed
        if generated_content.startswith("Error:"):
            print(f"[error] {generated_content}")
            return False

        # Save and open content
        success = self.save_and_open_content(generated_content, query)
        return success


# Usage example
if __name__ == "__main__":
    try:
        # Initialize the module
        writer = ContentModule()
        
        # Example queries
        queries = [
            "Write a Python function to calculate factorial",
            "Write a professional email requesting a meeting",
            "Write a short poem about nature"
        ]
        
        # Generate content for first query
        query = queries[1]
        print(f"\n[bold cyan]Processing query:[/bold cyan] {query}\n")
        writer.content(query)
        
    except Exception as e:
        print(f"[error] {e}")