'''
This module contains all the functions that talk directly to the relays.
This is the only module that talks directly to the relays.

This module has 6 functions 5 of which are callable directly from the prompt.
Commands or,cr,tr,rr,cycr call functions openRelay, closeRelay, toggleRelay
and readRelay, respectively.

The 6th function (relayOCTR) is a driver for or,cr,tr,rr.  Those 4 functions
(openRelay, closeRelay, toggleRelay, readRelay) are just thin wrappers to
relayOCTR.
'''

import inspect
import time

ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'
#############################################################################

def relayOCTR( parmLst ): # Relay Open/Close/Toggle/Read Driver Function.

    relayObjLst  = parmLst[0] # This was created by function in file init.py
    gpioDic      = parmLst[1] # Also from init.py, refer to comments therein.
    relayObjIdxs = parmLst[2] # A list of relays to perform the action on.
    rtnVal       = None

    rspStr = ''
    relays = []
    if relayObjIdxs is not None:
        # -1 RE: Relay nums start @ 1, lst index start @ 0.
        relays = [ relayObjLst[el-1] for el in relayObjIdxs ]
    else:
        rspStr = ' No relays specified.'

    whoCalledMeFuncNameStr = inspect.stack()[1][3]
    for relay in relays:
        gpioStr   = str(relay.pin)
        pinNum    = gpioDic[gpioStr]['pin']
        relayNum  = gpioDic[gpioStr]['relay']

        if whoCalledMeFuncNameStr == 'openRly':
            rspStr +=' Opening relay {} ({:6} on pin {}).\n'.format(relayNum, gpioStr, pinNum)
            relay.off()
        if whoCalledMeFuncNameStr == 'closeRly':
            rspStr +=' Closing relay {} ({:6} on pin {}).\n'.format(relayNum, gpioStr, pinNum)
            relay.on()
        if whoCalledMeFuncNameStr == 'toggleRly':
            rspStr +=' Toggling relay {} ({:6} on pin {}).\n'.format(relayNum, gpioStr, pinNum)
            relay.toggle()
        if whoCalledMeFuncNameStr == 'readRly':
            rtnVal = 'open'
            rv = relay.value
            if rv == 1:
                rtnVal = 'closed'
            rspStr += ' Relay {} ({:6} on pin {}) is {}{}{}.\n'.\
                format(relayNum, gpioStr, pinNum, ESC+RED ,rtnVal, ESC+TERMINATE)

    return [rspStr,rtnVal]
#############################################################################

def openRly( parmLst ):   # Wrapper function.
    rtnLst = relayOCTR( parmLst )
    return rtnLst
#############################################################################

def closeRly( parmLst ):  # Wrapper function.
    rtnLst = relayOCTR( parmLst )
    return rtnLst
#############################################################################

def toggleRly( parmLst ): # Wrapper function.
    rtnLst = relayOCTR( parmLst )
    return rtnLst
#############################################################################

def readRly( parmLst ):   # Wrapper function.
    rtnLst = relayOCTR( parmLst )
    return rtnLst
#############################################################################

def cycleRly( parmLst ):

    relayObjLst = parmLst[0]
    gpioDic     = parmLst[1]
    rtnVal      = 0
    try:
        while True:
            for ii in range(len(relayObjLst)):
                rtnVal = closeRelay([relayObjLst,  gpioDic, [ii+1]])
                time.sleep(1)
                rtnVal = openRelay( [relayObjLst,  gpioDic, [ii+1]])
                time.sleep(3)
    except KeyboardInterrupt:
        pass
    return [rtnVal]
#############################################################################
