'''
fixme
'''

import time
import queue
import threading
import datetime      as dt
import pprint        as pp
import relayRoutines as rr
import timeRoutines  as tr
import utilRoutines  as ur
import profileRoutines as pr

ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'
#############################################################################

def checkDayMatch( rlyData, currDT ):

    dayMatch = False
    onDays   = rlyData['Days']

    if 'all' in onDays:
        dayMatch  = True

    elif currDT['dowStr'] in onDays:
        dayMatch  = True

    elif 'even' in onDays and currDT['day']%2 == 0:
        dayMatch  = True

    elif 'odd'  in onDays and currDT['day']%2 == 1:
        dayMatch  = True

    return dayMatch
#############################################################################
def checkTimeMatch( rlyData, currDT ):

    onTimes   = rlyData['Times']
    durations = rlyData['durations']
    timeMatch = False

    rspStr = '   {:20} {:20} {:20} {:10} \n'.format('onTime','now','offTime','inWindow')
    for t,d in zip(onTimes,durations):
        onTime = dt.datetime( currDT['year'], currDT['month'], currDT['day'],
                              t//100, t%100, 0)

        offTime = onTime + dt.timedelta(seconds = d*60)

        tempTimeMatch = onTime <= currDT['now'] <= offTime
        if tempTimeMatch:
            timeMatch = True

        onT = '{}'.format( onTime.isoformat(        timespec = 'seconds' ))
        cDT = '{}'.format( currDT['now'].isoformat( timespec = 'seconds' ))
        ofT = '{}'.format( offTime.isoformat(       timespec = 'seconds' ))

        rspStr += '   {:20} {:20} {:20} {} \n'.format(onT,cDT,ofT,tempTimeMatch)
        #print(rspStr)

    return [rspStr,timeMatch]
#############################################################################

def strtTwoThrds( parmLst ): # Called from sprinkler.

    relayObjLst = parmLst[0] # For access to relay methods.
    gpioDic     = parmLst[1] # For print Statements (pin, gpio, .. )
    pDict       = parmLst[2] # profile dict
    uiCQ        = parmLst[3] # For com between handleClient thread and
    uiRQ        = parmLst[4] # runAP_UI thread (started below).
    wkCQ        = parmLst[5]
    wkRQ        = parmLst[6]

    threadLst = [ t.name for t in threading.enumerate() ]

    #######################
    if 'runAP_UI' in threadLst:
        startRsp = ' runAP_UI thread already started'
        print(' {}'.format(startRsp))
    else:
        prmLst = [uiCQ,uiRQ,wkCQ,wkRQ]
        runAP_UI_Thrd = threading.Thread( target = runAP_UI,
                                          name   = 'runAP_UI',
                                          args   = (prmLst,)
                                        )
        runAP_UI_Thrd.start()
        startRsp = ' runAP_UI thread started'
    #######################
    if 'runAP_WRK' in threadLst:
        startRsp += ' runAP_WRK thread already started'
        print(' {}'.format(startRsp))
    else:
        prmLst = [relayObjLst,gpioDic,pDict,wkCQ,wkRQ]
        runAP_WRK_Thrd = threading.Thread( target = runAP_WRK,
                                           name   = 'runAP_WRK',
                                           args   = (prmLst,)
                                        )
        #runAP_WRK_Thrd.start()
        startRsp += ' runAP_WRK thread started'
    #######################

    print(' {}'.format(startRsp))
    return [startRsp]
#############################################################################

def queryViaTwoThrds( parmLst ):  # Called from sprinkler.

    uiCQ = parmLst[0]
    uiRQ = parmLst[1]
    wkCQ = parmLst[2]
    wkRQ = parmLst[3]

    threadLst = [ t.name for t in threading.enumerate() ]

    if 'runAP_UI' in threadLst:
        ###################
        uiCQ.put('qp')
        time.sleep(.001)
        if not uiRQ.empty():
            cmdQsiz  = uiCQ.qsize()
            rspQsiz  = uiRQ.qsize()
            queryRsp = ''
            #queryRsp = 'RQ Not Empty. sizes = {},{} \n'.format(cmdQsiz,rspQsiz)
            while not uiRQ.empty():
                queryRsp += uiRQ.get(block=False)
            print(' Read = {}'.format(queryRsp))
        else:
            cmdQsiz  = uiCQ.qsize()
            rspQsiz  = uiRQ.qsize()
            queryRsp = 'RQ Empty. Sizes = {},{}'.format(cmdQsiz,rspQsiz)
            ###################
    else:
        queryRsp = ' runAP_UI thread not running, so can\'t be queried'
    print(' {}'.format(queryRsp))
    return [queryRsp]
#############################################################################

def stopTwoThrd( parmLst ): # Called from sprinkler.

    uiCQ = parmLst[0]
    uiRQ = parmLst[1]
    wkCQ = parmLst[2]
    wkRQ = parmLst[3]

    threadLst = [ t.name for t in threading.enumerate() ]

    if 'runAP_UI' not in threadLst:
        stopRsp = ' runAP_UI thread not running, so can\'t be stopped.'
    else:
        uiCQ.put('sp')
        stopRsp = ' runAP_UI thread stopped'
    print(' {}'.format(stopRsp))
    return [stopRsp]
#############################################################################

def runAP_UI( parmLst ): # Runs in thread started br startTwo...

    uiCQ        = parmLst[0] # For com between handleClient thread and
    uiRQ        = parmLst[1] # runAP_UI thread (started below).
    wkCQ        = parmLst[2] # For com between handleClient thread and
    wkRQ        = parmLst[3] # runAP_UI thread (started below).

    counter = 0

    while True:

        try:
            cmd = uiCQ.get(timeout=1)
        except queue.Empty:
            pass
        else:
            if cmd == 'qp':
                uiRQ.put(' Wrk Response = {}. \n'.format(counter))

            if cmd == 'sp':
                break

        counter += 1

    return 0
#############################################################################

def runAP_WRK( parmLst ): # Runs in thread started br startTwo...

    relayObjLst = parmLst[0] # For access to relay methods.
    gpioDic     = parmLst[1] # For print Statements (pin, gpio, .. )
    pDict       = parmLst[2] # profile dict
    wkCQ        = parmLst[3]
    wkRQ        = parmLst[4]

    rtnLst      = pr.getAP( pDict )
    apName      = rtnLst[1]
    apDict      = pDict[apName]
    counter = 0

    while True:

        try:
            cmd = wkCQ.get(timeout=5)
        except queue.Empty:
            pass
        else:
            if cmd == 'qp':
                wkRQ.put(' Wrk Response = {}. \n'.format(counter))

            if cmd == 'sp':
                break

        counter += 1

    rspStr = ''
    ##############
    try:
        while 1:
            rspStr = ''
            rspLst = tr.getTimeDate(False)
            curDT  = rspLst[1]
            for relayName,relayData in apDict.items():

                if relayName in ('active', 'about'):
                    continue

                relayNum  = int(relayName[-1])
                rtnLst    = ur.getTemp(False)
                cpuInfo   = rtnLst[1]

                rspStr += ' {} {} {} {} ( Temp = {:.1f}{}C ) \n'.\
                    format( relayName, relayData['Days'],
                            relayData['Times'], relayData['durations'],
                            cpuInfo.temperature, chr(176))

                dayMatch = checkDayMatch( relayData,curDT )

                if dayMatch:
                    rspLst    = checkTimeMatch( relayData, curDT )
                    rspStr   += rspLst[0]
                    timeMatch = rspLst[1]

                rspStr += '   day  match = {}{}{} \n'.format( ESC+RED, dayMatch, ESC+TERMINATE )
                if dayMatch:
                    rspStr +=  '   time match = {}{}{} \n'.format(ESC+RED,timeMatch,ESC+TERMINATE)

                if timeMatch:
                    rtnLst  = rr.readRly([relayObjLst,gpioDic,[relayNum]])
                    rspStr += rtnLst[0]
                    relayState = rtnLst[1]
                    if relayState == 'open':
                        rtnLst  = rr.closeRly([relayObjLst,gpioDic,[relayNum]] )
                        rspStr += rtnLst[0]
                else:
                    rtnLst  = rr.readRly([relayObjLst,gpioDic,[relayNum]])
                    rspStr += rtnLst[0]
                    relayState = rtnLst[1]
                    if relayState == 'closed':
                        rtnLst = rr.openRly( [relayObjLst,gpioDic,[relayNum]] )
                        rspStr += rtnLst[0]
            rspStr += '############################################'
            print(rspStr)
            #time.sleep(5)
            return [rspStr]

    except KeyboardInterrupt:
        return [rspStr]
#############################################################################

if __name__ == '__main__':
    pass
