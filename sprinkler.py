#  C:\Users\stang\AppData\Roaming\Python\Python312\Scripts\pylint .\*.py
'''
When a client enters a command those commands are received by function 
handleClient in file server.py.  The command (string) is forwarded to
function "sprinkler" (in this file) and the appropriate "worker" function
is then vectored to.

This project (collection of files/scripts) cannot be run on a PC,
it has to be run on an RPi.

Every file in this project has comments like this at the top.
Comments like this (enclosed by three single quotes) are called doc-strings.
doc-strings are like comments but ... different. Comments are proceeded by #.

The recommended way to learn about this project is to read the comments at
the top of the files in this order:
  server.py, client.py,
  initRoutines.py, timeRoutines.py, relayRoutines.py,
  profileRoutines.py, runActProfRtns.py, config.yml.

After reading the doc-strings perusing the comments will also be helpful.
'''

# Import a standard python libraries.
import pickle

# Import other source files that are in the same directory as this file.
import queue
import initRoutines    as ir
import timeRoutines    as tr
import relayRoutines   as rr
import profileRoutines as pr
import runActProfRtns  as rap
import utilRoutines    as ur
#############################################################################

gpioDict  = None
rlyObjLst = None
uiCmdQ = queue.Queue()
uiRspQ = queue.Queue()
wkCmdQ = queue.Queue()
wkRspQ = queue.Queue()

def sprinkler(inputStr): # called from handleClient. inputStr from client.

    global gpioDict
    global rlyObjLst
    if gpioDict is None:
        gpioDict, rlyObjLst = ir.init()

    try:
        with open('pickle/schedDict.pickle', 'rb') as f:
            profDict = pickle.load(f)
    except FileNotFoundError:
        print('\n Could not open pickle/schedDict.pickle.')
        print(' Generating it now ...\n')
        pr.makeProf()
        with open('pickle/schedDict.pickle', 'rb') as f:
            profDict = pickle.load(f)

    allRlys  = ['12345678']
    strToFunctDict = {

    ## RELAY ###############################

    'or'   : { 'func' : rr.openRly,           'parm':[rlyObjLst,gpioDict,None   ],
    'menu' :   'Open    Relay'                },

    'cr'   : { 'func' : rr.closeRly,          'parm':[rlyObjLst,gpioDict,None   ],
    'menu' :   'Close   Relay'                },

    'tr'   : { 'func' : rr.toggleRly,         'parm':[rlyObjLst,gpioDict,None   ],
    'menu' :   'Toggle  Relay'                },

    'rr'   : { 'func' : rr.readRly,           'parm':[rlyObjLst,gpioDict,allRlys],
    'menu' :   'Read    Relay'                },

    ## PROFILE MGMT ########################

    'mp'   : { 'func' : pr.makeProf,          'parm':None,
    'menu' :   'Make    Profiles'             },

    'lp'   : { 'func' : pr.listProfs,         'parm':profDict,
    'menu' :   'List    Profiles'             },

    'gap'  : { 'func' : pr.getAP,             'parm':profDict,
    'menu' :   'Get Act Profile'              },

    'sap'  : { 'func' : pr.setAP,             'parm':[profDict,None],
    'menu' :   'Set Act Profile'              },

    ## PROFILE RUN #########################

    'rp'   : { 'func' : rap.strtTwoThrds,     'parm':[rlyObjLst,gpioDict,profDict,
                                                      uiCmdQ,uiRspQ,wkCmdQ,wkRspQ],
    'menu' :   'Run   Active  Profile'        },

    'sp'   : { 'func' : rap.stopTwoThrd,      'parm':[uiCmdQ],
    'menu' :   'Stop  Running Profile'        },

    'qp'   : { 'func' : rap.queryViaTwoThrds, 'parm':[uiCmdQ,uiRspQ],
    'menu' :   'Query Running Profile'        },

    ## MISC ################################

    'gdt'  : { 'func' : tr.getTimeDate,       'parm':None,
    'menu' :   'Get Date/Time'                },

    'gt'   : { 'func' : ur.getTemp,           'parm':None,
    'menu' :   'Get CPU Temp'                 },

    'gv'   : { 'func' : ur.getVer,            'parm':None,
    'menu' :   'Get Version'                  },

    'gat'  : { 'func' : ur.getActiveThreads,  'parm':None,
    'menu' :   'Get Active Threads'            },
    }

    inputWords = inputStr.split()

    if inputWords == []: # In case user entered string of just spaces.
        rspStr = 'Invalid command'
        return rspStr               # return to srvr for forwarding to clnt.

    choice     = inputWords[0]
    optArgsStr = inputWords[1:]

    if choice in strToFunctDict:
        func   = strToFunctDict[choice]['func']
        params = strToFunctDict[choice]['parm']

        if choice in ['or','cr','tr']:
            params    = strToFunctDict[choice]['parm'][:]
            params[2] = optArgsStr

        if choice in ['sap']:
            params    = strToFunctDict[choice]['parm'][:]
            params[1] = optArgsStr

        if params is None:
            rsp = func()            # rsp[0] = rspStr
            return rsp[0]           # return to srvr for forwarding to clnt.

        rsp = func(params)          # rsp[0] = rspStr
        return rsp[0]               # return to srvr for forwarding to clnt.

    if choice == 'm':
        rspStr = ''
        for k,v in strToFunctDict.items():
            if k == 'or':
                rspStr += ' RELAY COMMANDS \n'
            elif k == 'mp':
                rspStr += '\n MANAGE PROFILE COMMANDS \n'
            elif k == 'rp':
                rspStr += '\n RUN PROFILE COMMANDS \n'
            elif k == 'gdt':
                rspStr += '\n MISC COMMANDS \n'

            rspStr += ' {:4} - {}\n'.format(k, v['menu'] )
        return rspStr               # return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr                   # return to srvr for forwarding to clnt.
