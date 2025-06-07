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
            (cmdVectors.py) is started (from the RPi command line).

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

def loadProf():
    try:
        with open('pickle/schedDict.pickle', 'rb') as f:
            profDict = pickle.load(f)
    except FileNotFoundError:
        print('\n Could not open pickle/schedDict.pickle.')
        print(' Generating it now ...\n')
        pr.makeProf()
        with open('pickle/schedDict.pickle', 'rb') as f:
            profDict = pickle.load(f)
    return profDict
#############################################################################

def makeProf():
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

def listProfs():
    rspStr = ''
    pDict = loadProf()
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

def getAP():
    pDict = loadProf()
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

    pDict  = loadProf()
    rspStr = ''
    # Check for error conditions.
    if len(parmLst) == 0:
        rspStr  = ' No index specified.  Example usage: sap 1\n'
        rspStr += ' Try one of these (enter index number):\n'
        rspStr += ''.join( '  {} - {}\n'.format(ii,k) for ii,k in enumerate(pDict.keys()))

    if rspStr == '':
        dsrdProfIdx = parmLst[0]
        keyLst      = list(pDict.keys())
        idxStr      = dsrdProfIdx[0]

        try:
            idx = int(idxStr)
        except ValueError:
                rspStr = ' Invalid entry. Not an integer. Try one of these (enter index number):\n'
                rspStr += ''.join( '  {} - {}\n'.format(ii,k) for ii,k in enumerate(pDict.keys()))
        else: # There was no exception.
            if idx > len(pDict)-1:
                rspStr = ' Invalid entry. Int out of range. Try one of these (enter index number):\n'
                rspStr += ''.join( '  {} - {}\n'.format(ii,k) for ii,k in enumerate(pDict.keys()))

    if rspStr == '':
        threadLst = [ t.name for t in threading.enumerate() ]
        print(threadLst)
        if 'runApWrk' in threadLst:
            rspStr = ' Can\'t sap while a profile is running. Issue sp and re-try.'

    if rspStr == '':
        # Set all profiles to inactive, except selected profile is set to active.
        for profileKey,profileValue in pDict.items():
            for profKey in profileValue:
                if profKey == 'active':
                    if profileKey == keyLst[idx]:
                        pDict[profileKey]['active'] = True
                    else:
                        pDict[profileKey]['active'] = False

        with open('pickle/schedDict.pickle', 'wb') as handle:
            pickle.dump(pDict, handle)

        rspStr = ' Active profile set to {}'.format(keyLst[idx])

    return [rspStr]
#############################################################################

if __name__ == '__main__':
    makeProf()
