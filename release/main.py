'''
- Log updates
- More alliances
- Switch to local chat for system detection
'''


#Imports
from pypresence import Presence
from datetime import datetime, timezone
import sys
import requests
import webbrowser
import time
import psutil
import json
import os

'''
Functions
'''
def logging(message, type): #Logging
    debugLogTime = datetime.utcfromtimestamp(timeLaunched).strftime('%m%d%Y %H%M%S')

    logMessage = datetime.now(timezone.utc).strftime('%m/%d/%Y %H:%M:%S') + f': [{type.upper()}] {message}'
    
    with open(f'{os.getcwd()}/logs/{debugLogTime}.txt', 'a') as debugLog:
        debugLog.write(f"{logMessage}\n")
    print(logMessage)

def checkRunning(): #Check if EVE and Discord are Running
    processNames = [p.name() for p in psutil.process_iter()]
    discord = "Discord" in processNames or "Discord.exe" in processNames
    eve = "exefile" in processNames or "exefile.exe" in processNames

    if discord and eve:
        return True
    elif discord and not(eve):
        logging('EVE not detected', 'warn')        
        return False
    elif not(discord) and eve:
        logging('Discord not detected', 'warn')        
        return False
    else:
        logging('EVE and Discord not detected', 'warn')        
        return False

def getAlliance(): #Get Aliiance Name from EVE API
    global id, allianceID, allianceName
    headers = {
        'accept': "application/json",
        "Accept-Language": "en",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    bloodlineIds = {
        "Amarr": [5, 6, 13],
        "Caldari": [1, 11, 2],
        "Gallente": [7, 8, 12],
        "Minmatar": [4, 3, 14]
    }
    supportedAlliances = ['Azure Citizen', 'Brave Collective', 'Brave United', 'Dracarys', 'Fraternity', 'Fraternity University', 'Goonswarm Federation', 'Pandemic Horde', 'Silent Company', 'The Initiative', 'WE FORM BL0B', 'WE FORM V0LTA']
    try:
        id = requests.post("https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en", headers = headers, data = f"[\"{characterName}\"]").json()['characters'][0]['id']
        logging(f'Character ID is {id}', 'startup')
    except:
        logging('No character found', 'critical')
        shutdown()

    try:
        allianceID = requests.get(f"https://esi.evetech.net/latest/characters/{id}/?datasource=tranquility").json()['alliance_id']
        allianceName = requests.get(f"https://esi.evetech.net/latest/alliances/{allianceID}/?datasource=tranquility").json()['name']
        logging(f'Character alliance is {allianceName}', 'startup')
        
        allianceName = allianceName.replace('.', "")
        if allianceName not in supportedAlliances:
            allianceID = requests.get(f"https://esi.evetech.net/latest/characters/{id}/?datasource=tranquility").json()['bloodline_id']
            for key, value in bloodlineIds.items():
                if allianceID in value:
                    allianceName = key
            logging(f'Alliance not supported, reverting to {allianceName}', 'startup')
            
    except KeyError:
        allianceID = requests.get(f"https://esi.evetech.net/latest/characters/{id}/?datasource=tranquility").json()['bloodline_id']
        for key, value in bloodlineIds.items():
            if allianceID in value:
                allianceName = key
        logging(f'No alliance found, character alliance is now: {allianceName}', 'startup')

def updateActivity(line): #Parses and Detects Activity Type
    global inCombat, inMining, system, logContent, timeUpdated, systemUpdate
    lineTxt = logContent[line]
    activity = ''

    if line <= 4:
        return 0
    else:
        try:
            for x in range(lineTxt.index('(') + 1, lineTxt.index(')')):
                activity = activity + lineTxt[x]
            logging('Message detected: ' + activity, 'update')
        except ValueError:
            logging('No activity type', 'warn')
            return 0
    
    match activity:
        case 'None':
            startPos = lineTxt.index(' to ') + 4
            system = lineTxt[startPos:].replace('\n', "")
            systemUpdate = True
            logging('System is now: ' + system, 'update')
        case 'combat':
            inCombat = True
            inMining = False
            timeUpdated = int(time.time())
            logging('inCombat', 'update')
        case 'mining':
            inMining = True
            if not(inCombat):
                timeUpdated = int(time.time())
            logging('inMining', 'update')
        case _:
            logging('Activity not found', 'warn')


def updateLog(): #Updates logContent
    global logContent, update, log
    lastContent = logContent
    logContent = []
    
    with open(logDir, 'r') as log:
        for x in log:
            logContent.append(x)

    if logContent == lastContent:
        update = False
    else:
        update = True

    logging('Log updated', 'notice')
    return len(logContent)

def updateDiscord(): #Updates Discord Rich Presence
    global timeUpdated, timeLaunched, inCombat, inMining, system, systemUpdate

    if int(time.time()) - timeUpdated >= 120 and (inCombat or inMining):
        presence.update(details = characterName, state = 'In ' + system, start = timeEVELaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord updated to neutral', 'update')
        inCombat = False
        inMining = False

    if systemUpdate and not(inCombat):
        presence.update(details = characterName, state = 'In ' + system, start = timeEVELaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord updated system to ' + system, 'update')
        systemUpdate = False
    elif inCombat and update:
        presence.update(details = characterName, state = 'In Combat', start = timeEVELaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord updated to \'In Combat\'', 'update')
    elif inMining and update and not(inCombat):
        presence.update(details = characterName, state = 'Mining in ' + system, start = timeEVELaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord updated to \'Mining\'', 'update')
    

def shutdown():
    global system

    config['lastSystem'] = system
    os.remove('config.json')
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    logging('Updated config.json', 'shutdown')

    try:
        presence.close()
        logging('Discord presence closed', 'shutdown')
    except:
        logging('Discord presence closed', 'shutdown')
    sys.exit()


timeLaunched = int(time.time())
logging('Program start', 'startup')

#Load Config
try:
    with open('config.json', 'r+') as x:
        config = json.load(x)
except:
    logging('config.json not detected', 'critical')
    shutdown()
logging('config.json loaded', 'startup')

#Current Activity
inCombat = False
inMining = False
systemUpdate = False
system = config['lastSystem']

#Log
homeDir = os.path.expanduser('~')
osName = os.name
logging(f'OS is {osName}', 'startup')
if osName == 'nt':
    logsDir = homeDir.replace('\\', '/')
    logsDir += '/Documents/EVE/logs/Gamelogs'
elif osName == 'posix':
    logsDir = homeDir + '/Documents/EVE/logs/Gamelogs'
    if not(os.path.exists(logsDir)):
        logsDir = homeDir + '/.local/share/Steam/steamapps/compatdata/8500/pfx/drive_c/users/steamuser/My Documents/EVE/logs/Gamelogs'

if not(os.path.exists(logsDir)):
    logging('Game logs not found', 'critical')
    shutdown()

logging(f'Gamelogs in {logsDir}', 'startup')
logDir = ''
logList = []
logContent = []
lastLine = 0
currentLine = 0

#Misc
update = False
timeEVELaunched = 0
timeUpdated = int(time.time())
initalConfig = True

#Discord
clientID = '1136144163868508262'
presence = Presence(clientID)

#Character Info
characterName = config['characterName']
logging('Active character is: ' + characterName, 'startup')
id = 0
allianceID = 0
allianceName = ''
getAlliance()
alliancePic = allianceName.lower().replace(' ', '_')

try: #Connect to Discord
    presence.connect()
except:
    logging('Discord connection error (Discord might not be running)', 'critical')
    shutdown()

logging('Opening EVE Launcher through Steam', 'startup')
webbrowser.open('steam://rungameid/8500') #Open EVE Launcher
for file in sorted(os.listdir(logsDir)): #Take Initial Snapshot
    if file.endswith('.txt'):
        logList.append(file)
logging('Initial logs snapshot taken', 'startup')

while True:
    if checkRunning() and initalConfig:
        logging('EVE detected', 'startup')
        while True:
            logSnapshot = logList
            logList = []

            for file in sorted(os.listdir(logsDir)):
                if file.endswith('.txt'):
                    logList.append(file)

            for x in logList:
                if x not in logSnapshot:
                    logging(f'New log found: {x}', 'update')
                    if x[16:] == str(id) + '.txt':
                        logging('Log matched to character ID, continuing startup', 'update')
                        logDir = f"{logsDir}/{x}"
                        timeEVELaunched = int(time.time())
                        break
            
            if logDir != '':
                break

            logging('Character not connected', 'warn')
            time.sleep(config['delay'])
    if logDir != '':
        break
    time.sleep(config['delay'])


while checkRunning():
    if initalConfig:
        logging('Log is: ' + logDir, 'startup')
        with open(logDir, 'r') as log:
            logging('Log Opened', 'startup')
            for x in log:
                logContent.append(x)
        logging('Initial log analyzed', 'startup')

        presence.update(details = characterName, state = 'In ' + system, start = timeEVELaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord rich presence started', 'startup')

        lastLine = len(logContent)
        initalConfig = False

        logging('Startup complete', 'startup')

    currentLine = updateLog()
    if update:
        for i in range(lastLine, currentLine):
            updateActivity(i)
        lastLine = currentLine
        updateDiscord()
    else:
        updateDiscord()
        logging('No change detected', 'notice')
    time.sleep(config['delay'])

shutdown()