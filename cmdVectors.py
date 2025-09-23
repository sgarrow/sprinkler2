#  C:\Users\stang\AppData\Roaming\Python\Python312\Scripts\pylint .\*.py
'''
When a client enters a command those commands are received by function 
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to.

This project cannot be run on a PC, it has to be run on an RPi with the
exception of file client.py which may be run on a PC.

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

# Import standard python libraries.
import queue

# Import other source files that are in the same directory as this file.
import initRoutines    as ir
import timeRoutines    as tr
import relayRoutines   as rr
import profileRoutines as pr
import runActProfRtns  as rap
import utils           as ut
#############################################################################

gpioDict  = None
rlyObjLst = None
uiCmdQ = queue.Queue() # These queues are used by the rp, qp qnd sp commands.
uiRspQ = queue.Queue() # These commands (run/query/stop active profile) are
wkCmdQ = queue.Queue() # run in various threads and these queues serve as
wkRspQ = queue.Queue() # communication vehicles to/from these threads.
#############################################################################

def killSrvr(): # The ks cmd is handled directly in the handleClient
    return      # function so doesn't need a "worker" function.  However,
                # because of the way the menu/vectoring is done a function
                # needs to at least exist.  This function is never called.
#############################################################################

def disconnect():  # Handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################

def getVer():
    VER = ' v3.21.14 - 22-Sep-2025'
    return [VER]
#############################################################################

def vector(inputStr,styleDic,styleLk): # called from handleClient.

    global gpioDict      # These global variables are
    global rlyObjLst     # discussed in file initRoutines.py.
    if gpioDict is None:
        gpioDict, rlyObjLst = ir.init()

    if styleDic and styleLk: pass # Not used, generates pylint error.

    allRlys  = ['12345678']

    # This dictionary embosies the worker function vector (and menu) info.
    strToFunctDict = {

    ## RELAY ###############################

    'or' : { 'func' : rr.openRly,           
             'parm' : [rlyObjLst,gpioDict,None],
             'menu' : 'Set Relay To Open'            }, # Open Relay

    'cr' : { 'func' : rr.closeRly,          
             'parm' : [rlyObjLst,gpioDict,None],
             'menu' : 'Set Relay To Closed'          }, # Close Relay 

    'tr' : { 'func' : rr.toggleRly,         
             'parm' : [rlyObjLst,gpioDict,None],
             'menu' : 'Toggle  Relay'                },

    'rr' : { 'func' : rr.readRly,           
             'parm' : [rlyObjLst,gpioDict,allRlys],
             'menu' : 'Get All Relay States'         }, # Read Relay

    ## PROFILE MGMT ########################

    'mp' : { 'func' : pr.makeProf,          
             'parm' : None,
             'menu' : 'Make Profiles'                },

    'lp' : { 'func' : pr.listProfs,         
             'parm' : None,
             'menu' : 'Get All Profiles'             }, # List Profiles

    'gap': { 'func' : pr.getAP,             
             'parm' : None,
             'menu' : 'Get Act Profile'              },

    'sap': { 'func' : pr.setAP,             
             'parm' : None,
             'menu' : 'Set Act Profile'              },

    ## PROFILE RUN #########################

    'rp' : { 'func' : rap.strtTwoThrds,     
             'parm' : [rlyObjLst,gpioDict,
                       uiCmdQ,uiRspQ,wkCmdQ,wkRspQ],
             'menu' : 'Run Active Profile'             },

    'sp' : { 'func' : rap.stopTwoThrd,      
             'parm' : [uiCmdQ],
             'menu' : 'Stop Running Profile'           },

    'qp' : { 'func' : rap.queryViaTwoThrds, 
             'parm' : [uiCmdQ,uiRspQ],
             'menu' : 'Get Profile Status'             }, # Query Running Profile

    ## MISC ################################

    'gdt': { 'func' : tr.getTimeDate,
             'parm' : None,
             'menu' : 'Get Date/Time'                  },

    'gt' : { 'func' : ut.getTemp,
             'parm' : None,
             'menu' : 'Get CPU Temp'                   },

    'gvn': { 'func' : getVer,
             'parm' : None,
             'menu' : 'Get Version Number'             },

    'gat': { 'func' : ut.getActiveThreads,
             'parm' : None,
             'menu' : 'Get Active Threads'             },

    'ks' : { 'func' : killSrvr,
             'parm' : None,
             'menu' : 'Kill Server'                    },

    ## FILE ################################

    'ral': { 'func' : ut.readFile,
             'parm' : ['appLog.txt',[5]],
             'menu' : 'Read App Log File'              },

    'rsl': { 'func' : ut.readFile,
             'parm' : ['serverLog.txt',[5]],
             'menu' : 'Read Srvr Log File'             },

    'rse': { 'func' : ut.readFile,
             'parm' : ['serverException.txt',[5]],
             'menu' : 'Read Srvr Except File'          },

    'cal': { 'func' : ut.clearFile,
             'parm' : ['appLog.txt'],
             'menu' : 'Clear App Log File'             },

    'csl': { 'func' : ut.clearFile,
             'parm' : ['serverLog.txt'],
             'menu' : 'Clear Srvr Log File'            },

    'cse': { 'func' : ut.clearFile,
             'parm' : ['serverException.txt'],
             'menu' : 'Clear Srvr Except File'         },

    'close':{'fun'  : disconnect,
             'prm'  : None,
             'menu' : 'close'                          },
    }

    # Process the string (command) passed to this function via the call
    # from function handleClient in file server.py.
    inputWords = inputStr.split()

    if inputWords == []:       # In case user entered just spaces.
        rspStr = 'Invalid command'
        return rspStr          # Return to srvr for forwarding to clnt.

    choice     = inputWords[0]
    optArgsStr = inputWords[1:]

    if choice in strToFunctDict:
        func   = strToFunctDict[choice]['func']
        params = strToFunctDict[choice]['parm']

        if choice in ['or','cr','tr']:
            params    = strToFunctDict[choice]['parm'][:]
            params[2] = optArgsStr

        if choice in ['sap']:
            params = optArgsStr

        if choice in ['ral','rsl','rse']:
            if len(optArgsStr) > 0:
                params[1] = optArgsStr

        # crontab @reboot /bin/sleep 30; cd python/sprinkler2; nohup python3 server.py > serverException.txt $
        try:
            if params is None:
                rsp = func()   # rsp[0] = rspStr. Vector to worker.
                return rsp[0]  # return to srvr for forwarding to clnt.
         
            rsp = func(params) # rsp[0] = rspStr. Vector to worker.
            return rsp[0]      # Return to srvr for forwarding to clnt.
        except: # pylint: disable=W0702
            rsp = ' Command {} generated an exception'.format(choice)
            print(rsp)
            return rsp

    if choice == 'm':
        rspStrDict = { 'or'  : ' RELAY COMMANDS \n',
                       'mp'  : '\n MANAGE PROFILE COMMANDS \n',
                       'rp'  : '\n RUN PROFILE COMMANDS \n',
                       'gdt' : '\n MISC COMMANDS \n',
                       'ral' : '\n FILE COMMANDS \n'
                     }
        rspStr = ''
        for k,v in strToFunctDict.items():
            if k in rspStrDict:
                rspStr += rspStrDict[k]
            rspStr += ' {:4} - {}\n'.format(k, v['menu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
