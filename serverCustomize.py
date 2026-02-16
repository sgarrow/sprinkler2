import multiprocessing as mp
import cmdVectors      as cv # Contains vectors to "worker" functions.
specialCmds = ['tmp']
#############################################################################

def getMultiProcSharedDictAndLock():
    manager = mp.Manager()
    #styleDict = manager.dict({
    mpSharedDict = manager.dict({
        'activeDigitStyle': 'greyOnBlack', # This style cannot be deleted.
        'dayDigitStyle'   : 'greyOnBlack',
        'nightDigitStyle' : 'greyOnBlack',
        'nightTime'       : [ 2, 1, 0, 0, 0, 0 ],
        'dayTime'         : [ 0, 7, 0, 0, 0, 0 ],
        'alarmTime'       : [ 0, 0, 0, 0, 0, 0 ],
        'displayingPics'  : False
    })
    #styleDictLock = mp.Lock()
    mpSharedDictLock = mp.Lock()

    #return styleDict, styleDictLock
    return mpSharedDict, mpSharedDictLock
#############################################################################

def ksCleanup(mpSharedDict, mpSharedDictLock):
    rspStr  = ''
    rspStr += cv.vector('sp',  mpSharedDict, mpSharedDictLock) + '\n'
    rspStr += '\n\n' + cv.vector('or 12345678', mpSharedDict, mpSharedDictLock) + '\n'
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
    #appVerName  = appVerSplit[0]
    appVerNum   = appVerSplit[1].split(' - ')[0]
    #appVerDt    = appVerSplit[1].split(' - ')[1]

    srvVerSplit = srvVerStr.split('=')
    #srvVerName  = srvVerSplit[0]
    srvVerNum   = srvVerSplit[1].split(' - ')[0]
    #srvVerDt    = srvVerSplit[1].split(' - ')[1]

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
    if inParms and clientSocket: pass
    response = 'Nothing Done.'
    return response
