'''
This module contains all the functions that deal with profiles.
A profile is a sprinkler schedule: valve, days, times, durations, etc.

Profiles are defined in the file config.yml.  config.yml is just a text file
but it is in specific format that is parseable by the python module named
'yaml' (yet another mark up language ... sort of like xml files).
config.yml can be edited on a PC and can contain multiple profiles.

This module has 4 funcs all of which are callable directly from the prompt.

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

Command gap: Calls function getAP (getActiveProfile).
             This function prints the name of the active profile -
             the profile that will be run when the rap command is entered.

Command sap: Calls function setAP (setActiveProfile).
'''

import pickle
import threading
import pprint as pp
import yaml

# For print red text in the client wondows.
ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'
#############################################################################

def makeProfSap(sapProdDict):
    with open('pickle/schedDict.pickle', 'wb') as handle:
        pickle.dump(sapProdDict, handle)
#############################################################################

def makeProf( ):
    with open('config.yml', 'r',encoding='utf-8') as file:
        schedDict = yaml.safe_load(file)

    with open('pickle/schedDict.pickle', 'wb') as handle:
        pickle.dump(schedDict, handle)

    with open('pickle/schedDict.pickle', 'rb') as handle:
        sd = pickle.load(handle)

    rspStr = pp.pformat(sd)

    #print(rspStr)
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

    #print(rspStr)
    return [rspStr]
#############################################################################

def getAP( pDict ):
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
    #print(rspStr)
    return [rspStr,ap]
#############################################################################
def setAP( parmLst ):

    pDict       = parmLst[0]
    dsrdProfIdx = parmLst[1]

    threadLst = [ t.name for t in threading.enumerate() ]
    if 'runApWrk' in threadLst:
        rspStr=' Can\'t sap while a profile is running. Issue sp and re-try.'
        return [rspStr]

    # Read sapState info.
    with open('pickle/sapStateMachineInfo.pickle', 'rb') as handle:
        stateMachInfo = pickle.load(handle)
    state     = stateMachInfo[ 'sapState'  ]
    profNms   = stateMachInfo[ 'profNames' ]

    stateToFuncDict = { 0 : sapSte0, 1 : sapSte1, 2 : sapSte2, 3 : sapSte3 }

    stateToParmDict = { 0 : [ pDict, stateMachInfo ],
                        1 : [ stateMachInfo ],
                        2 : [ pDict, dsrdProfIdx, stateMachInfo ],
                        3 : [ pDict, dsrdProfIdx, profNms ] }

    rspStr = stateToFuncDict[state](stateToParmDict[state])

    return [rspStr]
########################################

def sapSte0(parmLst):

    pDict         = parmLst[0]
    stateMachInfo = parmLst[1]

    # Print a menu of available profiles.
    ks = [] # list of profile names
    rspStr = ''
    for ii,(profileKey,v) in enumerate(pDict.items()):
        rspStr += ' {} - {} ({})\n'.format(ii,profileKey,v['about'])
        ks.append(profileKey)

    stateMachInfo = updateSapStateMachineInfo(stateMachInfo,
    sapState  = 1, profNames = ks)
    rspStr += ' sv sapState = 1'
    return rspStr
########################################

def sapSte1(parmLst):

    stateMachInfo = parmLst[0]

    # Get idx of desired profile (from client) to make active.
    stateMachInfo = updateSapStateMachineInfo(stateMachInfo,sapState=2)
    rspStr = ' sv sapState = 2'
    return rspStr
########################################

def sapSte2(parmLst):

    pDict         = parmLst[0]
    dsrdProfIdx   = parmLst[1]
    stateMachInfo = parmLst[2]

    # Error check idx of desired active profile to make active
    # desired profile index will have been sent in by client.
    idxStr = dsrdProfIdx[0]
    try:
        idx = int(idxStr)
    except ValueError:
        if idxStr == 'q':
            stateMachInfo = initSapStateMachineInfo()
            rspStr= ' Quit sap. Reset sapStateMachine.\n sv sapState = 0'
        else:
            stateMachInfo = updateSapStateMachineInfo( stateMachInfo,
                                                       sapState=1 )
            rspStr = ' Invalid entry. Not an integer. Try again.\n sv sapState = 1'
    else: # There was no exception.
        if idx > len(pDict)-1:
            updateSapStateMachineInfo(stateMachInfo,sapState=1)
            rspStr = ' Invalid entry. Int out of range. Try again.\n sv sapState = 1'
        else:
            stateMachInfo = updateSapStateMachineInfo(stateMachInfo,
            sapState  = 3)
            rspStr = ' sv sapState = 3'
    return rspStr
########################################

def sapSte3(parmLst):

    pDict         = parmLst[0]
    dsrdProfIdx   = parmLst[1]
    profNms       = parmLst[2]

    # Set active profile.
    # Set all profiles to inactive, except selected profile is set to active.
    idxStr = dsrdProfIdx[0]
    ap = profNms[int(idxStr)] # Name of the profile to set active.
    for profileKey,profileValue in pDict.items():
        for profKey in profileValue:
            if profKey == 'active':
                if profileKey == ap:
                    pDict[profileKey]['active'] = True
                else:
                    pDict[profileKey]['active'] = False
    makeProfSap(pDict) # new ap will be active on next start up as well.
    initSapStateMachineInfo()
    rspStr = ' sv sapState = 0 \n'
    rspStr += ' Active profile set.'
    return rspStr
#############################################################################

def initSapStateMachineInfo():
    sapStateMachineInfo = {
    'sapState'   : 0,
    'profNames'  : [],
    }
    with open('pickle/sapStateMachineInfo.pickle', 'wb') as handle:
        pickle.dump(sapStateMachineInfo, handle)
    return sapStateMachineInfo
#############################################################################

def updateSapStateMachineInfo(sapStateMachineInfo, **kwargs):
    sapStateMachineInfo.update(kwargs)
    with open('pickle/sapStateMachineInfo.pickle', 'wb') as handle:
        pickle.dump(sapStateMachineInfo, handle)
    return sapStateMachineInfo
#############################################################################

if __name__ == '__main__':
    makeProf()
    initSapStateMachineInfo()
