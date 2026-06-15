# Luxify Assistant - Quick Start Guide

Get your voice-controlled AI up and running in 5 minutes!

## Step 1: Installation (2 minutes)

### 1.1 Install Python Dependencies
```bash
pip install -r requirements.txt
```

If you encounter issues with PyAudio, see the README.md for platform-specific instructions.

### 1.2 Run the Application
```bash
# Windows
run.bat

# Linux/macOS
bash run.sh
```

Or run directly:
```bash
python code.py
```

## Step 2: Initial Setup (1 minute)

### 2.1 Verify Microphone
1. Go to **Home** tab (🏠)
2. Click **"🎤 Start Listening"**
3. Say something like "Hello"
4. You should see "Recognized: hello" in the status

If microphone not detected:
- Check Settings > Sound > Microphone is set as default
- Restart the application

## Step 3: Add Your First Command (1 minute)

### 3.1 Create Command
1. Go to **Commands** tab (📝)
2. Click **"➕ Add Command"**
3. Fill in the fields:
   - **Voice Trigger:** `open notepad`
   - **Application Path:** `C:\Windows\notepad.exe`
   - **Description:** `Opens text editor`
4. Click **Save**

### 3.2 Find Application Paths
**Common Windows paths:**
- Notepad: `C:\Windows\notepad.exe`
- Calculator: `C:\Windows\System32\calc.exe`
- File Explorer: `C:\Windows\explorer.exe`
- Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`

**To find any application path:**
1. Right-click application shortcut
2. Click "Properties"
3. Look at "Target" field - copy the full path

## Step 4: Test Your Command (30 seconds)

### 4.1 Using Explorer
1. Go to **Explorer** tab (🔍)
2. Find your newly created command
3. Click **"▶️ Test Command"**
4. The application should launch!

If it doesn't work:
- Verify the application path is correct
- Make sure the application file exists
- Check that the path has quotes if it contains spaces

## Step 5: Use Voice Command (30 seconds)

### 5.1 Activate Listening
1. Go to **Home** tab (🏠)
2. Click **"🎤 Start Listening"** (button turns red)
3. Say **"open notepad"** clearly and loudly
4. Notepad should launch!

### 5.2 Monitor Execution
- **Status** shows what was recognized
- **Recent Commands** shows recent executions
- **History** tab shows all past commands with timestamps

## Tips for Success

### Voice Recognition Tips
✓ **Speak clearly** - Enunciate each word  
✓ **Normal volume** - Don't whisper or shout  
✓ **Minimal noise** - Reduce background noise  
✓ **Internet required** - Needs connection for Google API  

### Command Trigger Tips
✓ **Keep it short** - 2-3 words is ideal  
✓ **Make it distinct** - "open notepad" vs "close notepad"  
✓ **Be consistent** - Always say the trigger the same way  
✓ **Use clear words** - Avoid slurred or unclear phrases  

## Recommended Starter Commands

Set these up for a quick start:

| Voice Trigger | Application Path | Description |
|---------------|------------------|-------------|
| open notepad | C:\Windows\notepad.exe | Text editor |
| open browser | C:\Program Files\Google\Chrome\Application\chrome.exe | Web browser |
| open calculator | C:\Windows\System32\calc.exe | Calculator |
| open file explorer | C:\Windows\explorer.exe | File manager |

## Settings Recommendations

### For Beginners
- ✓ Keep all toggles OFF (defaults)
- ✓ Volume at 80%
- ✓ Prefix Mode: OFF
- ✓ Quiet Mode: OFF

### For Power Users
- ✓ Enable Prefix Mode for safety (say "Hey Luxify, ...")
- ✓ Enable Always on Top to keep visible
- ✓ Quiet Mode if in shared spaces
- ✓ Adjust volume to preference

## Troubleshooting Quick Reference

### Problem: "Could not understand audio"
**Try:** Speak louder, reduce background noise, move closer to mic

### Problem: Speech recognition timeout
**Try:** Check internet connection, try again, update API access

### Problem: Command doesn't execute
**Try:** Verify path exists, check in Explorer tab, test command

### Problem: Microphone not found
**Try:** Check system settings, set as default device, restart app

## Next Steps

### 1. Create Your Custom Commands
Add commands for applications you use daily:
- Email client
- IDE or text editor
- Media players
- Utilities

### 2. Organize Your Commands
- Use clear descriptions
- Group similar commands
- Keep trigger names consistent

### 3. Explore Features
- Try different settings combinations
- Check the History tab regularly
- Use Explorer to manage commands

### 4. Advanced Usage
Read ADVANCED_CONFIG.md for:
- Database customization
- Performance optimization
- Extension possibilities
- Voice profiles (future)

## Keyboard Shortcuts (Available)
- `Tab` - Navigate between fields
- `Enter` - Confirm dialogs
- `Delete` - Delete selected items
- `Ctrl+A` - Select all in tables

## Useful Keyboard Workflow

1. **Create command:** Tab to App Path field → Paste path → Tab to Description → Enter
2. **Delete command:** Select row → Press Delete → Confirm
3. **Search Explorer:** Ctrl+F in Explorer tab → Type search term

## Video Tutorial Walkthrough

### Minute 0-1: Setup
- Install requirements
- Run application
- Check microphone

### Minute 1-3: Add Commands
- Go to Commands tab
- Add first command
- Add second command

### Minute 3-4: Test
- Use Explorer to test
- See history update

### Minute 4-5: Use Voice
- Enable listening
- Speak command
- Watch application launch

## Support Resources

### In-App Help
- **Hover tooltips** - Descriptions of buttons
- **Status messages** - Real-time feedback
- **History tab** - Track everything executed

### External Resources
- README.md - Complete user guide
- ADVANCED_CONFIG.md - Technical details
- COMMANDS_EXAMPLES.json - Pre-configured examples

## Common Mistakes to Avoid

❌ **Wrong:** Application path without full directory  
✓ **Right:** C:\Program Files\Application\app.exe

❌ **Wrong:** Voice trigger with special characters  
✓ **Right:** open notepad

❌ **Wrong:** Speaking command before enabling listening  
✓ **Right:** Click button first, then speak

❌ **Wrong:** Using Windows shortcut path  
✓ **Right:** Use the actual application .exe file

## Performance Notes

### First Launch
- Takes a few seconds to initialize database
- First speech recognition has slight delay (API startup)

### Subsequent Launches
- Much faster after database initialized
- Microphone already configured
- Commands cached in memory

### During Use
- Listening is non-blocking (UI stays responsive)
- Multiple commands can be in history
- Database grows over time (can be cleared)

## Backup Your Commands

Your commands are stored in `voice_commands.db` file.

### Simple Backup:
```bash
copy voice_commands.db voice_commands_backup.db
```

### Restore:
```bash
copy voice_commands_backup.db voice_commands.db
```

## What's Next?

1. ✓ Add 5-10 of your most-used applications
2. ✓ Practice saying voice triggers consistently
3. ✓ Enable Quiet Mode if needed
4. ✓ Set Always on Top for quick access
5. ✓ Explore History to see your usage patterns

---

**Congratulations!** 🎉 You now have a working voice-controlled AI system!

Need help? Check README.md or ADVANCED_CONFIG.md for more details.

**Happy voice controlling!** 🎤✨
