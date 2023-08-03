# Changelog

## Linux Support
- Scans for EVE and Discord processes without .exe
- Scans for EVE log directory based on system os

## Others 
- Removed pytz
- Used 'with' to close text files after every refresh/log
- Fixed bug where Discord would continue to update to default presence after >120 seconds since timeUpdated
- Fixed bug where Discord would continue to update combat and mining messages during the 120 seconds
- Deleted 'user' from config.json
