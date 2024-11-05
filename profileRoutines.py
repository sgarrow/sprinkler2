'''
This module contains all the functions that deal with profiles.
A profile is a sprinkler schedule: valve, days, times, durations, etc.

Profiles are defined in the file config.yml.  config.yml is just a text file
but it is in specific format that is parseable by the python module named
'yaml' (yet another mark up language ... sort of like xml files).
config.yml can be edited on a PC and can contain multiple profiles.

This module has 5 funcs all of which are callable directly from the prompt.

Command mp: Calls function makeProfile.
            This function reads config.yml and converts the text therein into
            a python "dictionary" A dictionary is directly useable by the
            python programming language whereas the text file itself
            (config.yml) is not.  The resulting dictionary is saved to a
            binary file named schedDict.pickle.

            schedDict.pickle is loaded automatically when the main script
            (sprinkler.py) is started (from the RPi command line).

            Note: It's easier to edit config.yml on a PC.  To then make the
            pickle file on the PC type "python profileRoutines.py" at a
            PC command prompt.

Command lp: Calls function listProfiles.
            This function prints the profiles, the data in the dictionary
            loaded at start up as described above.

Command gap: Calls function getActiveProfile.
             This function prints the name of the active profile -
             the profile that will be run when the rap command is entered.

Command sap: Calls function setActiveProfile.

Command rap: Calls function runActiveProfile.
             This function is an infinite loop.  The loop can be exited with
             ctrl-c.  Upon exit a return to the command prompt occurs.
'''

import pickle
import time
import datetime      as dt
import pprint        as pp
import yaml
#import relayRoutines as rr
import timeRoutines  as tr
import utilRoutines  as ur

ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'
#############################################################################

def makeProfSap(sapProdDict):
    with open('schedDict.pickle', 'wb') as handle:
        pickle.dump(sapProdDict, handle)
#############################################################################

def makeProf( ):
    with open('config.yml', 'r',encoding='utf-8') as file:
        schedDict = yaml.safe_load(file)

    with open('schedDict.pickle', 'wb') as handle:
        pickle.dump(schedDict, handle)

    with open('schedDict.pickle', 'rb') as handle:
        sd = pickle.load(handle)

    rspStr = pp.pformat(sd)

    print(rspStr)
    return [rspStr]
#############################################################################

def listProfs( pDict ):
    rspStr = ''
    for profile,sched in pDict.items():
        rspStr += ' {}\n'.format(profile)
        rspStr += '  About   {}\n'.format(sched['about'])
        rspStr += '  Active  {}\n\n'.format(sched['active'])

        for theKey,data in sched.items():

            if theKey.startswith('relay'):
                rspStr += '  {:<6}'.format(theKey)
                rspStr += '  {}\n'.format(data['About'])
                rspStr += '          Days: {}, Times: {}, Durations: {}\n'.\
                    format(data['Days'], data['Times'], data['durations'])

    print(rspStr)
    return [rspStr]
#############################################################################

def getActProf( pDict ):
    ap = None
    for profileKey,profileValue in pDict.items():
        for profKey,profValue in profileValue.items():
            if profKey == 'active':
                if profValue:
                    ap = profileKey
                    break
        if ap is not None:
            break

    rspStr = ' Active Profile = {}'.format(ap)
    print(rspStr)
    return [rspStr]
#############################################################################
def setActProf( pDict ):

    # Read sapState info.
    with open('sapStateMachineInfo.pickle', 'rb') as handle:
        stateMachInfo = pickle.load(handle)
    state     = stateMachInfo[ 'sapState'    ]
    profIdx   = stateMachInfo[ 'dsrdProfIdx' ]
    profNms   = stateMachInfo[ 'profNames'   ]
    print(' sapStateMachineInfo on entry:')
    print('',stateMachInfo,'\n')
    ########################################

    # Print a menu of available profiles.
    if state == 0:
        ks = [] # list of profile names
        rspStr = ''
        for ii,profileKey in enumerate(pDict):
            rspStr += ' {} - {}\n'.format(ii,profileKey)
            ks.append(profileKey)

        stateMachInfo = updateSapStateMachineInfo(stateMachInfo,
        sapState  = 1, profNames = ks)
        rspStr += ' Going from state 0 to state 1.'
    ########################################

    # Get idx of desired profile to make active.
    if state == 1:
        stateMachInfo = updateSapStateMachineInfo(stateMachInfo,sapState=2)
        rspStr = ' Going from state 1 to state 2.'
    ########################################

    # Error check idx of desired active profile to make active
    # desired profile index will have been updated in dict by client.
    if state == 2:
        # Get the index of the desired profle from pickle.
        idxStr = profIdx
        print(' idxStr = ', idxStr)
        try:
            idx = int(idxStr)
        except ValueError:
            if idxStr == 'q':
                rspStr = ' Quiting sap. Resetting sapStateMachine.'
                stateMachInfo = initSapStateMachineInfo()
            else:
                rspStr = ' Invalid entry. Must be an integer. Try again. Going from state 2 back to state 1'
                stateMachInfo = updateSapStateMachineInfo(stateMachInfo,sapState=1)
        else: # There was no exception.
            if idx > len(pDict):
                updateSapStateMachineInfo(stateMachInfo,sapState=1)
                rspStr = ' Invalid entry. Integer out of range. Try again. Going from state 2 back to state 1'
            else:
                stateMachInfo = updateSapStateMachineInfo(stateMachInfo,
                sapState  = 3,
                prompt    = '\n Choice (m=menu, q=quit) -> '  )

                rspStr = ' valid idx entry. Going from state 2 to state 3'
    ########################################

    # Set active profile.
    # Set all profiles to inactive, except selected profile is set to active.
    if state == 3:
        ap = profNms[int(profIdx)] # Name of the profile to set active.
        for profileKey,profileValue in pDict.items():
            for profKey in profileValue:
                if profKey == 'active':
                    if profileKey == ap:
                        pDict[profileKey]['active'] = True
                    else:
                        pDict[profileKey]['active'] = False
        makeProfSap(pDict)
        rspStr = ' active profile set. Resetting sapStateMachine.'
        stateMachInfo = initSapStateMachineInfo()
    ########################################
    
    if 0 > state > 3:
        rspStr = ' Invalid sapState. Resetting sapStateMachine.'
        stateMachInfo = initSapStateMachineInfo()
    ########################################

    print('\n sapStateMachineInfo on exit:')
    print('',stateMachInfo)
    print(rspStr)
    print('*********************************')
    return [rspStr,pDict]
#############################################################################

def checkDayMatch( rlyData, currDT ):

    dayMatch = False
    onDays   = rlyData['Days']

    if 'all' in onDays:
        dayMatch  = True

    elif currDT['dowStr'] in onDays:
        dayMatch  = True

    elif 'even' in onDays and currDT['day']%2 == 0:
        dayMatch  = True

    elif 'odd'  in onDays and currDT['day']%2 == 1:
        dayMatch  = True

    return dayMatch
#############################################################################
def checkTimeMatch( rlyData, currDT ):

    onTimes   = rlyData['Times']
    durations = rlyData['durations']

    timeMatch     = False

    print('   {:20} {:20} {:20} {:10}'.format('onTime','now','offTime','inWindow'))
    for t,d in zip(onTimes,durations):
        onTime = dt.datetime( currDT['year'], currDT['month'], currDT['day'],
                              t//100, t%100, 0)

        offTime = onTime + dt.timedelta(seconds = d*60)

        tempTimeMatch = onTime <= currDT['now'] <= offTime
        if tempTimeMatch:
            timeMatch = True

        onT = '{}'.format( onTime.\
              isoformat( timespec = 'seconds' ))

        cDT = '{}'.format( currDT['now'].\
              isoformat( timespec = 'seconds' ))

        ofT = '{}'.format( offTime.\
              isoformat( timespec = 'seconds' ))

        print('   {:20} {:20} {:20} {}'.\
            format( onT, cDT, ofT, tempTimeMatch ))


    return timeMatch
#############################################################################


def runActProf( parmLst ):

    relayObjLst = parmLst[0] # For access to relay methods.
    gpioDic      = parmLst[1] # For print Statements (pin, gpio, .. )
    pDict        = parmLst[2] # profile dict
    rtnVal = 0
    apName = getActProf( pDict )
    apDict = pDict[apName]

    try:
        while 1:
            curDT = tr.getTimeDate(False)
            for relayName,relayData in apDict.items():

                if relayName in ('active', 'about'):
                    continue

                relayNum  = int(relayName[-1])
                cpuInfo   = ur.getTemp(False)

                print(' {} {} {} {} ( Temp = {:.1f}{}C )'.\
                    format( relayName, relayData['Days'],
                            relayData['Times'], relayData['durations'],
                            cpuInfo.temperature, chr(176)))

                dayMatch = checkDayMatch( relayData,curDT )

                if dayMatch:
                    timeMatch = checkTimeMatch( relayData, curDT )

                print( '   day  match = {}{}{}'.format( ESC+RED, dayMatch, ESC+TERMINATE ))
                if dayMatch:
                    print( '   time match = {}{}{}'.format( ESC+RED, timeMatch, ESC+TERMINATE ))

                if timeMatch:
                    relayState = rr.readRelay([relayObjLst,gpioDic,[relayNum]])
                    if relayState == 'open':
                        rtnVal = rr.closeRelay([relayObjLst,gpioDic,[relayNum]] )
                else:
                    relayState = rr.readRelay([relayObjLst,gpioDic,[relayNum]])
                    if relayState == 'closed':
                        rtnVal = rr.openRelay( [relayObjLst,gpioDic,[relayNum]] )
                print()
            print('############################################')
            time.sleep(5)

    except KeyboardInterrupt:
        return rtnVal
#############################################################################
def initSapStateMachineInfo():
    sapStateMachineInfo = { 
    'sapState'   : 0,
    'dsrdProfIdx': 1,
    'profNames'  : [],
    'prompt'     : ' Enter num of dsrd Act Prof (or \'q\') -> '
    }
    with open('sapStateMachineInfo.pickle', 'wb') as handle:
        pickle.dump(sapStateMachineInfo, handle)
    return sapStateMachineInfo
#############################################################################

def updateSapStateMachineInfo(sapStateMachineInfo, **kwargs):
    sapStateMachineInfo.update(kwargs)
    with open('sapStateMachineInfo.pickle', 'wb') as handle:
        pickle.dump(sapStateMachineInfo, handle)
    return sapStateMachineInfo
#############################################################################

if __name__ == '__main__':
    makeProf()
    initSapStateMachineInfo()

