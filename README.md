# EVE-Discord-Rich-Presence

Python Script for displaying EVE Discord Rich Presence

## Requirements
- OS: Windows or Linux
- Python (3.10 or above)

## Features
- [X]  Character Detection
- [X]  Corporation Config
- [X]  Mining and Combat Detection
- [X]  System Detection
- [X]  Automatic Shutdown
- []  Game/Log Startup Detection
- [X]  Pull Character Information from EVE API
- [X] Cross Platform

## Limitations
- Not extensively tested
- Unable to launch EVE instances not on Steam
- Slow refresh (15s)
- Limited alliance selection
    - Alliance will be one of the four races if not availiable

## Screenshots
![Discord](screenshots/discord.png)

![Logs](screenshots/logs.png)

## Installation
1. Download the [**Newest Release**](https://github.com/ianli0122/EVE-Discord-Rich-Presence/releases)
2. Install the required libraries using `pip install -r requirements.txt` inside the folder
3. Edit **config.json**
```
{
    "characterName": {IGN},
    "lastSystem": {Current System},
    "delay": 15
}
```
(Recommended delay time is 15 seconds)

## Usage
1. Launch Discord
2. Run the script

When EVE or Discord is closed, the script will detect it and shutdown automatically.

## Availiable Alliances
|Alliances|
|-------|
|Azure Citizen|
|Brave Collective|
|Brave United|
|Dracarys|
|Fraternity.|
|Fraternity University|
|Goonswarm Federation|
|Pandemic Horde|
|Silent Company|
|The Initiative|
|WE FORM BL0B|
|WE FORM V0LTA|