import multiprocessing as mp
import cmdVectors      as cv # Contains vectors to "worker" functions.

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

def hwInit():
    print('No HW Init to do.')
