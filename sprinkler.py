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
import initRoutines    as ir
import timeRoutines    as tr
import relayRoutines   as rr
import profileRoutines as pr
import runActProfRtns  as rap
import utilRoutines    as ur
import queue
#############################################################################

gpioDict  = None
rlyObjLst = None
rapCmdQ = queue.Queue()
rapRspQ = queue.Queue()

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

    allRlys  = [1,2,3,4,5,6,7,8]
    strToFunctDict = {
    'or'   : {'func' : rr.openRly,        'parm' : [rlyObjLst,gpioDict,None   ], 
    'menu' : 'Open    Relay '          },

    'cr'   : {'func' : rr.closeRly,       'parm' : [rlyObjLst,gpioDict,None   ], 
    'menu' : 'Close   Relay '          },

    'tr'   : {'func' : rr.toggleRly,      'parm' : [rlyObjLst,gpioDict,None   ], 
    'menu' : 'Toggle  Relay '          },

    'rr'   : {'func' : rr.readRly,        'parm' : [rlyObjLst,gpioDict,allRlys], 
    'menu' : 'Read    Relay '          },

    'cyr'  : {'func' : rr.cycleRly,       'parm' : [rlyObjLst,gpioDict,None   ], 
    'menu' : 'Cycle   Relays'          },


    'mp'   : {'func' : pr.makeProf,       'parm' : None,                         
    'menu' : 'Make    Profiles '       },

    'lp'   : {'func' : pr.listProfs,      'parm' : profDict,                     
    'menu' : 'List    Profiles '       },

    'gap'  : {'func' : pr.getAP,          'parm' : profDict,                     
    'menu' : 'Get Act Profile  '       },

    'sap'  : {'func' : pr.setAP,          'parm' : profDict,                     
    'menu' : 'Set Act Profile  '       },

    'rp'   : {'func' : rap.strtUiThrd,    'parm' : [rlyObjLst,gpioDict,profDict,rapCmdQ,rapRspQ],
    'menu' : 'Run act Profile'         },

    'sp'   : {'func' : rap.stopUiThrd,    'parm' : [rapCmdQ,rapRspQ],                            
    'menu' : 'Stop  Running Pro'       },

    'qp'   : {'func' : rap.queryUiThrd,   'parm' : [rapCmdQ,rapRspQ],                            
    'menu' : 'Query Running Pro'       },


    'gdt'  : {'func':tr.getTimeDate,      'parm' : None,                         
    'menu' : 'Get Date/Time'           },

    'gt'   : {'func':ur.getTemp,          'parm' : None,                         
    'menu' : 'Get CPU Temp '           },

    'gv'   : {'func':ur.getVer,           'parm' : None,                         
    'menu' : 'Get Version  '           },
    }

    inputWords = inputStr.split()
    choice     = inputWords[0]
    optArgsStr = inputWords[1:]
    rtnLst     = ur.verifyRelayArgs( optArgsStr )
    vraRspStr  = rtnLst[0]
    optArgs    = rtnLst[1]

    if choice in strToFunctDict:
        func   = strToFunctDict[choice]['func']
        params = strToFunctDict[choice]['parm']

        if choice in ['or','cr','tr'] and len(optArgs) > 0:
            params    = strToFunctDict[choice]['parm'][:]
            params[2] = optArgs

        if params is None:
            rsp = func()            # rsp[0] = rspStr
            return rsp[0]           # return to srvr for forwarding to clnt.
        else:
            rsp = func(params)      # rsp[0] = rspStr
            return vraRspStr+rsp[0] # return to srvr for forwarding to clnt.

    elif choice == 'm':
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

    else:
        rspStr = 'Invalid command'
        return rspStr               # return to srvr for forwarding to clnt.
