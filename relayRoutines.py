'''
This module contains all the functions that talk directly to the relays.
This is the only module that talks directly to the relays.

This module has 5 functions 4 of which are callable directly from the prompt.
Commands or,cr,tr,rr,cycr call functions openRelay, closeRelay, toggleRelay
and readRelay, respectively.

The 5th function (relayOCTR) is a driver for or,cr,tr,rr.  Those 4 functions
(openRelay, closeRelay, toggleRelay, readRelay) are just thin wrappers to
relayOCTR.

Any time a relay is open or closed that fact, along with a timestamp is
written to file appLog.txt.
'''

import inspect
import timeRoutines  as tr
#############################################################################

def verifyRelayArgs( optArgsStrLst ):

    rspStr = ''
    argsSingleWord  = ''.join(optArgsStrLst)
    argsByIntLst    = [ int(x) for x in filter(str.isdigit,argsSingleWord) ]
    argsByIntNoDups = list(set(argsByIntLst))
    argsByIntNoDupsNo0 = [ x for x in argsByIntNoDups if 0 < x < 9 ]

    if len(argsSingleWord) != len(argsByIntNoDupsNo0):
        rspStr += ' Note: Duplicate and/or invalid relay numbers ignored.\n'

    return [rspStr, sorted(argsByIntNoDupsNo0)]
#############################################################################

def relayOCTR( parmLst ): # Relay Open/Close/Toggle/Read Driver Function.

    relayObjLst  = parmLst[0] # This was created by function in file init.py
    gpioDic      = parmLst[1] # Also from init.py, refer to comments therein.
    optArgsStr   = parmLst[2] # A list of relays to perform the action on.
    rtnVal       = None

    rspStr = ''
    relays = []

    if optArgsStr != []:
        rtnLst       = verifyRelayArgs( optArgsStr )
        rspStr      += rtnLst[0]
        relayObjIdxs = rtnLst[1]
        # -1 RE: Relay nums start @ 1, lst index start @ 0.
        relays = [ relayObjLst[el-1] for el in relayObjIdxs ]
        if len(relays) == 0:
            rspStr = ' No relays specified.'
    else:
        rspStr = ' No relays specified.'

    whoCalledMeFuncNameStr = inspect.stack()[1][3]
    for relay in relays:
        gpioStr   = str(relay.pin)
        pinNum    = gpioDic[gpioStr]['pin']
        relayNum  = gpioDic[gpioStr]['relay']

        rspLst = tr.getTimeDate(False)
        curDT  = rspLst[1]
        cDT = '{}'.format(curDT['now'].isoformat( timespec = 'seconds' ))

        if whoCalledMeFuncNameStr == 'openRly':
            rspStr +=' Opening relay {} ({:6} on pin {}).\n'.\
            format(relayNum, gpioStr, pinNum)
            relay.off()
            with open('appLog.txt', 'a',encoding='utf-8') as f:
                f.write( 'Relay {} opened at {} \n'.\
                    format(relayNum,cDT))

        if whoCalledMeFuncNameStr == 'closeRly':
            rspStr +=' Closing relay {} ({:6} on pin {}).\n'.\
                format(relayNum, gpioStr, pinNum)
            relay.on()
            with open('appLog.txt', 'a',encoding='utf-8') as f:
                f.write( 'Relay {} closed at {} \n'.\
                    format(relayNum,cDT))

        if whoCalledMeFuncNameStr == 'toggleRly':
            rspStr +=' Toggling relay {} ({:6} on pin {}).\n'.\
                format(relayNum, gpioStr, pinNum)
            relay.toggle()

        if whoCalledMeFuncNameStr == 'readRly':
            rtnVal = 'open'
            rv = relay.value
            if rv == 1:
                rtnVal = 'closed'
            rspStr += ' Relay {} ({:6} on pin {}) is {}.\n'.\
                format(relayNum,gpioStr,pinNum,rtnVal)

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
