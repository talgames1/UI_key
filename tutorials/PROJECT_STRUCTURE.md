# Project Structure - Luxify Assistant Voice Control AI

## 📁 File Overview

### Core Application
- **code.py** (1000+ lines)
  - Main PyQt6 application
  - Voice listener thread implementation
  - SQLite database management
  - All UI components and styling

### Documentation & Guides
- **README.md** - Complete user guide with installation & usage
- **QUICK_START.md** - 5-minute quick start guide
- **ADVANCED_CONFIG.md** - Technical details and advanced features
- **PROJECT_STRUCTURE.md** - This file

### Configuration & Examples
- **COMMANDS_EXAMPLES.json** - Example commands and Windows app paths
- **requirements.txt** - Python package dependencies
- **run.bat** - Windows startup script
- **run.sh** - Linux/macOS startup script

### Runtime Data
- **voice_commands.db** - SQLite database (created on first run)
  - Stores all voice commands
  - Logs execution history

## 🎯 Key Features Implemented

### 1. Voice Recognition System ✓
- Real-time microphone listening
- Google Speech Recognition API integration
- Non-blocking background thread
- Automatic ambient noise adjustment
- Timeout and error handling

### 2. User Interface ✓
**Multi-tab Design:**
- Home Tab: Main control and recent commands
- Commands Tab: Create, edit, delete voice commands
- Settings Tab: Control panel for features
- History Tab: View execution history
- Explorer Tab: Browse and manage commands

**Visual Design:**
- Dark modern theme (matches screenshot)
- Responsive layout
- Professional gradient effects
- Clear status indicators
- Intuitive navigation

### 3. Settings Section ✓
- Prefix Mode toggle (requires "Hey Luxify" prefix)
- Quiet Mode toggle (disable TTS feedback)
- Avatar Animation toggle
- Window Always on Top toggle
- Volume slider (0-100%)

### 4. Command Management ✓
- Add new voice commands
- Edit existing commands
- Delete commands
- Unique voice trigger validation
- Support for command descriptions

### 5. Execution History ✓
- Automatic logging of all commands
- Timestamp tracking
- Success/failure status
- 50-command limit per session
- Clear history functionality

### 6. Command Explorer ✓
- Browse all commands
- Search/filter functionality
- Edit commands in-place
- Delete commands
- Test commands before activation
- Copy command details

## 🏗️ Architecture Overview

```
VoiceAIApp (Main Window)
├── Sidebar Navigation
│   └── 5 Tab Navigation Buttons
├── Content Area (QTabWidget)
│   ├── Home Tab
│   │   ├── Status Display
│   │   ├── Listen Button
│   │   └── Recent Commands List
│   ├── Commands Tab
│   │   ├── Commands Table
│   │   ├── Add/Refresh Buttons
│   │   └── Edit/Delete Actions
│   ├── Settings Tab
│   │   ├── Prefix Mode Checkbox
│   │   ├── Quiet Mode Checkbox
│   │   ├── Avatar Animation Checkbox
│   │   ├── Always on Top Checkbox
│   │   └── Volume Slider
│   ├── History Tab
│   │   ├── History Table
│   │   ├── Refresh/Clear Buttons
│   │   └── Status Indicators
│   └── Explorer Tab
│       ├── Search Bar
│       ├── Command List
│       └── Edit/Delete/Test Buttons

VoiceListenerThread
├── Microphone Interface
├── Speech Recognition
├── Command Matching
└── Signal Emission

CommandDatabase
├── SQLite Connection
├── Commands Table
├── History Table
├── CRUD Operations
└── Query Functions

AddCommandDialog
├── Voice Trigger Input
├── App Path Input
├── Description Input
└── Save/Cancel Buttons
```

## 💾 Database Schema

### Commands Table
```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voice_trigger TEXT UNIQUE NOT NULL,
    application_path TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### History Table
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success'
)
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | 6.6.1 | UI Framework |
| PyQt6-Charts | 6.6.0 | Chart components |
| speech-recognition | 3.10.0 | Voice recognition |
| pyttsx3 | 2.90 | Text-to-speech |
| pyaudio | 0.2.13 | Microphone interface |

## 🚀 Getting Started

### Quick Start (3 steps)
1. **Install:** `pip install -r requirements.txt`
2. **Run:** `python code.py` or `run.bat`
3. **Use:** Go to Commands tab, add a command, then listen!

### Detailed Setup
See QUICK_START.md for step-by-step instructions

## 🎨 UI Components

### Color Scheme
- Background: `#0d1117` (Dark blue-grey)
- Secondary: `#1e1e1e` (Darker)
- Accent: `#0078d4` (Microsoft blue)
- Text: `#ffffff` (White)
- Border: `#3d3d3d` (Grey)

### Styling Features
- Rounded corners (4-8px radius)
- Smooth hover effects
- Consistent spacing
- Professional typography
- Status color coding (green=success, red=error)

## 🔧 Configuration Files

### requirements.txt
Lists all Python package dependencies for easy installation

### run.bat
Windows batch script that:
- Checks Python installation
- Verifies dependencies
- Launches application

### run.sh
Linux/macOS shell script that:
- Checks Python 3 installation
- Verifies dependencies
- Launches application

## 📚 Documentation Structure

### For Users
- **README.md**: Complete feature list and installation guide
- **QUICK_START.md**: 5-minute setup walkthrough
- **COMMANDS_EXAMPLES.json**: Copy-paste ready examples

### For Developers
- **ADVANCED_CONFIG.md**: Technical architecture and extension guide
- **code.py**: Fully commented source code (1000+ lines)
- **This document**: Project structure overview

## 💡 Key Implementation Details

### Threading Model
- Main thread: UI (PyQt6 event loop)
- Worker thread: Voice listening (VoiceListenerThread)
- Signal-based communication between threads

### Error Handling
- Try-catch blocks for robustness
- User-friendly error messages
- Graceful degradation
- Logging of failures

### Data Persistence
- SQLite database for commands
- Automatic history logging
- Settings stored in UI state
- No external APIs called except Speech Recognition

### Performance Optimizations
- Non-blocking listening
- Lazy loading of table data
- Database query optimization
- Memory-efficient UI updates

## 🎯 Feature Checklist

- ✅ Voice command recognition and execution
- ✅ Sleek modern UI with dark theme
- ✅ Settings section with multiple toggles
- ✅ Commands section with CRUD operations
- ✅ History section with execution logs
- ✅ Command explorer with search
- ✅ Add/edit/delete commands
- ✅ Test commands before activation
- ✅ Volume control for TTS
- ✅ Quiet mode for silent operation
- ✅ Recent commands display
- ✅ Command history with timestamps
- ✅ Status indicators
- ✅ Error handling and reporting
- ✅ Database persistence
- ✅ Multiple startup scripts
- ✅ Comprehensive documentation

## 🔐 Security Features

- ✅ Local-only data storage (no cloud sync by default)
- ✅ Application path validation
- ✅ Subprocess execution with error handling
- ✅ No arbitrary code execution
- ✅ Voice command logging for audit trail
- ✅ User confirmation for deletions

## 🌟 Extensibility

The system can be easily extended with:
- Custom voice profiles
- Command aliases and macros
- Voice-based smart home control
- Integration with APIs and web services
- Custom audio processing
- Machine learning for personalization
- Multi-language support
- Cloud synchronization

## 📋 Maintenance

### Regular Tasks
- Clear history monthly: History Tab → Clear History
- Backup commands: Copy `voice_commands.db` file
- Update dependencies: `pip install -r requirements.txt --upgrade`

### Troubleshooting Resources
- Check README.md for common issues
- See ADVANCED_CONFIG.md for debugging
- Review voice recognition settings
- Verify microphone permissions

## 📞 Support

For issues:
1. Check QUICK_START.md troubleshooting
2. Review README.md FAQ
3. See ADVANCED_CONFIG.md technical guide
4. Verify system meets requirements
5. Check database integrity with SQLite

## 🎓 Learning Resources

### Understanding the Code
- Start with the main loop in `VoiceAIApp.__init__`
- Review `VoiceListenerThread` for threading
- Study `CommandDatabase` for data management
- Examine UI components in `create_*_tab()` methods

### Extending Functionality
- Add new UI tabs in `create_content_area()`
- Implement new database features in `CommandDatabase`
- Extend `VoiceListenerThread` for additional recognition
- Add settings toggles in `create_settings_tab()`

---

**Project Version:** 1.0  
**Created:** 2024  
**Status:** Complete and Ready to Use  
**License:** Open Source (Educational)

For a quick overview, start with QUICK_START.md.  
For complete details, read README.md.  
For technical information, see ADVANCED_CONFIG.md.
