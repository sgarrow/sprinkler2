'''
fixme
'''

import time
import queue
import threading
import datetime      as dt
import relayRoutines as rr
import timeRoutines  as tr
import utilRoutines  as ur
import profileRoutines as pr

ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'
#############################################################################

def strtTwoThrds( parmLst ): # Called from sprinklerb (rp).

    relayObjLst = parmLst[0] # For access to relay methods.
    gpioDic     = parmLst[1] # For print Statements (pin, gpio, .. )
    pDict       = parmLst[2] # profile dict
    uiCQ        = parmLst[3] # For com between handleClient thread and
    uiRQ        = parmLst[4] # runApUi thread (started below).
    wkCQ        = parmLst[5]
    wkRQ        = parmLst[6]

    threadLst = [ t.name for t in threading.enumerate() ]

    #######################
    if 'runApUi' in threadLst:
        startRsp = ' runApUi thread already started \n'
        #print(' {}'.format(startRsp))
    else:
        prmLst = [uiCQ,uiRQ,wkCQ,wkRQ]
        runApUiThrd = threading.Thread( target = runApUi,
                                        name   = 'runApUi',
                                        args   = (prmLst,)
                                      )
        runApUiThrd.start()
        startRsp = ' runApUi thread started'
    #######################
    if 'runApWrk' in threadLst:
        startRsp += ' runApWrk thread already started \n'
        #print(' {}'.format(startRsp))
    else:
        prmLst = [relayObjLst,gpioDic,pDict,wkCQ,wkRQ]
        runApWrkThrd = threading.Thread( target = runApWrk,
                                         name   = 'runApWrk',
                                         args   = (prmLst,)
                                        )
        runApWrkThrd.start()
        startRsp += '\n runApWrk thread started'
    #######################

    #print(' {}'.format(startRsp))
    return [startRsp]
#############################################################################

def queryViaTwoThrds( parmLst ):  # Called from sprinkler (qp).

    uiCQ = parmLst[0]
    uiRQ = parmLst[1]

    threadLst = [ t.name for t in threading.enumerate() ]

    if 'runApUi' in threadLst:
        ###################
        uiCQ.put('qp')
        time.sleep(.001)
        if not uiRQ.empty():
            queryRsp = 'queryViaTwoThrds = \n'
            while not uiRQ.empty():
                queryRsp += uiRQ.get(block=False) + '\n'
        else:
            queryRsp = 'queryViaTwoThrds = uiRQ Empty'
            ###################
    else:
        queryRsp = ' runApUi thread not running, so can\'t be queried'
    #print(' {}'.format(queryRsp))
    return [queryRsp]
#############################################################################

def stopTwoThrd( parmLst ): # Called from sprinkler (sp).

    uiCQ = parmLst[0]

    threadLst = [ t.name for t in threading.enumerate() ]

    if 'runApUi' not in threadLst:
        stopRsp = ' runApUi thread not running, so can\'t be stopped.'
    else:
        uiCQ.put('sp')
        stopRsp = ' runApUi  thread stopped \n'
        stopRsp += ' runApWrk thread stopped'
    #print(' {}'.format(stopRsp))
    return [stopRsp]
#############################################################################

def runApUi( parmLst ): # Runs in thread started br startTwo...

    uiCQ        = parmLst[0] # For com between handleClient thread and
    uiRQ        = parmLst[1] # runApUi thread (started below).
    wkCQ        = parmLst[2] # For com between handleClient thread and
    wkRQ        = parmLst[3] # runApUi thread (started below).
    while True:

        # See if queryViaTwoThrds or stopTwoThrd wants to communicate.
        try:
            cmd = uiCQ.get(timeout=1)
        except queue.Empty:
            pass
        else:
            if cmd == 'qp':

                # See if runApWrk has any new data.
                wkInfo = 'runApUi = \n'
                if not wkRQ.empty():
                    while not wkRQ.empty():
                        wkInfo += wkRQ.get(timeout=.1) + '\n'
                else:
                    wkInfo += 'wkRQ Empty' + '\n'

                uiRQ.put('{}'.format(wkInfo))

            if cmd == 'sp':
                wkCQ.put('{}'.format(cmd))
                break
    return 0
#############################################################################

def runApWrk( parmLst ): # Runs in thread started br startTwo...

    relayObjLst = parmLst[0] # For access to relay methods.
    gpioDic     = parmLst[1] # For print Statements (pin, gpio, .. )
    pDict       = parmLst[2] # profile dict
    wkCQ        = parmLst[3]
    wkRQ        = parmLst[4]

    rtnLst      = pr.getAP( pDict )
    apName      = rtnLst[1]
    apDict      = pDict[apName]

    while True:

        try:
            cmd = wkCQ.get(block=False)
        except queue.Empty:
            pass
        else:
            if cmd == 'sp':
                break
        ####
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

            rtnLst  = rr.readRly([relayObjLst,gpioDic,[relayNum]])
            rspStr += rtnLst[0]
            relayState = rtnLst[1]
            if timeMatch:
                if relayState == 'open':
                    rtnLst  = rr.closeRly([relayObjLst,gpioDic,[relayNum]] )
            else:
                if relayState == 'closed':
                    rtnLst = rr.openRly( [relayObjLst,gpioDic,[relayNum]] )
            rspStr += rtnLst[0]
        rspStr += '############################################'
        ####

        wkRQsize = wkRQ.qsize()
        #print(' wkRQ.qsize = {}'.format(wkRQsize))
        if wkRQsize < 5:
            wkRQ.put('runApWrk = {}'.format(rspStr))
        time.sleep(5)
    return 0
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

if __name__ == '__main__':
    pass
