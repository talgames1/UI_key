# Luxify Assistant - Voice Control AI System   ---VERSION ALPHA: 0.3---

A sleek, modern voice-controlled AI application that listens to user-spoken commands and launches applications based on those commands.

## Features

### 🎤 Voice Recognition
- Real-time voice command recognition using Google Speech Recognition API
- Automatic command matching against your voice triggers
- Background listening without blocking the UI

### 📝 Command Management
- Add, edit, and delete custom voice commands
- Link voice triggers to any application path
- Add descriptions to commands for better organization

### ⚙️ Settings Panel
- **Prefix Mode**: Enable/disable prefix requirement for commands
- **Quiet Mode**: Toggle audio feedback on/off
- **Avatar Animation**: Show/hide avatar animations
- **Always on Top**: Keep window above other windows
- **Volume Control**: Adjust TTS (Text-to-Speech) volume (0-100%)

### 📊 Execution History
- View all executed commands with timestamps
- Track command success/failure status
- Clear history when needed

### 🔍 Command Explorer
- Browse all available voice commands
- Search and filter commands
- Edit or delete commands directly from explorer
- Test commands before using them live

### 💾 Data Persistence
- SQLite database for storing commands
- Automatic history logging
- Persistent settings between sessions

## Installation

### Prerequisites
- Python 3.8+
- Microphone (for voice input)
- Internet connection (for Google Speech Recognition)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install PyAudio (if needed)
For Windows (if pip install fails):
```bash
pip install pipwin
pipwin install pyaudio
```

For macOS:
```bash
brew install portaudio
pip install pyaudio
```

For Linux:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Step 3: Run the Application
```bash
python code.py
```

## Usage Guide

### Home Tab (🏠)
- **Listen Button**: Start/stop listening for voice commands
- **Status Display**: Shows current listening status
- **Recent Commands**: Quick view of recently executed commands

### Commands Tab (📝)
- **Add Command**: Create new voice command
  - Voice Trigger: The words to say (e.g., "open notepad")
  - Application Path: Full path to application (e.g., "C:\\Windows\\notepad.exe")
  - Description: Optional description
- **Edit/Delete**: Manage existing commands
- **Refresh**: Update the command list

### Settings Tab (⚙️)
- Toggle various features
- Adjust volume slider (0-100%)
- Customize AI behavior

### History Tab (📊)
- View execution history with timestamps
- See success/failure status of each command
- Clear all history

### Explorer Tab (🔍)
- Search commands by name or description
- Edit selected command
- Delete selected command
- Test commands before activating listening

## Example Voice Commands

Setup these commands in the app:

1. **"open notepad"** → `C:\Windows\notepad.exe`
2. **"launch calculator"** → `C:\Windows\System32\calc.exe`
3. **"open browser"** → `C:\Program Files\Google\Chrome\Application\chrome.exe`
4. **"open visual studio"** → `C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe`
5. **"open spotify"** → `C:\Users\[YourUsername]\AppData\Roaming\Spotify\Spotify.exe`

## Database Schema

### Commands Table
```
- id: INTEGER PRIMARY KEY
- voice_trigger: TEXT UNIQUE
- application_path: TEXT
- description: TEXT
- created_at: TIMESTAMP
```

### History Table
```
- id: INTEGER PRIMARY KEY
- command: TEXT
- executed_at: TIMESTAMP
- status: TEXT (success/failed)
```

## Troubleshooting

### Microphone not detected
- Check that your microphone is connected and enabled
- Go to Settings > Sound and verify microphone is set as default
- Restart the application

### Speech recognition errors
- Ensure you have internet connection (Google Speech Recognition requires it)
- Speak clearly and at normal volume
- Make sure there's minimal background noise

### Commands not executing
- Verify the application path is correct
- Use absolute paths (full path from root)
- Ensure the application file exists

### PyAudio installation issues
- Follow platform-specific installation steps above
- Consider using virtual environment

## Advanced Features

### Batch Testing
Select any command in Explorer and click "Test Command" to verify it launches correctly without actually listening.

### History Tracking
All executed commands are logged automatically. Use the History tab to verify commands were executed.

### Volume Adjustment
Use the volume slider in Settings to control TTS feedback volume.

## File Structure
```
voice_ai/
├── code.py              # Main application
├── requirements.txt     # Dependencies
├── README.md           # This file
└── voice_commands.db   # SQLite database (created on first run)
```

## Keyboard Shortcuts (Future)
- `Ctrl+Shift+V`: Toggle listening
- `Ctrl+E`: Open Explorer
- `Ctrl+S`: Open Settings

## License
This project is provided as-is for educational and personal use.

## Support
For issues or improvements, check:
1. Microphone permissions in system settings
2. Python version compatibility (3.8+)
3. All dependencies installed correctly

Enjoy your voice-controlled AI experience! 🎤✨

## Firebase Unlock (User Access)
This application is distributed to end users and includes a simple unlock step at startup.

How to unlock
- When you start the app you will be prompted for a password. Enter the password provided by your administrator or support contact.
- If the password is correct the app opens normally.
- If the password is incorrect you will see "Incorrect password" — try again or contact your administrator.

Connection problems
- If you see "Firebase connection failed" when starting the app, first check your internet connection and try again.
- If the problem continues, contact your administrator or support — the app needs to be able to reach the remote access service to verify passwords.

If you are the administrator
- If you are responsible for deploying this app and need to configure access, see the developer documentation or contact the project maintainer for setup instructions. The user app does not include any private admin credentials.
