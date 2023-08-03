#Imports
from pypresence import Presence
from datetime import datetime
import sys
import time
import psutil
import json
import pytz
import os

'''
Functions
'''
def logging(message, type): #Logging
    log = datetime.now(pytz.timezone('utc')).strftime('%m/%d/%Y %H:%M:%S') + ': [' + type + '] ' + message
    print(log)
    debugLog.write(log + '\n')

def getTime(): #Get Current Time
    return datetime.now(pytz.timezone('utc'))

def checkRunning(): #Check if EVE and Discord are Running
    discord = "Discord.exe" in (p.name() for p in psutil.process_iter())
    eve = "exefile.exe" in (p.name() for p in psutil.process_iter())
    if discord and eve:
        return True
    elif discord and not(eve):
        logging('EVE not detected', 'WARN')        
        return False
    elif not(discord) and eve:
        logging('Discord not detected', 'WARN')        
        return False
    else:
        logging('EVE and Discord not detected', 'WARN')        
        return False

def currentCharacter(): #Gets Name of Current Character
    out = logContent[2][12:].replace('\n', "")
    return out

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
            logging('Message Detected: ' + activity, 'UPDATE')
        except ValueError:
            logging('No Activity Type', 'WARN')
            return 0
    
    match activity:
        case 'None':
            startPos = lineTxt.index(' to ') + 4
            system = lineTxt[startPos:].replace('\n', "")
            systemUpdate = True
            logging('System is now: ' + system, 'UPDATE')
        case 'combat':
            inCombat = True
            inMining = False
            timeUpdated = int(time.time())
            logging('isCombat', 'UPDATE')
        case 'mining':
            inMining = True
            inCombat = False
            timeUpdated = int(time.time())
            logging('isMining', 'UPDATE')
        case _:
            logging('Activity not found', 'WARN')


def updateLog(): #Updates logContent
    global logContent, update, log
    lastContent = logContent
    logContent = []
    
    log = open(logDir, 'r')

    for x in log:
        logContent.append(x)

    log.close()

    if logContent == lastContent:
        update = False
    else:
        update = True

    logging('Log updated', 'NOTICE')
    return len(logContent)

def updateDiscord():
    global timeUpdated, timeLaunched, inCombat, inMining, system, systemUpdate

    if int(time.time()) - timeUpdated >= 120:
        presence.update(details = currentCharacter(), state = 'In ' + system, start = timeLaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord Updated to Neutral', 'UPDATE')
        inCombat = False
        inMining = False

    if systemUpdate:
        presence.update(details = currentCharacter(), state = 'In ' + system, start = timeLaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord Updated System to ' + system, 'UPDATE')
        systemUpdate = False
    elif inCombat:
        presence.update(details = currentCharacter(), state = 'In Combat', start = timeLaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord Updated to \'In Combat\'', 'UPDATE')
    elif inMining:
        presence.update(details = currentCharacter(), state = 'Mining in ' + system, start = timeLaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord Updated to \'Mining\'', 'UPDATE')
    

def shutdown():
    global system

    config['lastSystem'] = system
    os.remove('config.json')
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    logging('Updated config.json', 'SHUTDOWN')

    try:
        presence.close()
        logging('Discord Presence Closed', 'SHUTDOWN')
    except:
        logging('Discord Shutdown Error', 'WARN')

    logging('Log Stopping', 'SHUTDOWN')
    debugLog.close()
    sys.exit()

#Load Config
with open('config.json', 'r+') as x:
    config = json.load(x)

'''
Variable Initialization
'''
#Current Activity
inCombat = False
inMining = False
systemUpdate = False
system = config['lastSystem']

#Log
logsDir = config['user']
logsDir = os.path.join("C:", os.sep, "Users", logsDir, "Documents", "EVE", "logs", "Gamelogs")
logList = []
logContent = []
lastLine = 0
currentLine = 0

#Misc
update = True #If New Text was Detected
debugLog = open(os.getcwd() + '\\logs\\'+ getTime().strftime('%m%d%Y %H%M%S') + '.txt', 'w') #Start Debug Log File
timeLaunched = int(time.time())
timeUpdated = int(time.time())
alliancePic = config['alliance']
allianceName = config['alliance'].replace('_', " ").title()
initalConfig = True

#Discord
clientID = '1136144163868508262'
presence = Presence(clientID)


'''
Program
'''
logging('Program Start', 'STARTUP')

try:
    presence.connect()
except:
    logging('Discord Connection Error', 'WARN')
    shutdown()

while checkRunning():
    if initalConfig:
        logging('EVE and Discord Detected', 'NOTICE')

        for file in os.listdir(logsDir): #Get List of Logs
            if file.endswith(".txt"):
                logList.append(file)
        logDir = os.path.join(logsDir, logList[-1])
        logging('Log is: ' + logDir, 'STARTUP')
        log = open(logDir, "r") #Open Most Recent Log
        logging('Log Opened', 'STARTUP')

        for x in log: #Add Every Line to logContent
            logContent.append(x)
        log.close()
        logging('Log Closed', 'STARTUP')
        logging('Initial Log Analyzed', 'STARTUP')

        logging('Active Character is: ' + currentCharacter(), 'STARTUP')

        presence.update(details = currentCharacter(), state = 'In ' + system, start = timeLaunched, large_image = 'eveonline', large_text = 'EVE Online', small_image = alliancePic, small_text = allianceName)
        logging('Discord Rich Presence Started', 'STARTUP')

        lastLine = len(logContent)
        initalConfig = False

        logging('Inital Startup Complete', 'STARTUP')

    currentLine = updateLog()
    if update:
        for i in range(lastLine, currentLine):
            updateActivity(i)
        lastLine = currentLine
        updateDiscord()
    else:
        updateDiscord()
        logging('No change detected', 'NOTICE')
    time.sleep(config['delay'])

shutdown()