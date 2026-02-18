#  C:\Users\stang\AppData\Roaming\Python\Python312\Scripts\pylint .\*.py
'''
When a client enters a command those commands are received by function 
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to.
'''

import queue
import initRoutines    as ir
import timeRoutines    as tr
import relayRoutines   as rr
import profileRoutines as pr
import fileIO          as fio
import runActProfRtns  as rap
import utils           as ut
import swUpdate        as su
#############################################################################

gpioDict  = None
rlyObjLst = None
uiCmdQ = queue.Queue() # These queues are used by the rp, qp qnd sp commands.
uiRspQ = queue.Queue() # These commands (run/query/stop active profile) are
wkCmdQ = queue.Queue() # run in various threads and these queues serve as
wkRspQ = queue.Queue() # communication vehicles to/from these threads.
#############################################################################

# Cmds close,ks,up,rbt are handled directly in the handleClient func so they
# don't need a wrk funct, but because of way vectoring is done a func needs
# to exist. This function is never called/runs.
def dummy():
    return
#############################################################################

# Version number of the "app".
# As opposed to the version number of the "server" which is in fileIO.py
VER = ' v4.1.05 - 17-Feb-2026'
def getVer():
    appVer = VER
    srvVer = fio.VER
    rspStr = ' appVer = {} \n serVer = {}'.format(appVer, srvVer)
    return [rspStr]
#############################################################################

def vector(inputStr,mpSharedDict,mpSharedDictLock): # called from handleClient.

    global gpioDict      # These global variables are
    global rlyObjLst     # discussed in file initRoutines.py.
    if gpioDict is None:
        gpioDict, rlyObjLst = ir.init()

    if mpSharedDict and mpSharedDictLock: pass # Not used, generates pylint error.

    allRlys  = ['12345678']

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {

    # GET COMMANDS
    'grs': { 'func' : rr.readRly,
             'parm' : [rlyObjLst,gpioDict,allRlys],
             'menu' : 'Get Relay States'             },

    'gp' : { 'func' : pr.listProfs,
             'parm' : None,
             'menu' : 'Get Profiles'                 },

    'gap': { 'func' : pr.getAP,
             'parm' : None,
             'menu' : 'Get Act Profile'              },

    'gps': { 'func' : rap.queryViaTwoThrds,
             'parm' : [uiCmdQ,uiRspQ],
             'menu' : 'Get Profile Status'           },

    'gdt': { 'func' : tr.getTimeDate,
             'parm' : None,
             'menu' : 'Get Date/Time'                },

    'gt' : { 'func' : rap.getTemp,
             'parm' : None,
             'menu' : 'Get CPU Temp'                 },

    'gat': { 'func' : ut.getActThrds,
             'parm' : None,
             'menu' : 'Get Active Threads'           },

    'gvn': { 'func' : getVer,
             'parm' : None,
             'menu' : 'Get Version Number'           },

    # SET COMMANDS
    'sro': { 'func' : rr.openRly,
             'parm' : [rlyObjLst,gpioDict,None],
             'menu' : 'Set Relay To Open'            },

    'src': { 'func' : rr.closeRly,          
             'parm' : [rlyObjLst,gpioDict,None],
             'menu' : 'Set Relay To Closed'          },

    'sap': { 'func' : pr.setAP,             
             'parm' : None,
             'menu' : 'Set Act Profile'              },

    # FILE COMMANDS
    'ral': { 'func' : fio.readFile,
             'parm' : ['appLog.txt',[5]],
             'menu' : 'Read App Log File'              },

    'rsl': { 'func' : fio.readFile,
             'parm' : ['serverLog.txt',[5]],
             'menu' : 'Read Srvr Log File'             },

    'rse': { 'func' : fio.readFile,
             'parm' : ['serverException.txt',[5]],
             'menu' : 'Read Srvr Except File'          },

    'cal': { 'func' : fio.clearFile,
             'parm' : ['appLog.txt'],
             'menu' : 'Clear App Log File'             },

    'csl': { 'func' : fio.clearFile,
             'parm' : ['serverLog.txt'],
             'menu' : 'Clear Srvr Log File'            },

    'cse': { 'func' : fio.clearFile,
             'parm' : ['serverException.txt'],
             'menu' : 'Clear Srvr Except File'         },

    # OTHER COMMANDS

    'mp' : { 'func' : pr.makeProf,          
             'parm' : None,
             'menu' : 'Make Profiles'                },

    'rp' : { 'func' : rap.strtTwoThrds,     
             'parm' : [rlyObjLst,gpioDict,
                       uiCmdQ,uiRspQ,wkCmdQ,wkRspQ],
             'menu' : 'Run Active Profile'             },

    'sp' : { 'func' : rap.stopTwoThrd,      
             'parm' : [uiCmdQ],
             'menu' : 'Stop Running Profile'           },

    # OTHER COMMANDS
    'us' : { 'func' : su.updateSw,
             'parm' : [getVer(),'sprinkler2'],
             'menu' : 'Update SW'                      },

    'close':{'func' : dummy,
             'parm' : None,
             'menu' : 'Disconnect'                     },

    'ks' : { 'func' : dummy,
             'parm' : None,
             'menu' : 'Kill Server'                    },

    'rbt': { 'func' : dummy,
             'parm' : None,
             'menu' : 'Reboot RPi'                      },

    # TEST COMMANDS
    't1' : { 'func' : rr.toggleRly,
             'parm' : [rlyObjLst,gpioDict,None],
             'menu' : 'Test 1 - Toggle  Relay'       },

    }
    #####################################################

    # Process the string (command) passed to this function via the call
    # from function handleClient in file server.py.
    inputWords = inputStr.split()

    if inputWords == []:       # In case user entered just spaces.
        rspStr = 'Invalid command'
        return rspStr          # Return to srvr for forwarding to clnt.

    choice     = inputWords[0]
    optArgsStr = inputWords[1:]

    if choice in vectorDict:
        func   = vectorDict[choice]['func']
        params = vectorDict[choice]['parm']

        if choice in ['or','cr','tr']:
            params    = vectorDict[choice]['parm'][:]
            params[2] = optArgsStr

        elif choice in ['sap']:
            params = optArgsStr

        elif choice in ['ral','rsl','rse']:
            if len(optArgsStr) > 0:
                params[1] = optArgsStr

        try:
            if params is None:
                rsp = func()   # rsp[0] = rspStr. Vector to worker.
                return rsp[0]  # return to srvr for forwarding to clnt.

            rsp = func(params) # rsp[0] = rspStr. Vector to worker.
            return rsp[0]      # Return to srvr for forwarding to clnt.
        except Exception as e: # pylint: disable = W0718
            return str(e)

    if choice == 'm':
        tmpDic = {
        'grs' : '{}'.format(   ' === GET   COMMANDS === \n' ),
        'sro' : '{}'.format( '\n === SET   COMMANDS === \n' ),
        'ral' : '{}'.format( '\n === FILE  COMMANDS === \n' ),
        'mp'  : '{}'.format( '\n === OTHER COMMANDS === \n' ),
        't1'  : '{}'.format( '\n === TEST  COMMANDS === \n' ) }

        rspStr = ''
        for k,v in vectorDict.items():
            if k in tmpDic:
                rspStr += tmpDic[k]
            rspStr += ' {:4} - {}\n'.format(k, v['menu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
