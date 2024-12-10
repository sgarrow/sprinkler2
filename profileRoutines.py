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

import time
import pickle
import threading
import pprint as pp
import yaml
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

    #kStart    = time.time()
    threadLst = [ t.name for t in threading.enumerate() ]
    if 'runApWrk' in threadLst:
        rspStr=' Can\'t sap while a profile is running. Issue sp and re-try.'
        return [rspStr]

    # Read sapState info.
    with open('pickle/sapStateMachineInfo.pickle', 'rb') as handle:
        stateMachInfo = pickle.load(handle)
    state     = stateMachInfo[ 'sapState'  ]
    profNms   = stateMachInfo[ 'profNames' ]
    #print(' sapStateMachineInfo on entry:')
    #print('',stateMachInfo,'\n')
    ########################################

    # Print a menu of available profiles.
    if state == 0:
        ks = [] # list of profile names
        rspStr = ''
        for ii,(profileKey,v) in enumerate(pDict.items()):
            rspStr += ' {} - {} ({})\n'.format(ii,profileKey,v['about'])
            ks.append(profileKey)

        stateMachInfo = updateSapStateMachineInfo(stateMachInfo,
        sapState  = 1, profNames = ks)
        rspStr += ' sv sapState = 1'
        time.sleep(.05)
    ########################################

    # Get idx of desired profile to make active.
    if state == 1:
        stateMachInfo = updateSapStateMachineInfo(stateMachInfo,sapState=2)
        rspStr = ' sv sapState = 2'
    ########################################

    # Error check idx of desired active profile to make active
    # desired profile index will have been updated in dict by client.
    if state == 2:
        # Get the index of the desired profle from pickle.
        idxStr = dsrdProfIdx[0]
        try:
            idx = int(idxStr)
        except ValueError:
            if idxStr == 'q':
                stateMachInfo = initSapStateMachineInfo()
                rspStr = ' Quiting sap. Resetting sapStateMachine.\n'
                rspStr += ' sv sapState = 0'
            else:
                stateMachInfo = updateSapStateMachineInfo( stateMachInfo,
                                                           sapState=1 )
                rspStr = ' Invalid entry. Must be an integer. Try again.'
                rspStr += ' sv sapState = 1'
        else: # There was no exception.
            if idx > len(pDict)-1:
                updateSapStateMachineInfo(stateMachInfo,sapState=1)
                rspStr = ' Invalid entry. Integer out of range. Try again.'
                rspStr += ' sv sapState = 1'
            else:
                stateMachInfo = updateSapStateMachineInfo(stateMachInfo,
                sapState  = 3)
                rspStr = ' sv sapState = 3'
    ########################################

    # Set active profile.
    # Set all profiles to inactive, except selected profile is set to active.
    if state == 3:
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
        stateMachInfo = initSapStateMachineInfo()
        rspStr = ' sv sapState = 0 \n'
        rspStr += ' Active profile set.'
    ########################################

    # Should never get here, but jusr in case ...
    if 0 > state > 3:
        stateMachInfo = initSapStateMachineInfo()
        rspStr  = ' ERROR. Invalid sapState. Resetting sapStateMachine.\n'
        rspStr += ' sv sapState = 0'
    ########################################

    #print('\n sapStateMachineInfo on exit:')
    #print('',stateMachInfo)
    #print( ' state {} exeTime {:8.5f} sec'.format(state,time.time()-kStart))
    return [rspStr,pDict]
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
