import multiprocessing as mp
import cmdVectors      as cv # Contains vectors to "worker" functions.
specialCmds = ['tmp']
#############################################################################

def getMultiProcSharedDict():
    manager = mp.Manager()
    styleDict = manager.dict({
        'tbd1' : 'tbd1',
        'tbd2' : 'tbd2',
        'tbd3' : 'tbd3',
        'tbd4' : 'tbd4',
        'tbd5' : 'tbd5',
        'tbd6' : 'tbd6',
    })
    styleDictLock = mp.Lock()
    return styleDict, styleDictLock
#############################################################################

def ksCleanup(styleDict, styleDictLock):
    rspStr  = ''
    rspStr += cv.vector('sp',  styleDict, styleDictLock) + '\n'
    rspStr += '\n\n' + cv.vector('or 12345678', styleDict, styleDictLock) + '\n'
    return rspStr
#############################################################################

def displayLanIp(inLanIp):
    if inLanIp:
        lanIp   = inLanIp.split('.')
    else:
        lanIp   = [ '?', '?', '?', '?' ]

    verStrLst = cv.getVer()
    verStr    = verStrLst[0]
    verLines  = verStr.split('\n')
    appVerStr = verLines[0]
    srvVerStr = verLines[1]

    appVerSplit = appVerStr.split('=')
    appVerName  = appVerSplit[0]
    appVerNum   = appVerSplit[1].split(' - ')[0]
    appVerDt    = appVerSplit[1].split(' - ')[1]

    srvVerSplit = srvVerStr.split('=')
    srvVerName  = srvVerSplit[0]
    srvVerNum   = srvVerSplit[1].split(' - ')[0]
    srvVerDt    = srvVerSplit[1].split(' - ')[1]

    appV = [ x.strip() for x in appVerNum.split('.') ]
    srvV = [ x.strip() for x in srvVerNum.split('.') ]
    print()

    print(' LAN IP  as list: {}'.format( lanIp  ))
    print(' APP VER as list: {}'.format( appV ))
    print(' SRV VER as list: {}'.format( srvV ))
#############################################################################
def hwInit():
    print('No HW Init to do.')
#############################################################################

def specialCmdHndlr(inParms, clientSocket):
    response = 'Nothing Done.'
    return response


