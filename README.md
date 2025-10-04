# 🌌 Omnis AI - The All-in-One AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>

> *"Omnis isn't just an assistant. Omnis is everything."* 🌌

Omnis AI (from Latin *"Omnis"* meaning *"all"*) is a revolutionary multi-functional AI powerhouse that transcends the limitations of conventional digital assistants. Unlike Siri, Alexa, or Google Assistant, Omnis is designed to be **limitless, extensible, and evolving** — a true attempt at building an all-encompassing AI companion that handles everything from voice commands to system automation, social media management to real-time information retrieval.

---

## 📑 Table of Contents

- [✨ Vision & Philosophy](#-vision--philosophy)
- [🎯 Key Features](#-key-features)
- [🏗️ Architecture & Workflow](#️-architecture--workflow)
- [🧩 Core Modules](#-core-modules)
- [📂 Project Structure](#-project-structure)
- [🔧 Tech Stack](#-tech-stack)
- [⚙️ Installation](#️-installation)
- [🚀 Usage](#-usage)
- [🖼️ User Interface](#️-user-interface)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Vision & Philosophy

Omnis AI was born from a singular vision: **to create a truly universal AI assistant that breaks all boundaries.**

### Core Principles:
- 🎙️ **Natural Interaction**: Understands voice commands and natural text queries seamlessly
- 🤖 **Universal Automation**: Automates both digital and real-world tasks effortlessly
- 🔌 **Infinite Extensibility**: Evolves continuously with new modules and integrations
- 🧠 **Contextual Intelligence**: Maintains memory and learns from interactions
- 🌐 **Bridge Everything**: Unifies personal productivity, automation, and intelligence into one ecosystem

Omnis AI is not just another tool — it's a personal AI companion that adapts, learns, and grows with you.

---

## 🎯 Key Features

### 🎤 Voice-Powered Intelligence
- Complete hands-free operation via voice commands
- Natural language understanding for intuitive interactions
- Real-time speech recognition and synthesis

### 🤖 Comprehensive Automation
- **System Control**: Open/close apps, switch tabs, adjust volume/brightness, take screenshots
- **Social Media Management**: Automate Instagram, Facebook, and YouTube interactions
- **Content Generation**: Create blog posts, captions, emails, and more
- **Real-Time Information**: Fetch latest news, weather, stock data, and trends

### 🧠 AI-Powered Core
- Advanced conversational AI using Groq API
- Context-aware responses with memory retention
- Smart query classification and routing
- AI-generated images and artwork

### 🔌 Modular Architecture
- Plug-and-play module system
- Easy to extend with custom functionality
- Independent, reusable components

---

## 🏗️ Architecture & Workflow

Omnis AI operates as a sophisticated modular pipeline where each component plays a crucial role in transforming user input into meaningful actions:

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                         │
│                  (Voice / Text Input)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              🎙️ SPEECH-TO-TEXT LAYER                        │
│          (Google Speech Recognition API)                     │
│     Converts voice commands into processable text            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           🧠 QUERY CLASSIFICATION ENGINE                     │
│                   (model.py - Cohere API)                    │
│   Analyzes and routes queries to appropriate modules         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              ⚡ MODULE EXECUTION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  Chat │ Social Media │ System │ Real-Time │ Image Gen       │
│       │  Automation  │ Control│   Data    │               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            🗣️ TEXT-TO-SPEECH LAYER                          │
│                 (Google TTS Library)                         │
│       Converts results into natural voice output             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              📂 MEMORY & DATA STORAGE                        │
│    Stores chat history, queries, and generated content       │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Breakdown:

1. **Input Layer**: User speaks or types a command
2. **Speech Recognition**: Voice is converted to text using Google Speech Recognition API
3. **Classification**: The query classifier (powered by Cohere API) analyzes the input and determines the appropriate module
4. **Execution**: The selected module processes the request and performs the action
5. **Output**: Results are converted back to speech via Google TTS and delivered to the user
6. **Memory**: All interactions are logged for context and future reference

---

## 🧩 Core Modules

### 1. 🎙️ Chatbot Module
**Technology**: Groq API
**File**: `chatbot_module.py`

The conversational heart of Omnis AI. Provides intelligent, context-aware responses to user queries.

**Capabilities**:
- Natural language conversations
- Question answering with reasoning
- Summarization and explanations
- Context retention across sessions
- Multi-turn dialogue handling
- Personality-driven responses

---

### 2. ✍️ Content Writing Module
**Technology**: Groq API
**File**: `content_writing_module.py`

Professional content generation for various purposes.

**Capabilities**:
- Blog post generation with SEO optimization
- Social media captions for all platforms
- Email drafting (professional and casual)
- Creative writing assistance
- Marketing copy and advertisements
- Technical documentation
- Article summarization and rewriting

---

### 3. 📺 YouTube Module
**Technology**: Selenium

Automates YouTube interactions and management.

**Capabilities**:
- Video search and playback
- Channel navigation
- Playlist management
- Future: Content scheduling and analytics

---

### 4. 📸 Instagram Module
**Technology**: Selenium/Playwright

Complete Instagram automation suite for social media management.

**Capabilities**:
- Automated login
- Post creation and publishing
- Liking and commenting
- Follow/unfollow operations
- Story management
- Marketing automation

---

### 5. 📘 Facebook Module
**Technology**: Selenium

Facebook automation tailored for the platform's unique features.

**Capabilities**:
- Post automation
- Messaging and communication
- Group management
- Page administration

---

### 6. 📈 Mero Lagani Share Market Module
**Technology**: Web scraping + Groq API
**Integration**: Mero Lagani (Leading Nepali Stock Market Platform)
**File**: `merolagani_module.py`

Specialized module for Nepali stock market analysis and tracking.

**Capabilities**:
- Real-time NEPSE stock data fetching
- Trend analysis for Nepali shares
- Portfolio tracking
- Market insights and summaries
- Foundation for AI-driven trading assistants
- Live market updates and news

---

### 7. 🌐 Real-Time Data Module
**Technology**: Groq API + Web Scraping (Google/Bing)
**Files**: `realtime_module.py`, `google_search.py`

Keeps Omnis connected to the real world with live information.

**Capabilities**:
- Latest news updates from multiple sources
- Weather information and forecasts
- Current trends and viral topics
- Live data fetching from the web
- Intelligent summarization of search results
- Multi-source verification
- Fact-checking capabilities

**How it works**: 
1. Searches Google/Bing for relevant information
2. Scrapes and parses results using BeautifulSoup
3. Uses Groq API to generate concise, accurate summaries
4. Filters and prioritizes most relevant information

---

### 8. 💻 System Automation Module
**Technology**: PyAutoGUI, Keyboard, OS libraries

One of the most powerful features — complete voice-powered system control.

**Capabilities**:
- **Application Management**: Open, close, switch applications
- **Window Control**: Minimize, maximize, restore windows
- **Browser Control**: Switch tabs by name
- **Volume Control**: Increase, decrease, mute, unmute
- **Brightness Adjustment**: Control screen brightness
- **Screenshots**: Capture screen on command
- **System Operations**: Lock, shutdown, restart
- **File Operations**: Open files and folders

*Essentially, Omnis becomes your voice-powered desktop manager.*

---

### 9. 🖼️ Image Generation Module
**Technology**: HuggingFace Inference API

AI-powered creative image generation.

**Capabilities**:
- Text-to-image generation
- Artistic rendering
- Custom visual creation
- Image storage and management in `/data` folder

---

### 10. 📧 Email Automation Module
**Status**: Planned
**Technology**: Gmail/Outlook API

Future email management capabilities.

**Planned Features**:
- Email drafting and sending
- Attachment handling
- Template management
- Scheduled emails

---

### 11. 💬 WhatsApp Automation Module
**Status**: Planned
**Technology**: Twilio/WhatsApp Business API

Future messaging automation.

**Planned Features**:
- Send WhatsApp messages
- Initiate calls
- Group message management
- Business automation

---

## 📂 Project Structure

```
OMNIS-AI/
│
├── 📄 main.py                           # Entry point - orchestrates all modules
│
├── 📁 backend/                          # Core intelligence & automation modules
│   ├── 🐍 chatbot_module.py             # Conversational AI (Groq API)
│   ├── 🐍 content_writing_module.py     # Content generation engine
│   ├── 🐍 core.py                       # Core functionality and utilities
│   ├── 🐍 facebook_module.py            # Facebook automation (Selenium)
│   ├── 🐍 google_search.py              # Google search integration
│   ├── 🐍 image_generation_module.py    # AI image generation (HuggingFace)
│   ├── 🐍 instagram_module.py           # Instagram automation (Selenium)
│   ├── 🐍 merolagani_module.py          # Nepali stock market integration
│   ├── 🐍 model.py                      # Query classification engine (Cohere API)
│   ├── 🐍 realtime_module.py            # Real-time data fetching & summarization
│   ├── 🐍 speech_to_text.py             # Voice input (Google Speech Recognition)
│   ├── 🐍 system_automation.py          # Complete system control module
│   ├── 🐍 text_to_speech.py             # Voice output (Google TTS)
│   └── 🐍 youtube_module.py             # YouTube automation
│
├── 📁 data/                             # Data storage and persistence
│   ├── 📁 content/                      # Generated content storage
│   ├── 📁 GeneratedImage/               # AI-generated images
│   ├── 📁 Screenshots/                  # System screenshots
│   └── 📄 ChatLog.json                  # Conversation history and memory
│
├── 📁 Frontend/                         # User interface layer
│   ├── 📁 __pycache__/                  # Python cache files
│   ├── 📁 data/                         # Frontend-specific data
│   ├── 📁 Files/                        # UI assets and resources
│   ├── 📁 Graphics/                     # Visual elements and icons
│   └── 🐍 GUI.py                        # Main graphical interface (PyQt5)
│
├── 🔒 .env                              # API keys and environment variables
├── 📄 requirements.txt                  # Python dependencies
└── 📄 README.md                         # This documentation
```

### File Descriptions

#### Backend Modules
- **chatbot_module.py**: Powers intelligent conversations using Groq's LLM API
- **content_writing_module.py**: Generates blogs, captions, and creative content
- **core.py**: Contains shared utilities and helper functions
- **facebook_module.py**: Automates Facebook posts, likes, and interactions
- **google_search.py**: Handles Google search queries and result parsing
- **image_generation_module.py**: Creates AI-generated artwork via HuggingFace
- **instagram_module.py**: Manages Instagram automation with Selenium
- **merolagani_module.py**: Fetches and analyzes Nepali stock market data
- **model.py**: Classifies user queries and routes to appropriate modules
- **realtime_module.py**: Fetches live news, weather, and trends
- **speech_to_text.py**: Converts voice commands to text
- **system_automation.py**: Controls system operations (apps, volume, brightness)
- **text_to_speech.py**: Converts text responses to natural speech
- **youtube_module.py**: Automates YouTube search and playback

#### Data Storage
- **content/**: Stores generated articles and written content
- **GeneratedImage/**: Archive of all AI-created images
- **Screenshots/**: System screenshots taken by voice command
- **ChatLog.json**: Complete conversation history with context

---

## 🔧 Tech Stack

### Core Technologies
- **Python 3.8+**: Primary development language
- **PyQt5**: Professional GUI framework

### AI & Language Models
- **Groq API**: Fast LLM for chat and content generation
- **Cohere API**: Query classification and routing
- **HuggingFace API**: AI image generation

### Speech Processing
- **Google Speech Recognition API**: Voice-to-text conversion
- **Google TTS (gTTS)**: Text-to-speech synthesis
- **pyttsx3**: Alternative TTS engine

### Web Automation
- **Selenium**: Browser automation for social media
- **Playwright**: Modern web automation
- **ChromeDriver**: Chrome browser control
- **BeautifulSoup**: Web scraping

### System Integration
- **PyAutoGUI**: GUI automation
- **Keyboard**: Keyboard control
- **OS Libraries**: System-level operations
- **Wikipedia API**: Knowledge base integration

### Additional Tools
- **Requests**: HTTP client for API calls
- **Python-dotenv**: Environment configuration
- **JSON**: Data serialization

---

## ⚙️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Chrome browser (for Selenium modules)
- Microphone (for voice input)

### Setup Steps

1. **Clone the Repository**
```bash
git clone https://github.com/Nabin68/Omnis-AI.git
cd Omnis-AI
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Keys**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
COHERE_API_KEY=your_cohere_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

4. **Install System Dependencies**
```bash
# For Linux/macOS
sudo apt-get install portaudio19-dev python3-pyaudio

# For Windows
# PyAudio wheels are included in requirements.txt
```

5. **Run Omnis AI**
```bash
python main.py
```

---

## 🚀 Usage

### Voice Commands
Simply speak naturally to Omnis. Examples:

```
"Hey Omnis, what's the weather today?"
"Open Chrome and search for Python tutorials"
"Post this on Instagram: [your caption]"
"Generate an image of a sunset over mountains"
"What's the latest news about AI?"
"Write me a blog post about machine learning"
"Check my stock portfolio"
"Take a screenshot"
"Increase volume"
```

### Text Commands
Type commands directly in the GUI for silent operation.

### System Control Examples
```
"Open Visual Studio Code"
"Switch to Chrome tab"
"Minimize all windows"
"Mute system"
"Set brightness to 50%"
"Lock my computer"
```

---

## 🖼️ User Interface

Omnis AI features two beautiful GUI options:

### Main Interface
*Full-featured dashboard with all controls and visualization*

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/5c3e9b8d-3fe7-432d-b6c4-84ea0a6a582f" />


### Mini Interface
*Compact, always-on-top interface for quick access*

<img width="453" height="705" alt="Screenshot 2025-10-04 134611" src="https://github.com/user-attachments/assets/11740a66-b204-4f8d-b325-413776eecedc" />


Both interfaces provide:
- Real-time status updates
- Voice waveform visualization
- Chat history
- Module status indicators
- Quick action buttons

---

## 🗺️ Roadmap

### 🎯 Phase 1: Core Enhancement (Current)
- ✅ Voice recognition and synthesis
- ✅ Multi-module architecture
- ✅ System automation
- ✅ Social media integration
- ✅ Real-time data fetching
- ✅ Dual GUI interface

### 🚀 Phase 2: Intelligence Upgrade (In Progress)
- [ ] Enhanced conversational memory
- [ ] Context-aware multi-turn dialogues
- [ ] Advanced query understanding
- [ ] Personalized recommendations
- [ ] Email automation integration
- [ ] WhatsApp automation

### 🌟 Phase 3: Expansion (Upcoming)
- [ ] Multi-language support (Nepali, Hindi, Spanish, etc.)
- [ ] Plugin ecosystem for community modules
- [ ] Analytics dashboard
- [ ] Cloud sync across devices
- [ ] Team collaboration features

### 📱 Phase 4: Mobile Revolution (Future)
- [ ] Android app development
- [ ] iOS app development
- [ ] Complete device automation on mobile
- [ ] Cross-platform synchronization
- [ ] Wearable device integration

### 🌐 Phase 5: Universal AI (Vision)
- [ ] IoT device control
- [ ] Smart home integration
- [ ] Automotive integration
- [ ] AR/VR interfaces
- [ ] True ubiquitous AI assistance

---

## 🤝 Contributing

Omnis AI is a passion project, but contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Contribution
- New module development
- Bug fixes and optimization
- Documentation improvements
- Testing and quality assurance
- UI/UX enhancements

---

## ⚡ Why Omnis is Unique

### vs. Traditional Assistants (Siri, Alexa, Google Assistant)

| Feature | Traditional Assistants | Omnis AI |
|---------|----------------------|----------|
| **Scope** | Limited to predefined commands | Limitless - covers everything from coding to social media |
| **Extensibility** | Closed ecosystem | Open, modular architecture |
| **Automation** | Basic tasks only | Complete system + web automation |
| **Intelligence** | Cloud-dependent | Hybrid with local processing |
| **Privacy** | Data sent to company servers | Local-first approach possible |
| **Customization** | Minimal | Fully customizable and extensible |
| **Learning** | Fixed functionality | Evolves with new modules |

### Key Differentiators
✅ **Limitless Scope**: Handles everything from code to communication  
✅ **Modular Design**: New features plug in seamlessly  
✅ **Context Awareness**: Learns and remembers interactions  
✅ **True Personalization**: Not restricted by corporate limitations  
✅ **Open Source**: Community-driven development  
✅ **Privacy-Focused**: You control your data  

---

## 💝 About

Omnis AI is a personal passion project built to push the boundaries of what an AI assistant can be. It combines automation, intelligence, and human-computer interaction into one unified ecosystem. This is an ongoing journey to create an AI companion that truly understands and assists with everything you need.

**Developer**: Nabin Kumar Rouniyar  
**Contact**: nabingupta68@gmail.com  
**Project Status**: Active Development  

---

## 🌟 Acknowledgments

- Groq for their blazing-fast LLM API
- Cohere for query classification capabilities
- HuggingFace for AI image generation
- The open-source community for incredible tools and libraries

---

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/Nabin68/Omnis-AI/issues)
- **Discussions**: [Join the community](https://github.com/Nabin68/Omnis-AI/discussions)
- **Email**: nabingupta68@gmail.com

---

<p align="center">
  <b>⭐ If you find Omnis AI interesting, please star this repository! ⭐</b>
</p>

<p align="center">
  Made with ❤️ and countless hours of coding
</p>

<p align="center">
  <i>"Omnis isn't just an assistant. Omnis is everything."</i> 🌌
</p>
