# Changelog

## Major Features
### Linux Support
- Scans for EVE and Discord processes without .exe
- Scans for EVE log directory based on system os

### Smart Game/Log Detection
- Launches EVE launcher automatically via Steam
    - Added "webbrowser" library
- Waits until new log matching character ID appears, links to it

## Bug Fixes
- Bug: Discord would continue to update to default presence after >120 seconds since timeUpdated
- Bug: Discord would continue to update combat and mining messages during the 120 seconds
- Bug: Logging to txt file would only log one line

## Others 
- Removed pytz
    - Removed getTime() function
- Used 'with' to close text files after every refresh/log
- Replaced currentCharacter() with getAlliance() that fetches the EVE API from username
    - Removed "users" and "alliance" from config.json
    - Falls back on the 4 races if alliance not found or not supported
    - Add "requests" library for API access
- Logging cleanliness
- Fallbacks for situations
    - config.json not loaded
    - Game logs not found
    - No character found
- MOAR COMMENTS