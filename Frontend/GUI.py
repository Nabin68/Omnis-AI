from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QWidget, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,QSizePolicy, QScrollArea)
from PyQt5.QtGui import QIcon, QColor, QTextCursor, QFont, QPixmap, QPainter, QPainterPath, QMovie
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, QTime, QPoint
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "OmnisAI")
Username = env_vars.get("Username", "User")

# Directory paths
current_dir = os.getcwd()

# Handle both running from root directory and Frontend directory
if current_dir.endswith("Frontend"):
    TempDirPath = rf"{current_dir}\Files"
    GraphicsDirPath = rf"{current_dir}\Graphics"
    DataDirPath = rf"{current_dir}\data"
else:
    TempDirPath = rf"{current_dir}\Frontend\Files"
    GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"
    DataDirPath = rf"{current_dir}\Frontend\data"

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(DataDirPath, exist_ok=True)

# Global variables
old_chat_message = ""
current_display_text = ""
target_text = ""
char_index = 0
chat_history = []

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 'can you', 
                      "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
            Status = file.read().strip()
        return Status
    except:
        return "False"

def SetAsssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
            Status = file.read()
        return Status
    except:
        return ""

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path

def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def DataDirectoryPath(Filename):
    path = rf'{DataDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
        file.write(Text)

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

class AnimatedGIF(QLabel):
    """Widget to display animated GIFs"""
    def __init__(self, gif_path):
        super().__init__()
        self.movie = None
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.setMovie(self.movie)
            self.movie.start()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: transparent;")

class DigitalClock(QLabel):
    """Digital clock widget"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel {
                color: #4fc3f7;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Courier New', monospace;
                background-color: transparent;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        self.updateTime()
    
    def updateTime(self):
        current_time = QTime.currentTime()
        time_text = current_time.toString('hh:mm')
        self.setText(time_text)

class CompactChatWidget(QWidget):
    def __init__(self):
        super(CompactChatWidget, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        screen = QApplication.desktop().screenGeometry()
        self.compact_width = 450
        self.compact_height = 700
        self.setGeometry(screen.width() - self.compact_width - 20, 
                        screen.height() - self.compact_height - 60,
                        self.compact_width, self.compact_height)
        
        self.initUI()
        self.is_fullscreen = False
        self.mic_enabled = False
        
        self.loadChatHistory()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.loadMessages)
        self.update_timer.timeout.connect(self.checkQueryFile)
        self.update_timer.start(100)
        
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.typewriterEffect)
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1a1d2e;
                border: 2px solid #2a2f45;
                border-radius: 15px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        title_bar = self.createTitleBar()
        container_layout.addWidget(title_bar)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e2235;
                color: white;
                border: none;
                padding: 15px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e2235;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3a4057;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a5067;
            }
        """)
        container_layout.addWidget(self.chat_display, 1)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #7c8db0;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        input_container = self.createInputArea()
        container_layout.addWidget(input_container)
        
        main_layout.addWidget(self.container)
        
    def createTitleBar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("background-color: #1a1d2e; border-radius: 15px 15px 0 0;")
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 10, 0)
        
        icon_title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = DataDirectoryPath('ai_icon.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🤖")
            icon_label.setStyleSheet("font-size: 24px;")
        icon_title_layout.addWidget(icon_label)
        
        title_label = QLabel("OmnisAI")
        title_label.setStyleSheet("color: #e0e6f0; font-weight: 600; font-size: 16px; margin-left: 8px;")
        icon_title_layout.addWidget(title_label)
        
        layout.addLayout(icon_title_layout)
        layout.addStretch()
        
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(35, 35)
        minimize_btn.setStyleSheet(self.getButtonStyle("#3a4057", "#4a5067"))
        minimize_btn.clicked.connect(self.minimizeWidget)
        layout.addWidget(minimize_btn)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(35, 35)
        self.maximize_btn.setStyleSheet(self.getButtonStyle("#3a4057", "#4a5067"))
        self.maximize_btn.clicked.connect(self.toggleMaximize)
        layout.addWidget(self.maximize_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet(self.getButtonStyle("#d32f2f", "#b71c1c"))
        close_btn.clicked.connect(self.closeApplication)
        layout.addWidget(close_btn)
        
        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent
        
        return title_bar
    
    def createInputArea(self):
        input_widget = QWidget()
        input_widget.setStyleSheet("background-color: #1a1d2e; border-radius: 0 0 15px 15px;")
        layout = QHBoxLayout(input_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(50, 50)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2f45;
                color: white;
                border: 2px solid #3a4057;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #3a4057;
                border-color: #4a5067;
            }
            QPushButton:pressed {
                background-color: #1a1d2e;
            }
        """)
        self.mic_btn.clicked.connect(self.toggleMic)
        layout.addWidget(self.mic_btn)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2f45;
                color: white;
                border: 2px solid #3a4057;
                border-radius: 20px;
                padding: 12px 18px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4a7c9e;
            }
        """)
        self.text_input.returnPressed.connect(self.sendMessage)
        layout.addWidget(self.text_input)
        
        send_btn = QPushButton("▶")
        send_btn.setFixedSize(50, 50)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565c0;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        send_btn.clicked.connect(self.sendMessage)
        layout.addWidget(send_btn)
        
        return input_widget
    
    def createFullscreenLayout(self):
        """Create fullscreen landscape mode layout"""
        for i in reversed(range(self.container.layout().count())): 
            widget = self.container.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        main_h_layout = QHBoxLayout()
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)
        
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #1a1d2e;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        title_bar = self.createFullscreenTitleBar()
        left_layout.addWidget(title_bar)
        
        left_layout.addWidget(self.chat_display, 1)
        
        status_container = QWidget()
        status_container.setStyleSheet("background-color: #1a1d2e;")
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(20, 10, 20, 10)
        
        self.fullscreen_status = QLabel("Status: Online")
        self.fullscreen_status.setStyleSheet("color: #7c8db0; font-size: 12px;")
        status_layout.addWidget(self.fullscreen_status)
        status_layout.addStretch()
        
        left_layout.addWidget(status_container)
        
        input_area = self.createFullscreenInputArea()
        left_layout.addWidget(input_area)
        
        main_h_layout.addWidget(left_widget, 8)
        
        right_widget = self.createRightSidebar()
        main_h_layout.addWidget(right_widget, 2)
        
        self.container.layout().addLayout(main_h_layout)
    
    def createFullscreenTitleBar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("background-color: #1a1d2e;")
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 10, 0)
        
        icon_title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = DataDirectoryPath('ai_icon.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(35, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🤖")
            icon_label.setStyleSheet("font-size: 28px;")
        icon_title_layout.addWidget(icon_label)
        
        title_label = QLabel("OmnisAI")
        title_label.setStyleSheet("color: #e0e6f0; font-weight: 600; font-size: 20px; margin-left: 10px;")
        icon_title_layout.addWidget(title_label)
        
        layout.addLayout(icon_title_layout)
        layout.addStretch()
        
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(40, 40)
        minimize_btn.setStyleSheet(self.getButtonStyle("#3a4057", "#4a5067"))
        minimize_btn.clicked.connect(self.minimizeWidget)
        layout.addWidget(minimize_btn)
        
        restore_btn = QPushButton("◱")
        restore_btn.setFixedSize(40, 40)
        restore_btn.setStyleSheet(self.getButtonStyle("#3a4057", "#4a5067"))
        restore_btn.clicked.connect(self.toggleMaximize)
        layout.addWidget(restore_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet(self.getButtonStyle("#d32f2f", "#b71c1c"))
        close_btn.clicked.connect(self.closeApplication)
        layout.addWidget(close_btn)
        
        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent
        
        return title_bar
    
    def createFullscreenInputArea(self):
        input_widget = QWidget()
        input_widget.setStyleSheet("background-color: #1a1d2e;")
        layout = QHBoxLayout(input_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.fullscreen_mic_btn = QPushButton("🎤")
        self.fullscreen_mic_btn.setFixedSize(60, 60)
        self.fullscreen_mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2f45;
                color: white;
                border: 2px solid #4a7c9e;
                border-radius: 30px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #3a4057;
                border-color: #5a8cae;
            }
        """)
        self.fullscreen_mic_btn.clicked.connect(self.toggleMic)
        layout.addWidget(self.fullscreen_mic_btn)
        
        self.fullscreen_text_input = QLineEdit()
        self.fullscreen_text_input.setPlaceholderText("Type your message...")
        self.fullscreen_text_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2f45;
                color: white;
                border: 2px solid #3a4057;
                border-radius: 25px;
                padding: 15px 25px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4a7c9e;
            }
        """)
        self.fullscreen_text_input.returnPressed.connect(self.sendMessage)
        layout.addWidget(self.fullscreen_text_input)
        
        send_btn = QPushButton("▶")
        send_btn.setFixedSize(60, 60)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565c0;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        send_btn.clicked.connect(self.sendMessage)
        layout.addWidget(send_btn)
        
        return input_widget
    
    def createRightSidebar(self):
        """Create right sidebar with GIFs and clock"""
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #151824;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)
        
        gif1_path = DataDirectoryPath('gif1.gif')
        if os.path.exists(gif1_path):
            gif1 = AnimatedGIF(gif1_path)
            gif1.setFixedSize(280, 280)
            gif1_container = self.createGIFContainer(gif1, "Gaad Fad deb")
            right_layout.addWidget(gif1_container)
        else:
            placeholder1 = self.createPlaceholder("GIF", 300, 300)
            right_layout.addWidget(placeholder1)
        
        clock = DigitalClock()
        clock.setFixedHeight(100)
        right_layout.addWidget(clock)
        
        gif2_path = DataDirectoryPath('gif2.gif')
        if os.path.exists(gif2_path):
            gif2 = AnimatedGIF(gif2_path)
            gif2.setFixedSize(280, 280)
            gif2_container = self.createGIFContainer(gif2, "Ki rai hero")
            right_layout.addWidget(gif2_container)
        else:
            placeholder2 = self.createPlaceholder("GIF", 300, 300)
            right_layout.addWidget(placeholder2)
        
        right_layout.addStretch()
        
        hand_gif_path = DataDirectoryPath('gif3.gif')
        if os.path.exists(hand_gif_path):
            hand_gif = AnimatedGIF(hand_gif_path)
            hand_gif.setFixedSize(150, 150)
            right_layout.addWidget(hand_gif, alignment=Qt.AlignCenter)
        else:
            hand_placeholder = self.createPlaceholder("✋", 150, 150)
            right_layout.addWidget(hand_placeholder, alignment=Qt.AlignCenter)
        
        return right_widget
    
    def createGIFContainer(self, gif_widget, label_text):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #1e2235;
                border-radius: 15px;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(gif_widget, alignment=Qt.AlignCenter)
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #5a8cae; font-size: 11px; font-weight: 500;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        return container
    
    def createPlaceholder(self, text, width, height):
        placeholder = QLabel(text)
        placeholder.setFixedSize(width, height)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #1e2235;
                color: #5a8cae;
                border-radius: 15px;
                font-size: 48px;
            }
        """)
        placeholder.setAlignment(Qt.AlignCenter)
        return placeholder
    
    def getButtonStyle(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
    
    def toggleMic(self):
        self.mic_enabled = not self.mic_enabled
        
        mic_on_style = """
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: 2px solid #f44336;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """
        
        mic_off_style = """
            QPushButton {
                background-color: #2a2f45;
                color: white;
                border: 2px solid #3a4057;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #3a4057;
            }
        """
        
        if self.mic_enabled:
            self.mic_btn.setText("🔴")
            self.mic_btn.setStyleSheet(mic_on_style)
            if hasattr(self, 'fullscreen_mic_btn'):
                self.fullscreen_mic_btn.setText("🔴")
                fs_mic_style = mic_on_style.replace("25px", "30px").replace("20px", "24px")
                self.fullscreen_mic_btn.setStyleSheet(fs_mic_style)
            SetMicrophoneStatus("True")
            self.status_label.setText("🔴 Recording...")
        else:
            self.mic_btn.setText("🎤")
            self.mic_btn.setStyleSheet(mic_off_style)
            if hasattr(self, 'fullscreen_mic_btn'):
                self.fullscreen_mic_btn.setText("🎤")
                fs_mic_style = mic_off_style.replace("25px", "30px").replace("20px", "24px")
                self.fullscreen_mic_btn.setStyleSheet(fs_mic_style)
            SetMicrophoneStatus("False")
            self.status_label.setText("Ready")
    
    def sendMessage(self):
        if self.is_fullscreen and hasattr(self, 'fullscreen_text_input'):
            message = self.fullscreen_text_input.text().strip()
            self.fullscreen_text_input.clear()
        else:
            message = self.text_input.text().strip()
            self.text_input.clear()
        
        if message:
            with open(TempDirectoryPath('Query.data'), 'w', encoding='utf-8') as f:
                f.write(message)
    
    def checkQueryFile(self):
        """Check if there's a query from text input to process"""
        try:
            with open(TempDirectoryPath('Query.data'), 'r', encoding='utf-8') as f:
                query = f.read().strip()
            
            if query:
                with open(TempDirectoryPath('Query.data'), 'w', encoding='utf-8') as f:
                    f.write('')
        except:
            pass
    
    def loadChatHistory(self):
        """Load existing chat history on startup"""
        global chat_history, old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            
            if messages:
                chat_history = messages.split('\n')
                old_chat_message = messages
                self.displayChatHistory(messages)
        except FileNotFoundError:
            pass
    
    def displayChatHistory(self, messages):
        """Display chat history without typewriter effect"""
        self.chat_display.clear()
        html_content = self.formatMessages(messages)
        self.chat_display.setHtml(html_content)
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
    
    def formatMessages(self, text):
        """Format messages as HTML bubbles"""
        lines = text.split('\n')
        html_content = ""
        
        for line in lines:
            if line.strip():
                if line.startswith(f"{Username}:"):
                    content = line.replace(f"{Username}:", "").strip()
                    html_content += f"""
                        <div style='margin: 10px 0; text-align: left;'>
                            <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                                        color: white; padding: 12px 16px; border-radius: 18px 18px 18px 4px; 
                                        display: inline-block; max-width: 75%; box-shadow: 0 2px 8px rgba(0,0,0,0.3);'>
                                <span style='font-size: 10px; color: #b3d4fc; font-weight: 600;'>User</span><br>
                                <span style='font-size: 13px;'>{content}</span>
                            </div>
                        </div>
                    """
                elif line.startswith(f"{Assistantname}:") or line.startswith("OmnisAI:"):
                    content = line.replace(f"{Assistantname}:", "").replace("OmnisAI:", "").strip()
                    html_content += f"""
                        <div style='margin: 10px 0; text-align: right;'>
                            <div style='background: linear-gradient(135deg, #2a3f5f 0%, #3a5278 100%); 
                                        color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px; 
                                        display: inline-block; max-width: 75%; box-shadow: 0 2px 8px rgba(0,0,0,0.3);'>
                                <div style='display: flex; align-items: center; margin-bottom: 4px;'>
                                    <span style='background-color: #4a7c9e; color: white; font-size: 9px; 
                                                padding: 2px 8px; border-radius: 10px; font-weight: 600;'>AI</span>
                                </div>
                                <span style='font-size: 13px;'>{content}</span>
                            </div>
                        </div>
                    """
        
        return html_content
    
    def loadMessages(self):
        global old_chat_message, target_text, char_index
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            
            if messages and messages != old_chat_message:
                if len(messages) > len(old_chat_message):
                    target_text = messages
                    char_index = len(old_chat_message)
                    self.typewriter_timer.start(20)
                    old_chat_message = messages
                elif messages != old_chat_message:
                    old_chat_message = messages
                    self.displayChatHistory(messages)
            
            status = GetAssistantStatus()
            if status:
                self.status_label.setText(f"{status}")
                if hasattr(self, 'fullscreen_status'):
                    self.fullscreen_status.setText(f"Status: {status}")
        except FileNotFoundError:
            pass
    
    def typewriterEffect(self):
        global char_index, target_text
        
        if char_index < len(target_text):
            self.chat_display.clear()
            
            current_text = target_text[:char_index + 1]
            html_content = self.formatMessages(current_text)
            self.chat_display.setHtml(html_content)
            
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_display.setTextCursor(cursor)
            
            char_index += 1
        else:
            self.typewriter_timer.stop()
    
    def minimizeWidget(self):
        self.showMinimized()
    
    def toggleMaximize(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            screen = QApplication.desktop().screenGeometry()
            
            for i in reversed(range(self.container.layout().count())): 
                item = self.container.layout().itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
                elif item.layout():
                    self.clearLayout(item.layout())
            
            container_layout = QVBoxLayout(self.container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            
            title_bar = self.createTitleBar()
            container_layout.addWidget(title_bar)
            container_layout.addWidget(self.chat_display, 1)
            container_layout.addWidget(self.status_label)
            input_container = self.createInputArea()
            container_layout.addWidget(input_container)
            
            self.showNormal()
            self.setGeometry(screen.width() - self.compact_width - 20, 
                           screen.height() - self.compact_height - 60,
                           self.compact_width, self.compact_height)
            self.maximize_btn.setText("□")
        else:
            self.is_fullscreen = True
            self.showFullScreen()
            self.createFullscreenLayout()
    
    def clearLayout(self, layout):
        """Helper to clear a layout completely"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.clearLayout(item.layout())
    
    def closeApplication(self):
        SetMicrophoneStatus("False")
        QApplication.quit()
        os._exit(0)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

def GraphicalUserInterface():
    InitializeFiles()
    app = QApplication(sys.argv)
    window = CompactChatWidget()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    InitializeFiles()
    app = QApplication(sys.argv)
    window = CompactChatWidget()
    window.show()
    sys.exit(app.exec_())




















# from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QWidget, QLineEdit, 
#                              QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame)
# from PyQt5.QtGui import QIcon, QColor, QTextCursor, QFont, QPixmap
# from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
# from dotenv import dotenv_values
# import sys
# import os

# # Load environment variables
# env_vars = dotenv_values(".env")
# Assistantname = env_vars.get("Assistantname", "OmnisAI")
# Username = env_vars.get("Username", "User")

# # Directory paths
# current_dir = os.getcwd()

# # Handle both running from root directory and Frontend directory
# if current_dir.endswith("Frontend"):
#     TempDirPath = rf"{current_dir}\Files"
#     GraphicsDirPath = rf"{current_dir}\Graphics"
# else:
#     TempDirPath = rf"{current_dir}\Frontend\Files"
#     GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# # Ensure directories exist
# os.makedirs(TempDirPath, exist_ok=True)

# # Global variables
# old_chat_message = ""
# current_display_text = ""
# target_text = ""
# char_index = 0

# def AnswerModifier(Answer):
#     lines = Answer.split('\n')
#     non_empty_lines = [line.strip() for line in lines if line.strip()]
#     modified_answer = '\n'.join(non_empty_lines)
#     return modified_answer

# def QueryModifier(Query):
#     new_query = Query.lower().strip()
#     query_words = new_query.split()
#     question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 'can you', 
#                       "what's", "where's", "how's"]

#     if any(word + " " in new_query for word in question_words):
#         if query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "?"
#         else:
#             new_query += "?"
#     else:
#         if query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + '.'
#         else:
#             new_query += '.'
#     return new_query.capitalize()

# def SetMicrophoneStatus(Command):
#     with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
#         file.write(Command)

# def GetMicrophoneStatus():
#     try:
#         with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
#             Status = file.read().strip()
#         return Status
#     except:
#         return "False"

# def SetAsssistantStatus(Status):
#     with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
#         file.write(Status)

# def GetAssistantStatus():
#     try:
#         with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
#             Status = file.read()
#         return Status
#     except:
#         return ""

# def GraphicsDirectoryPath(Filename):
#     path = rf'{GraphicsDirPath}\{Filename}'
#     return path

# def TempDirectoryPath(Filename):
#     path = rf'{TempDirPath}\{Filename}'
#     return path

# def ShowTextToScreen(Text):
#     os.makedirs(TempDirPath, exist_ok=True)
#     with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
#         file.write(Text)

# def InitializeFiles():
#     """Initialize all required data files"""
#     os.makedirs(TempDirPath, exist_ok=True)
    
#     # Create required files if they don't exist
#     files_to_create = ['Mic.data', 'Status.data', 'Responses.data', 'Query.data']
    
#     for filename in files_to_create:
#         filepath = os.path.join(TempDirPath, filename)
#         if not os.path.exists(filepath):
#             with open(filepath, 'w', encoding='utf-8') as f:
#                 if filename == 'Mic.data':
#                     f.write('False')
#                 elif filename == 'Status.data':
#                     f.write('Ready')
#                 else:
#                     f.write('')

# class CompactChatWidget(QWidget):
#     def __init__(self):
#         super(CompactChatWidget, self).__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
#         self.setAttribute(Qt.WA_TranslucentBackground, False)
        
#         # Position in bottom-right corner
#         screen = QApplication.desktop().screenGeometry()
#         self.compact_width = 400
#         self.compact_height = 600
#         self.setGeometry(screen.width() - self.compact_width - 20, 
#                         screen.height() - self.compact_height - 60,
#                         self.compact_width, self.compact_height)
        
#         self.initUI()
#         self.is_minimized = False
#         self.mic_enabled = False
        
#         # Timer for updating messages
#         self.update_timer = QTimer(self)
#         self.update_timer.timeout.connect(self.loadMessages)
#         self.update_timer.timeout.connect(self.checkQueryFile)
#         self.update_timer.start(100)
        
#         # Timer for typewriter effect
#         self.typewriter_timer = QTimer(self)
#         self.typewriter_timer.timeout.connect(self.typewriterEffect)
        
#     def initUI(self):
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
        
#         # Container with border
#         container = QFrame()
#         container.setStyleSheet("""
#             QFrame {
#                 background-color: #1e1e1e;
#                 border: 2px solid #3a3a3a;
#                 border-radius: 10px;
#             }
#         """)
#         container_layout = QVBoxLayout(container)
#         container_layout.setContentsMargins(0, 0, 0, 0)
#         container_layout.setSpacing(0)
        
#         # Title bar
#         title_bar = self.createTitleBar()
#         container_layout.addWidget(title_bar)
        
#         # Chat area
#         self.chat_display = QTextEdit()
#         self.chat_display.setReadOnly(True)
#         self.chat_display.setStyleSheet("""
#             QTextEdit {
#                 background-color: #2d2d2d;
#                 color: white;
#                 border: none;
#                 padding: 10px;
#                 font-size: 12px;
#             }
#             QScrollBar:vertical {
#                 border: none;
#                 background: #2d2d2d;
#                 width: 8px;
#                 margin: 0px;
#             }
#             QScrollBar::handle:vertical {
#                 background: #5a5a5a;
#                 border-radius: 4px;
#             }
#         """)
#         container_layout.addWidget(self.chat_display, 1)
        
#         # Status label
#         self.status_label = QLabel("Ready")
#         self.status_label.setStyleSheet("""
#             QLabel {
#                 background-color: #252525;
#                 color: #888888;
#                 padding: 5px 10px;
#                 font-size: 10px;
#                 border-top: 1px solid #3a3a3a;
#             }
#         """)
#         container_layout.addWidget(self.status_label)
        
#         # Input area
#         input_container = self.createInputArea()
#         container_layout.addWidget(input_container)
        
#         main_layout.addWidget(container)
        
#     def createTitleBar(self):
#         title_bar = QWidget()
#         title_bar.setFixedHeight(40)
#         title_bar.setStyleSheet("background-color: #252525; border-radius: 10px 10px 0 0;")
        
#         layout = QHBoxLayout(title_bar)
#         layout.setContentsMargins(10, 0, 5, 0)
        
#         # Title
#         title_label = QLabel(f"🤖 OmnisAI")
#         title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
#         layout.addWidget(title_label)
        
#         layout.addStretch()
        
#         # Minimize button
#         minimize_btn = QPushButton("–")
#         minimize_btn.setFixedSize(30, 30)
#         minimize_btn.setStyleSheet(self.getButtonStyle())
#         minimize_btn.clicked.connect(self.minimizeWidget)
#         layout.addWidget(minimize_btn)
        
#         # Maximize/Restore button
#         self.maximize_btn = QPushButton("□")
#         self.maximize_btn.setFixedSize(30, 30)
#         self.maximize_btn.setStyleSheet(self.getButtonStyle())
#         self.maximize_btn.clicked.connect(self.toggleMaximize)
#         layout.addWidget(self.maximize_btn)
        
#         # Close button
#         close_btn = QPushButton("×")
#         close_btn.setFixedSize(30, 30)
#         close_btn.setStyleSheet(self.getButtonStyle("#d32f2f"))
#         close_btn.clicked.connect(self.closeApplication)
#         layout.addWidget(close_btn)
        
#         # Make title bar draggable
#         title_bar.mousePressEvent = self.mousePressEvent
#         title_bar.mouseMoveEvent = self.mouseMoveEvent
        
#         return title_bar
    
#     def createInputArea(self):
#         input_widget = QWidget()
#         input_widget.setStyleSheet("background-color: #252525; border-radius: 0 0 10px 10px;")
#         layout = QHBoxLayout(input_widget)
#         layout.setContentsMargins(10, 10, 10, 10)
        
#         # Mic button
#         self.mic_btn = QPushButton("🎤")
#         self.mic_btn.setFixedSize(40, 40)
#         self.mic_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #3a3a3a;
#                 color: white;
#                 border: none;
#                 border-radius: 20px;
#                 font-size: 18px;
#             }
#             QPushButton:hover {
#                 background-color: #4a4a4a;
#             }
#             QPushButton:pressed {
#                 background-color: #2a2a2a;
#             }
#         """)
#         self.mic_btn.clicked.connect(self.toggleMic)
#         layout.addWidget(self.mic_btn)
        
#         # Text input
#         self.text_input = QLineEdit()
#         self.text_input.setPlaceholderText("Type your message...")
#         self.text_input.setStyleSheet("""
#             QLineEdit {
#                 background-color: #3a3a3a;
#                 color: white;
#                 border: none;
#                 border-radius: 15px;
#                 padding: 10px 15px;
#                 font-size: 12px;
#             }
#         """)
#         self.text_input.returnPressed.connect(self.sendMessage)
#         layout.addWidget(self.text_input)
        
#         # Send button
#         send_btn = QPushButton("➤")
#         send_btn.setFixedSize(40, 40)
#         send_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #0d47a1;
#                 color: white;
#                 border: none;
#                 border-radius: 20px;
#                 font-size: 18px;
#             }
#             QPushButton:hover {
#                 background-color: #1565c0;
#             }
#         """)
#         send_btn.clicked.connect(self.sendMessage)
#         layout.addWidget(send_btn)
        
#         return input_widget
    
#     def getButtonStyle(self, hover_color="#4a4a4a"):
#         return f"""
#             QPushButton {{
#                 background-color: transparent;
#                 color: white;
#                 border: none;
#                 border-radius: 15px;
#                 font-size: 16px;
#                 font-weight: bold;
#             }}
#             QPushButton:hover {{
#                 background-color: {hover_color};
#             }}
#         """
    
#     def toggleMic(self):
#         self.mic_enabled = not self.mic_enabled
#         if self.mic_enabled:
#             self.mic_btn.setText("🔴")
#             self.mic_btn.setStyleSheet("""
#                 QPushButton {
#                     background-color: #d32f2f;
#                     color: white;
#                     border: none;
#                     border-radius: 20px;
#                     font-size: 18px;
#                 }
#                 QPushButton:hover {
#                     background-color: #b71c1c;
#                 }
#             """)
#             SetMicrophoneStatus("True")
#             self.status_label.setText("Microphone: ON")
#         else:
#             self.mic_btn.setText("🎤")
#             self.mic_btn.setStyleSheet("""
#                 QPushButton {
#                     background-color: #3a3a3a;
#                     color: white;
#                     border: none;
#                     border-radius: 20px;
#                     font-size: 18px;
#                 }
#                 QPushButton:hover {
#                     background-color: #4a4a4a;
#                 }
#             """)
#             SetMicrophoneStatus("False")
#             self.status_label.setText("Microphone: OFF")
    
#     def sendMessage(self):
#         message = self.text_input.text().strip()
#         if message:
#             # Write to query file for main.py to process
#             with open(TempDirectoryPath('Query.data'), 'w', encoding='utf-8') as f:
#                 f.write(message)
            
#             self.text_input.clear()
    
#     def checkQueryFile(self):
#         """Check if there's a query from text input to process"""
#         try:
#             with open(TempDirectoryPath('Query.data'), 'r', encoding='utf-8') as f:
#                 query = f.read().strip()
            
#             if query:
#                 # Clear the file after reading
#                 with open(TempDirectoryPath('Query.data'), 'w', encoding='utf-8') as f:
#                     f.write('')
#         except:
#             pass
    
#     def loadMessages(self):
#         global old_chat_message, target_text, char_index
#         try:
#             with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
#                 messages = file.read()
            
#             if messages and messages != old_chat_message:
#                 # Start typewriter effect for new message
#                 target_text = messages
#                 char_index = len(old_chat_message)
#                 self.typewriter_timer.start(20)
#                 old_chat_message = messages
            
#             # Update status
#             status = GetAssistantStatus()
#             if status:
#                 self.status_label.setText(f"{status}")
#         except FileNotFoundError:
#             pass
    
#     def typewriterEffect(self):
#         global char_index, target_text
        
#         if char_index < len(target_text):
#             self.chat_display.clear()
            
#             # Parse and display messages with animation
#             lines = target_text[:char_index + 1].split('\n')
#             html_content = ""
            
#             for line in lines:
#                 if line.strip():
#                     if line.startswith(f"{Username}:"):
#                         content = line.replace(f"{Username}:", "").strip()
#                         html_content += f"""
#                             <div style='text-align: left; margin: 10px 0;'>
#                                 <div style='background-color: #0d47a1; color: white; padding: 8px 12px; 
#                                             border-radius: 15px; display: inline-block; max-width: 70%;'>
#                                     <b>{Username}:</b> {content}
#                                 </div>
#                             </div>
#                         """
#                     elif line.startswith(f"{Assistantname}:") or line.startswith("OmnisAI:"):
#                         content = line.replace(f"{Assistantname}:", "").replace("OmnisAI:", "").strip()
#                         html_content += f"""
#                             <div style='text-align: right; margin: 10px 0;'>
#                                 <div style='background-color: #2e7d32; color: white; padding: 8px 12px; 
#                                             border-radius: 15px; display: inline-block; max-width: 70%;'>
#                                     <b>OmnisAI:</b> {content}
#                                 </div>
#                             </div>
#                         """
            
#             self.chat_display.setHtml(html_content)
            
#             # Scroll to bottom
#             cursor = self.chat_display.textCursor()
#             cursor.movePosition(QTextCursor.End)
#             self.chat_display.setTextCursor(cursor)
            
#             char_index += 1
#         else:
#             self.typewriter_timer.stop()
    
#     def minimizeWidget(self):
#         self.showMinimized()
    
#     def toggleMaximize(self):
#         if self.isFullScreen():
#             # Return to compact mode
#             screen = QApplication.desktop().screenGeometry()
#             self.showNormal()
#             self.setGeometry(screen.width() - self.compact_width - 20, 
#                            screen.height() - self.compact_height - 60,
#                            self.compact_width, self.compact_height)
#             self.maximize_btn.setText("□")
#         else:
#             # Go fullscreen
#             self.showFullScreen()
#             self.maximize_btn.setText("◱")
    
#     def closeApplication(self):
#         SetMicrophoneStatus("False")
#         QApplication.quit()
#         os._exit(0)
    
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
#             event.accept()
    
#     def mouseMoveEvent(self, event):
#         if event.buttons() == Qt.LeftButton:
#             self.move(event.globalPos() - self.drag_position)
#             event.accept()

# def GraphicalUserInterface():
#     InitializeFiles()
#     app = QApplication(sys.argv)
#     window = CompactChatWidget()
#     window.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = CompactChatWidget()
#     window.show()
#     sys.exit(app.exec_())

















