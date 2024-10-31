#  C:\Users\stang\AppData\Roaming\Python\Python312\Scripts\pylint .\*.py
'''
This is the main script for the sprinkler project.
To run it from the RPi command line type "python3 sprinkler.py".
This project (collection of files/scripts) cannot be run on a PC,
it has to be run on an RPi.

Every file in this project has comments like this at the top.
Comments like this (enclosed by three single quotes) are called doc-strings.
doc-strings are like comments but ... different. Comments are proceeded by #.

The recommended way to learn about this project is to read the comments at
the top of the files in this order:
  initRoutines.py, timeRoutines.py, relayRoutines.py,
  profileRoutines.py, config.yml.

After reading the doc-strings perusing the comments will also be helpful.
'''

# Import a standard python libraries.
import pickle

# Import other source files that are in the same directory as this file.
#import initRoutines    as ir
import timeRoutines    as tr
#import relayRoutines   as rr
#import profileRoutines as pr
import utilRoutines    as ur
#############################################################################

def sprinkler(inputStr):

    #print()
    #ur.getVer()

    #gpioDict, rlyObjLst = ir.init()

    try:
        with open('schedDict.pickle', 'rb') as f:
            profDict = pickle.load(f)
    except FileNotFoundError:
        pass
        #print('\n Could not open schedDict.pickle.')
        #print(' Generating it now ...\n')
        #pr.makeProf()
        #with open('schedDict.pickle', 'rb') as f:
        #    profDict = pickle.load(f)

    allRlys = [1,2,3,4,5,6,7,8]
    strToFunctDict = {
    #'or' :{'func':rr.openRelay,  'parm': [rlyObjLst,gpioDict,None   ], 'menu':' Open    Relay    '},
    #'cr' :{'func':rr.closeRelay, 'parm': [rlyObjLst,gpioDict,None   ], 'menu':' Close   Relay    '},
    #'tr' :{'func':rr.toggleRelay,'parm': [rlyObjLst,gpioDict,None   ], 'menu':' Toggle  Relay    '},
    #'rr' :{'func':rr.readRelay,  'parm': [rlyObjLst,gpioDict,allRlys], 'menu':' Read    Relay    '},
    #'cyr':{'func':rr.cycleRelays,'parm': [rlyObjLst,gpioDict,None   ], 'menu':' Cycle   Relays\n '},

    #'mp' :{'func':pr.makeProf,   'parm': None,                         'menu':' Make    Profiles '},
    #'lp' :{'func':pr.listProfs,  'parm': profDict,                     'menu':' List    Profiles '},
    #'gap':{'func':pr.getActProf, 'parm': profDict,                     'menu':' Get Act Profile  '},
    #'sap':{'func':pr.setActProf, 'parm': profDict,                     'menu':' Set Act Profile  '},
    #'rap':{'func':pr.runActProf, 'parm': [rlyObjLst,gpioDict,profDict],'menu':' Run Act Profile\n'},

    'gdt':{'func':tr.getTimeDate,'parm': None,                         'menu':' Get     Date/Time'},
    'gt' :{'func':ur.getTemp,    'parm': None,                         'menu':' Get     CPU Temp '},
    'gv' :{'func':ur.getVer,     'parm': None,                         'menu':' Get     Version  '},
    }

    inputWords = inputStr.split()
    choice     = inputWords[0]
    optArgsStr = inputWords[1:]
    optArgs    = ur.verifyRelayArgs( optArgsStr )

    if choice in strToFunctDict:
        func   = strToFunctDict[choice]['func']
        params = strToFunctDict[choice]['parm']

        if choice in ['or','cr','rr','cycr'] and len(optArgs) > 0:
            params    = strToFunctDict[choice]['parm'][:]
            params[2] = optArgs

        if params is None:
            rsp = func()       # rsp[0] = rspStr
            return rsp[0]      # return to srvr for forwarding to clnt.
        else:
            rsp = func(params) # rsp[0] = rspStr 
            return rsp[0]      # return to srvr for forwarding to clnt. 

    elif choice == 'm':
        rspStr = ''
        for k,v in strToFunctDict.items():
            print(' {:4} - {}'.format(k, v['menu'] ))
            rspStr += ' {:4} - {}\n'.format(k, v['menu'] )
        return rspStr     # return to server so it can forward to client. 

    #rtnVal = rr.openRelay([rlyObjLst,gpioDict,allRlys])
