# Luxify Assistant - Advanced Configuration Guide

## Overview
This document provides detailed information about the Luxify Assistant voice-controlled AI system and its advanced features.

## Architecture

### Core Components

#### 1. VoiceListenerThread
- Runs on a separate thread to avoid UI blocking
- Uses Google Speech Recognition API
- Automatically adjusts for ambient noise
- Emits signals for recognized commands and errors

**Key Features:**
- Non-blocking voice listening
- Timeout handling (1 second listen timeout, 5 second phrase limit)
- Graceful error handling

#### 2. CommandDatabase
- SQLite-based persistent storage
- Two main tables: `commands` and `history`
- CRUD operations for command management
- Automatic timestamp tracking

**Database Schema:**
```
commands:
- id (PRIMARY KEY)
- voice_trigger (UNIQUE, case-insensitive)
- application_path
- description
- created_at

history:
- id (PRIMARY KEY)
- command
- executed_at
- status (success/failed)
```

#### 3. VoiceAIApp (Main Window)
- PyQt6-based GUI
- Modular tab system (Home, Commands, Settings, History, Explorer)
- Real-time status updates
- Responsive and non-blocking

## Configuration Options

### Settings Panel

#### Prefix Mode
- **Default:** OFF
- **Purpose:** Requires a prefix word before commands
- **Example:** Say "Hey Luxify, open notepad" instead of just "open notepad"
- **Benefit:** Reduces accidental command triggers

#### Quiet Mode
- **Default:** OFF
- **Purpose:** Disables text-to-speech feedback
- **Benefit:** Silent operation in shared spaces
- **Uses:** Uses pyttsx3 TTS engine

#### Avatar Animation
- **Default:** ON
- **Purpose:** Shows visual feedback during listening
- **Benefit:** User feedback that system is active
- **Note:** Currently shows status text; can be extended to animated avatar

#### Window Always on Top
- **Default:** OFF
- **Purpose:** Keeps window above other applications
- **Benefit:** Quick access to commands and history

#### Volume Control
- **Range:** 0-100%
- **Default:** 80%
- **Applies to:** Text-to-speech feedback
- **Note:** Controlled by pyttsx3 engine

## Voice Command System

### How Voice Matching Works

1. **Listening Phase:** Microphone listens for audio with ambient noise adjustment
2. **Recognition Phase:** Audio converted to text using Google Speech Recognition
3. **Matching Phase:** Text searched against all voice triggers (case-insensitive)
4. **Execution Phase:** First matching command is executed
5. **History Phase:** Execution logged with timestamp and status

### Voice Trigger Best Practices

1. **Clarity:** Use distinct, easy-to-pronounce words
2. **Length:** Keep to 2-3 words for better recognition
3. **Uniqueness:** Avoid similar-sounding triggers
4. **Context:** Use context-appropriate triggers
   - "open" for applications
   - "launch" for tools
   - "start" for services

**Good Examples:**
- "open notepad"
- "launch calculator"
- "open file explorer"

**Poor Examples:**
- "the file thing" (too vague)
- "open notes" vs "open note" (too similar)
- "activate application launcher" (too long)

## Database Management

### Backup and Restore

**Manual Backup:**
```bash
# Copy database file
copy voice_commands.db voice_commands_backup.db
```

**Restore from Backup:**
```bash
# Stop the application
# Replace current database with backup
copy voice_commands_backup.db voice_commands.db
```

### Accessing Database Directly

**Using SQLite CLI:**
```bash
sqlite3 voice_commands.db
```

**Useful Queries:**
```sql
-- View all commands
SELECT * FROM commands;

-- View recent history
SELECT * FROM history ORDER BY executed_at DESC LIMIT 20;

-- Export commands
.mode csv
.output commands.csv
SELECT * FROM commands;
.quit

-- Delete specific command
DELETE FROM commands WHERE voice_trigger = 'open notepad';

-- Clear old history (older than 30 days)
DELETE FROM history WHERE executed_at < datetime('now', '-30 days');
```

## Troubleshooting Guide

### Issue: Microphone not detected
**Solution:**
1. Check device manager for microphone
2. Set microphone as default input device
3. Grant microphone permissions to Python
4. Restart application

### Issue: "Could not understand audio"
**Solution:**
1. Reduce background noise
2. Speak louder and clearer
3. Increase microphone sensitivity
4. Move closer to microphone

### Issue: Command not executing
**Diagnosis:**
1. Check if command path exists
2. Verify application can be launched manually
3. Check command history for errors
4. Use Explorer tab to test command

### Issue: Speech recognition timeout
**Solution:**
1. Check internet connection (API dependent)
2. Check firewall settings
3. Verify Google Speech API is accessible
4. Try again with clearer speech

### Issue: High CPU usage
**Solution:**
1. Disable avatar animation
2. Reduce listening frequency
3. Close other applications
4. Update Python and libraries

## Performance Optimization

### UI Responsiveness
- Voice listener runs on separate thread
- All heavy operations non-blocking
- Slider updates don't freeze UI
- Table refreshes happen asynchronously

### Memory Management
- Database queries limited to necessary fields
- History limited to last 50 entries by default
- Recent list limited to 5 items
- Proper cleanup on thread exit

### Database Optimization
**Recommended Maintenance:**
```sql
-- Optimize database
VACUUM;

-- Analyze for query planning
ANALYZE;

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_voice_trigger ON commands(voice_trigger);
CREATE INDEX IF NOT EXISTS idx_executed_at ON history(executed_at);
```

## Extension Possibilities

### Future Features
1. **Voice Profiles:** Multiple users with different commands
2. **Custom Hotkey:** Global hotkey to toggle listening
3. **Voice Macros:** Chain multiple commands
4. **Command Aliases:** Multiple voice triggers for one command
5. **Analytics Dashboard:** Command usage statistics
6. **Cloud Sync:** Synchronize commands across devices
7. **Custom TTS:** Different voices and languages
8. **AI Training:** Machine learning for personalized recognition

### API Integration
The system can be extended to:
- Control smart home devices
- Send emails/messages
- Query online services
- Execute scripts and batch files
- Control media playback
- Access system information

## Security Considerations

### Data Privacy
- All data stored locally in SQLite
- No cloud transmission (except Google Speech API)
- No personal information collection
- User has full control over database

### Best Practices
1. Keep voice commands vague enough not to expose personal info
2. Regularly backup database
3. Secure sensitive application paths
4. Use in private environments for sensitive commands
5. Consider using proxy for Speech API in sensitive networks

## Command Execution Safety

The application:
- Verifies application path exists before execution
- Uses subprocess.Popen for safe execution
- Logs all execution attempts
- Captures and displays errors
- Doesn't allow arbitrary code execution (only app launching)

## Logging and Debugging

### Enable Debug Mode (Modify code.py)
```python
# Add at the beginning of main()
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Debug Checks
```python
# Check microphone availability
import speech_recognition as sr
mic = sr.Microphone()

# Test speech recognition
recognizer = sr.Recognizer()
with mic as source:
    audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio)
    print(f"Recognized: {text}")
```

## System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- 100MB disk space
- Microphone input
- Internet connection (for Google Speech API)

### Recommended
- Python 3.10+
- 4GB RAM
- 500MB disk space
- Good quality USB microphone
- Stable internet connection

### Supported Platforms
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, Fedora 30+, etc.)

## File Structure

```
voice_ai/ui_test/
├── code.py                  # Main application (1000+ lines)
├── requirements.txt         # Python dependencies
├── README.md               # User guide
├── COMMANDS_EXAMPLES.json  # Example commands
├── ADVANCED_CONFIG.md      # This file
├── run.bat                 # Windows startup script
├── run.sh                  # Linux/macOS startup script
└── voice_commands.db       # SQLite database (created on first run)
```

## License and Support

This is an open-source educational project. Feel free to modify and extend!

For issues or improvements:
1. Check existing troubleshooting guide
2. Review system requirements
3. Verify all dependencies installed
4. Check database integrity

---

**Last Updated:** 2024
**Version:** 1.0
