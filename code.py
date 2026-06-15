import sys
import json
import sqlite3
import threading
import subprocess
import hashlib
import hmac
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import speech_recognition as sr
import pyttsx3

# PyAudio is optional - try to import but fall back gracefully
try:
    import pyaudio  
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not available. Microphone input may not work.")
    print("To fix: Install Microsoft C++ Build Tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/")
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QLabel, QDialog, QFormLayout, QComboBox, QMessageBox, QSlider,
    QCheckBox, QListWidget, QListWidgetItem, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QColor, QIcon, QFont


class VoiceListenerThread(QThread):
    """Thread for listening to voice commands without blocking UI"""
    command_recognized = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()

    def __init__(self, language="en-US"):
        super().__init__()
        self.is_running = False
        self.language = language
        self.recognizer = sr.Recognizer()
        
        # Check if microphone is available
        if not PYAUDIO_AVAILABLE:
            self.microphone = None
        else:
            try:
                self.microphone = sr.Microphone()
            except Exception as e:
                self.microphone = None
                print(f"Microphone initialization failed: {e}")

    def run(self):
        """Main listening loop"""
        if not self.microphone:
            self.error_occurred.emit("Microphone not available. Please install PyAudio with C++ Build Tools.")
            return
            
        self.is_running = True
        self.listening_started.emit()
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            self.error_occurred.emit(f"Microphone initialization failed: {str(e)}")
            self.is_running = False
            return
            
        while self.is_running:
            try:
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=5)
                        
                        try:
                            command = self.recognizer.recognize_google(audio, language=self.language)
                            self.command_recognized.emit(command.lower())
                        except sr.UnknownValueError:
                            pass  # Silently skip unrecognized audio
                        except sr.RequestError as e:
                            self.error_occurred.emit(f"API error: {str(e)}")
                    except sr.WaitTimeoutError:
                        pass  # Silently skip timeout - continue listening
                    except sr.RequestError as e:
                        self.error_occurred.emit(f"Microphone error: {str(e)}")
                        # Continue listening instead of breaking
                        
            except Exception as e:
                if self.is_running:
                    self.error_occurred.emit(f"Error: {str(e)}")

    def stop(self):
        """Stop listening"""
        self.is_running = False
        self.listening_stopped.emit()


class CommandDatabase:
    """Manage voice commands database"""
    
    def __init__(self, db_path="voice_commands.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Commands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voice_trigger TEXT UNIQUE NOT NULL,
                    application_path TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # History table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success'
                )
            ''')
            
            conn.commit()

    def add_command(self, voice_trigger, app_path, description=""):
        """Add a new voice command"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO commands (voice_trigger, application_path, description) VALUES (?, ?, ?)',
                    (voice_trigger.lower(), app_path, description)
                )
                conn.commit()
            return True, "Command added successfully"
        except sqlite3.IntegrityError:
            return False, "This voice trigger already exists"
        except Exception as e:
            return False, str(e)

    def remove_command(self, command_id):
        """Remove a voice command"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM commands WHERE id = ?', (command_id,))
                conn.commit()
            return True, "Command removed successfully"
        except Exception as e:
            return False, str(e)

    def get_all_commands(self):
        """Get all commands"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, voice_trigger, application_path, description FROM commands ORDER BY created_at DESC')
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching commands: {e}")
            return []

    def get_history(self, limit=50):
        """Get execution history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT command, executed_at, status FROM history ORDER BY executed_at DESC LIMIT ?',
                    (limit,)
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []

    def add_history(self, command, status="success"):
        """Log command execution"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO history (command, status) VALUES (?, ?)',
                    (command, status)
                )
                conn.commit()
        except Exception as e:
            print(f"Error adding history: {e}")

    def update_command(self, command_id, voice_trigger, app_path, description=""):
        """Update an existing command"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE commands SET voice_trigger = ?, application_path = ?, description = ? WHERE id = ?',
                    (voice_trigger.lower(), app_path, description, command_id)
                )
                conn.commit()
            return True, "Command updated successfully"
        except sqlite3.IntegrityError:
            return False, "This voice trigger already exists"
        except Exception as e:
            return False, str(e)


class AddCommandDialog(QDialog):
    """Dialog to add or edit a voice command"""
    
    def __init__(self, parent=None, command_data=None):
        super().__init__(parent)
        self.command_data = command_data
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())

    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Add Voice Command" if not self.command_data else "Edit Voice Command")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout()
        
        self.voice_input = QLineEdit()
        self.app_input = QLineEdit()
        self.desc_input = QLineEdit()
        
        if self.command_data:
            self.voice_input.setText(self.command_data[1])
            self.app_input.setText(self.command_data[2])
            self.desc_input.setText(self.command_data[3] or "")
        
        layout.addRow("Voice Trigger:", self.voice_input)
        layout.addRow("Application Path:", self.app_input)
        layout.addRow("Description:", self.desc_input)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)

    def get_stylesheet(self):
        return """
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d7;
            }
        """


FIREBASE_API_KEY = "AIzaSyA5PQ2AQRLDqibkdQ_tiDz0cgZnLRZy03M"
FIREBASE_PROJECT_ID = "hash-code-ai-reg"
FIRESTORE_COLLECTION = "access_control"
FIRESTORE_DOCUMENT = "app_hash"
FIRESTORE_FIELD = "hash"
FIRESTORE_URL = (
    f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}"
    f"/databases/(default)/documents/{FIRESTORE_COLLECTION}/{FIRESTORE_DOCUMENT}"
    f"?mask.fieldPaths={FIRESTORE_FIELD}&key={FIREBASE_API_KEY}"
)


def fetch_firebase_hash():
    """Fetch the stored password hash from Firestore."""
    try:
        request = urllib.request.Request(FIRESTORE_URL, method="GET")
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)

            fields = data.get("fields", {})
            if FIRESTORE_FIELD not in fields:
                raise ValueError("Hash field missing")

            field_value = fields[FIRESTORE_FIELD]
            if "stringValue" in field_value:
                return field_value["stringValue"]
            if "bytesValue" in field_value:
                return field_value["bytesValue"]

            raise ValueError("Unsupported hash format")
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            error_body = ""
        print(f"Firebase HTTP error {e.code}: {error_body}")
        raise ConnectionError("Firebase connection failed") from e
    except urllib.error.URLError as e:
        print(f"Firebase URL error: {e.reason}")
        raise ConnectionError("Firebase connection failed") from e
    except Exception as e:
        print(f"Firebase fetch error: {e}")
        raise ConnectionError("Firebase connection failed") from e


def hash_password(password, stored_hash):
    """Hash the entered password using the same method as the stored hash."""
    # If stored hash uses PBKDF2, compute PBKDF2 hex to compare with stored derived value
    if stored_hash.startswith("pbkdf2_sha256$"):
        parts = stored_hash.split("$")
        if len(parts) == 4:
            _, iterations, salt, expected = parts
            try:
                iterations = int(iterations)
                derived = hashlib.pbkdf2_hmac(
                    "sha256",
                    password.encode("utf-8"),
                    salt.encode("utf-8"),
                    iterations,
                ).hex()
                return derived
            except Exception:
                # Fall back to simple sha256 if pbkdf2 computation fails
                return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # For sha256$prefix or raw hex stored values, return plain hex digest
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, stored_hash):
    """Safely verify the entered password against the stored hash."""
    try:
        # Handle PBKDF2 stored values separately (stored format: pbkdf2_sha256$<iters>$<salt>$<derived>)
        if stored_hash.startswith("pbkdf2_sha256$"):
            parts = stored_hash.split("$")
            if len(parts) == 4:
                _, iterations, salt, expected = parts
                computed = hashlib.pbkdf2_hmac(
                    "sha256",
                    password.encode("utf-8"),
                    salt.encode("utf-8"),
                    int(iterations),
                ).hex()
                return hmac.compare_digest(computed, expected)

        # Normalize stored hash: strip optional "sha256$" prefix
        if stored_hash.startswith("sha256$"):
            stored_hex = stored_hash.split("$", 1)[1]
        else:
            stored_hex = stored_hash

        computed = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # If the stored hash is a truncated prefix of the full hex (testing convenience),
        # compare only the prefix length using constant-time comparison.
        if len(stored_hex) < len(computed):
            return hmac.compare_digest(computed[: len(stored_hex)], stored_hex)
        else:
            return hmac.compare_digest(computed, stored_hex)
    except Exception:
        return False


class PasswordUnlockDialog(QDialog):
    """Password dialog shown before the main application opens."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unlock Luxify Assistant")
        self.setModal(True)
        self.setGeometry(100, 100, 420, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Enter access password")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.on_submit)
        layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff5555;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        button_layout = QHBoxLayout()
        unlock_btn = QPushButton("Unlock")
        unlock_btn.clicked.connect(self.on_submit)
        cancel_btn = QPushButton("Exit")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(unlock_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def show_error(self, message):
        self.error_label.setText(message)

    def on_submit(self):
        password = self.password_input.text().strip()
        if not password:
            self.show_error("Please enter the password")
            return

        try:
            stored_hash = fetch_firebase_hash()
            if verify_password(password, stored_hash):
                self.accept()
            else:
                self.show_error("Incorrect password")
        except ConnectionError:
            self.show_error("Firebase connection failed")
        except Exception:
            self.show_error("Firebase connection failed")

    def get_stylesheet(self):
        return """
            QDialog {
                background-color: #0d1117;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d7;
            }
        """


class VoiceAIApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db = CommandDatabase()
        self.voice_thread = None
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.is_listening = False
        self.selected_language = "en-US"
        self.language_names = {
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Russian": "ru-RU",
            "Hebrew": "he-IL",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "German": "de-DE",
            "Arabic": "ar-SA",
            "Portuguese": "pt-PT",
            "Chinese (Simplified)": "zh-CN",
            "Japanese": "ja-JP",
        }
        
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())
        self.setWindowTitle("Luxify Assistant - Voice Control AI")
        self.setGeometry(100, 100, 1200, 700)

    def init_ui(self):
        """Initialize main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # Create tab widget first
        self.tab_widget = self.create_content_area()
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Main content
        main_layout.addWidget(self.tab_widget, 1)
        
        central_widget.setLayout(main_layout)

    def create_sidebar(self):
        """Create left sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setMaximumWidth(200)
        sidebar.setStyleSheet("background-color: #0d1117; border-right: 1px solid #30363d;")
        
        layout = QVBoxLayout()
        
        # Logo
        logo_label = QLabel("🎤 Luxify")
        logo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        layout.addSpacing(30)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", 0),
            ("📝 Commands", 1),
            ("⚙️ Settings", 2),
            ("📊 History", 3),
            ("🔍 Explorer", 4),
        ]
        
        for i, (text, idx) in enumerate(nav_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, x=idx: self.tab_widget.setCurrentIndex(x))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        sidebar.setLayout(layout)
        return sidebar

    def create_content_area(self):
        """Create main content area with tabs"""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { display: none; }
        """)
        
        # Home Tab
        tab_widget.addTab(self.create_home_tab(), "Home")
        
        # Commands Tab
        tab_widget.addTab(self.create_commands_tab(), "Commands")
        
        # Settings Tab
        tab_widget.addTab(self.create_settings_tab(), "Settings")
        
        # History Tab
        tab_widget.addTab(self.create_history_tab(), "History")
        
        # Explorer Tab
        tab_widget.addTab(self.create_explorer_tab(), "Explorer")
        
        return tab_widget

    def create_home_tab(self):
        """Create home/main tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("ОСНОВНОЕ ОКНО")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Status section
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 8px; padding: 15px;")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready to listen")
        self.status_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(self.status_label)
        
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
        # Listen button
        self.listen_btn = QPushButton("🎤 Start Listening")
        self.listen_btn.setMinimumHeight(60)
        self.listen_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.listen_btn.clicked.connect(self.toggle_listening)
        layout.addWidget(self.listen_btn)
        
        # Recent commands
        recent_label = QLabel("Recent Commands")
        recent_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(200)
        layout.addWidget(self.recent_list)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def create_commands_tab(self):
        """Create commands management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Voice Commands")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Commands table
        self.commands_table = QTableWidget()
        self.commands_table.setColumnCount(4)
        self.commands_table.setHorizontalHeaderLabels(["Voice Trigger", "Application", "Description", "Actions"])
        self.commands_table.horizontalHeader().setStretchLastSection(False)
        layout.addWidget(self.commands_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Command")
        add_btn.clicked.connect(self.add_command)
        button_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_commands_table)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        self.refresh_commands_table()
        
        return widget

    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Control Panel")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 8px; padding: 15px;")
        settings_layout = QVBoxLayout()
        
        # Prefix mode
        prefix_layout = QHBoxLayout()
        self.prefix_checkbox = QCheckBox("Enable Prefix Mode")
        self.prefix_checkbox.setChecked(False)
        prefix_layout.addWidget(self.prefix_checkbox)
        prefix_layout.addStretch()
        settings_layout.addLayout(prefix_layout)
        
        # Quiet mode
        quiet_layout = QHBoxLayout()
        self.quiet_checkbox = QCheckBox("Quiet Mode (No Audio Feedback)")
        self.quiet_checkbox.setChecked(False)
        quiet_layout.addWidget(self.quiet_checkbox)
        quiet_layout.addStretch()
        settings_layout.addLayout(quiet_layout)
        
        # Speech recognition language
        language_layout = QHBoxLayout()
        language_label = QLabel("Recognition Language:")
        self.language_combo = QComboBox()
        for name in self.language_names:
            self.language_combo.addItem(name)
        self.language_combo.setCurrentText("English (US)")
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        settings_layout.addLayout(language_layout)
        
        # Avatar animation
        avatar_layout = QHBoxLayout()
        self.avatar_checkbox = QCheckBox("Avatar Animation")
        self.avatar_checkbox.setChecked(True)
        avatar_layout.addWidget(self.avatar_checkbox)
        avatar_layout.addStretch()
        settings_layout.addLayout(avatar_layout)
        
        # Window always on top
        ontop_layout = QHBoxLayout()
        self.ontop_checkbox = QCheckBox("Window Always on Top")
        self.ontop_checkbox.setChecked(False)
        ontop_layout.addWidget(self.ontop_checkbox)
        ontop_layout.addStretch()
        settings_layout.addLayout(ontop_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        volume_value = QLabel("80%")
        self.volume_slider.sliderMoved.connect(lambda v: volume_value.setText(f"{v}%"))
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(volume_value)
        settings_layout.addLayout(volume_layout)
        
        settings_frame.setLayout(settings_layout)
        layout.addWidget(settings_frame)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def create_history_tab(self):
        """Create history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Execution History")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Command", "Executed At", "Status"])
        layout.addWidget(self.history_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_history_table)
        button_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        self.refresh_history_table()
        
        return widget

    def create_explorer_tab(self):
        """Create command explorer tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Command Explorer")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.explorer_search = QLineEdit()
        self.explorer_search.setPlaceholderText("Search commands...")
        self.explorer_search.textChanged.connect(self.filter_explorer)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.explorer_search)
        layout.addLayout(search_layout)
        
        # Explorer list
        self.explorer_list = QListWidget()
        layout.addWidget(self.explorer_list)
        
        # Action buttons
        action_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.clicked.connect(self.edit_from_explorer)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.clicked.connect(self.delete_from_explorer)
        action_layout.addWidget(delete_btn)
        
        test_btn = QPushButton("▶️ Test Command")
        test_btn.clicked.connect(self.test_command)
        action_layout.addWidget(test_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        widget.setLayout(layout)
        self.refresh_explorer()
        
        return widget

    def toggle_listening(self):
        """Toggle voice listening"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        """Start listening for voice commands"""
        if self.is_listening:
            return  # Already listening
            
        self.is_listening = True
        self.listen_btn.setText("🎤 Stop Listening")
        self.listen_btn.setStyleSheet("background-color: #d13438;")
        self.status_label.setText("Listening...")
        
        self.voice_thread = VoiceListenerThread(language=self.selected_language)
        self.voice_thread.command_recognized.connect(self.on_command_recognized)
        self.voice_thread.error_occurred.connect(self.on_error)
        self.voice_thread.listening_stopped.connect(self.on_listening_stopped)
        self.voice_thread.start()

    def stop_listening(self):
        """Stop listening for voice commands"""
        if not self.is_listening:
            return  # Already stopped
            
        self.is_listening = False
        if self.voice_thread:
            self.voice_thread.stop()
            self.voice_thread.wait(2000)  # Wait for thread to finish
        self.listen_btn.setText("🎤 Start Listening")
        self.listen_btn.setStyleSheet("")
        self.status_label.setText("Ready to listen")

    def on_command_recognized(self, command):
        """Handle recognized command"""
        self.status_label.setText(f"Recognized: {command}")
        
        # Check if command matches any trigger
        commands = self.db.get_all_commands()
        matched = False
        for cmd_id, trigger, app_path, desc in commands:
            if trigger.lower() in command.lower():
                self.execute_command(cmd_id, trigger, app_path)
                matched = True
                break
        
        if not matched:
            self.status_label.setText(f"No command found for: {command}")

    def on_error(self, error):
        """Handle voice recognition error"""
        if error:
            self.status_label.setText(f"Error: {error}")

    def on_listening_stopped(self):
        """Handle listening stopped"""
        if not self.is_listening:
            self.listen_btn.setText("🎤 Start Listening")
            self.listen_btn.setStyleSheet("")

    def execute_command(self, cmd_id, trigger, app_path):
        """Execute a command"""
        try:
            subprocess.Popen(app_path, shell=True)
            self.db.add_history(trigger, "success")
            self.status_label.setText(f"Executed: {trigger}")
            
            # Speak feedback in background thread
            if not self.quiet_checkbox.isChecked():
                tts_thread = threading.Thread(target=self._speak_feedback, args=(trigger,), daemon=True)
                tts_thread.start()
            
            # Update recent list
            self.update_recent_list(trigger)
            self.refresh_history_table()
            
        except Exception as e:
            self.db.add_history(trigger, "failed")
            self.status_label.setText(f"Failed: {str(e)}")

    def _speak_feedback(self, trigger):
        """Speak feedback in background thread"""
        try:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 150)
            tts_engine.say(f"Launching {trigger}")
            tts_engine.runAndWait()
            del tts_engine
        except Exception as e:
            print(f"TTS error: {e}")

    def update_recent_list(self, command):
        """Update recent commands list"""
        self.recent_list.insertItem(0, f"✓ {command} - {datetime.now().strftime('%H:%M:%S')}")
        if self.recent_list.count() > 5:
            self.recent_list.takeItem(self.recent_list.count() - 1)

    def add_command(self):
        """Add new command"""
        dialog = AddCommandDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            voice_trigger = dialog.voice_input.text().strip()
            app_path = dialog.app_input.text().strip()
            description = dialog.desc_input.text().strip()
            
            if voice_trigger and app_path:
                success, message = self.db.add_command(voice_trigger, app_path, description)
                QMessageBox.information(self, "Success" if success else "Error", message)
                self.refresh_commands_table()
                self.refresh_explorer()
            else:
                QMessageBox.warning(self, "Error", "Please fill in all required fields")

    def edit_from_explorer(self):
        """Edit command from explorer"""
        current_item = self.explorer_list.currentItem()
        if current_item:
            # Parse command data from item
            commands = self.db.get_all_commands()
            text = current_item.text()
            for cmd_data in commands:
                if cmd_data[1] in text:
                    dialog = AddCommandDialog(self, cmd_data)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        voice_trigger = dialog.voice_input.text().strip()
                        app_path = dialog.app_input.text().strip()
                        description = dialog.desc_input.text().strip()
                        
                        success, message = self.db.update_command(cmd_data[0], voice_trigger, app_path, description)
                        QMessageBox.information(self, "Success" if success else "Error", message)
                        self.refresh_commands_table()
                        self.refresh_explorer()
                    break
        else:
            QMessageBox.warning(self, "Error", "Please select a command to edit")

    def delete_from_explorer(self):
        """Delete command from explorer"""
        current_item = self.explorer_list.currentItem()
        if current_item:
            commands = self.db.get_all_commands()
            text = current_item.text()
            for cmd_data in commands:
                if cmd_data[1] in text:
                    reply = QMessageBox.question(self, "Confirm", f"Delete '{cmd_data[1]}'?")
                    if reply == QMessageBox.StandardButton.Yes:
                        success, message = self.db.remove_command(cmd_data[0])
                        QMessageBox.information(self, "Success" if success else "Error", message)
                        self.refresh_commands_table()
                        self.refresh_explorer()
                    break
        else:
            QMessageBox.warning(self, "Error", "Please select a command to delete")

    def test_command(self):
        """Test selected command"""
        current_item = self.explorer_list.currentItem()
        if current_item:
            commands = self.db.get_all_commands()
            text = current_item.text()
            for cmd_id, trigger, app_path, desc in commands:
                if trigger in text:
                    self.execute_command(cmd_id, trigger, app_path)
                    break
        else:
            QMessageBox.warning(self, "Error", "Please select a command to test")

    def filter_explorer(self):
        """Filter explorer list based on search"""
        search_text = self.explorer_search.text().lower()
        for i in range(self.explorer_list.count()):
            item = self.explorer_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def refresh_commands_table(self):
        """Refresh commands table"""
        self.commands_table.setRowCount(0)
        
        commands = self.db.get_all_commands()
        for cmd_id, trigger, app_path, description in commands:
            row = self.commands_table.rowCount()
            self.commands_table.insertRow(row)
            
            self.commands_table.setItem(row, 0, QTableWidgetItem(trigger))
            self.commands_table.setItem(row, 1, QTableWidgetItem(app_path))
            self.commands_table.setItem(row, 2, QTableWidgetItem(description or ""))
            
            # Action button
            btn_layout = QHBoxLayout()
            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")
            
            edit_btn.clicked.connect(lambda checked, cid=cmd_id, ct=trigger, cp=app_path, cd=description: 
                                    self.edit_command(cid, (cid, ct, cp, cd)))
            delete_btn.clicked.connect(lambda checked, cid=cmd_id: self.delete_command(cid))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.commands_table.setCellWidget(row, 3, btn_widget)

    def edit_command(self, cmd_id, command_data):
        """Edit existing command"""
        dialog = AddCommandDialog(self, command_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            voice_trigger = dialog.voice_input.text().strip()
            app_path = dialog.app_input.text().strip()
            description = dialog.desc_input.text().strip()
            
            success, message = self.db.update_command(cmd_id, voice_trigger, app_path, description)
            QMessageBox.information(self, "Success" if success else "Error", message)
            self.refresh_commands_table()
            self.refresh_explorer()

    def delete_command(self, cmd_id):
        """Delete command"""
        reply = QMessageBox.question(self, "Confirm", "Delete this command?")
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db.remove_command(cmd_id)
            QMessageBox.information(self, "Success" if success else "Error", message)
            self.refresh_commands_table()
            self.refresh_explorer()

    def on_language_changed(self, index):
        """Update recognition language from settings"""
        language_name = self.language_combo.currentText()
        self.selected_language = self.language_names.get(language_name, "en-US")

    def refresh_history_table(self):
        """Refresh history table"""
        self.history_table.setRowCount(0)
        
        history = self.db.get_history()
        for command, executed_at, status in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(command))
            self.history_table.setItem(row, 1, QTableWidgetItem(executed_at))
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#28a745" if status == "success" else "#dc3545"))
            self.history_table.setItem(row, 2, status_item)

    def refresh_explorer(self):
        """Refresh command explorer"""
        self.explorer_list.clear()
        
        commands = self.db.get_all_commands()
        for cmd_id, trigger, app_path, description in commands:
            item_text = f"🎤 {trigger.upper()}"
            if description:
                item_text += f" - {description}"
            self.explorer_list.addItem(item_text)

    def clear_history(self):
        """Clear execution history"""
        reply = QMessageBox.question(self, "Confirm", "Clear all history?")
        if reply == QMessageBox.StandardButton.Yes:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history')
                conn.commit()
            self.refresh_history_table()
            QMessageBox.information(self, "Success", "History cleared")

    def get_stylesheet(self):
        """Get application stylesheet"""
        return """
            QMainWindow {
                background-color: #0d1117;
                color: #ffffff;
            }
            QWidget {
                background-color: #0d1117;
                color: #ffffff;
            }
            QFrame {
                background-color: #1e1e1e;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d7;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                gridline-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 5px;
                border: none;
                border-right: 1px solid #3d3d3d;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                background-color: #2d2d2d;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #0078d4;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #1084d7;
            }
            QTabWidget {
                background-color: #0d1117;
                border: none;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
        """


def main():
    app = QApplication(sys.argv)
    unlock_dialog = PasswordUnlockDialog()
    if unlock_dialog.exec() == QDialog.DialogCode.Accepted:
        window = VoiceAIApp()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
