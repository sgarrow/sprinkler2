'''
A collection of misc routines for getting version, temp, active threads and
verifying relay args.
'''
import threading
import subprocess
import gpiozero
import timeRoutines  as tr

ver = ' v3.19.0 - 14-Jan-2025'
#############################################################################

def getTemp(prnEn = True):

    rspStr = ''
    cpu = gpiozero.CPUTemperature()

    if prnEn:
        rspStr += ' CPU  Temp = {} \n'.format(   cpu.temperature )
        rspStr += ' Over Temp = {} \n\n'.format( cpu.is_active   )

        result  = subprocess.run(['vcgencmd', 'get_throttled'],
                  stdout=subprocess.PIPE, check = False)
        rspStr += ' {} \n'.format(result.stdout.decode('utf-8').strip())

        rspStr += '  0: under-voltage\n'
        rspStr += '  1: arm frequency capped\n'
        rspStr += '  2: currently throttled\n'
        rspStr += ' 16: under-voltage has occurred\n'
        rspStr += ' 17: arm frequency capped has occurred\n'
        rspStr += ' 18: throttling has occurred'
        #print(rspStr)

    return [rspStr, cpu]
#############################################################################

def getVer():
    return [ver]
#############################################################################

def getActiveThreads():
    rspStr = ' Active Threads:'
    for t in threading.enumerate():
        rspStr += '\n   {}'.format(t.name)
    return [rspStr]
#############################################################################

def getLogFile(parmLst):

    print('in  params = ', parmLst)

    try:
        numLinesToRtn = int(parmLst[0])
    except ValueError:
        return [' Invalid number of lines to read.' ]

    lastIdx = 0
    rspStr  = ''

    #return(['quick return'])

    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        for line in f:
            lastIdx += 1
        rspStr += ' Last Lines Idx is {},  returning last {} lines.\n'.\
            format(lastIdx, numLinesToRtn)

    delta = lastIdx - numLinesToRtn
    startIndexToReturn = delta if delta > 0 else 0

    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        for idx,line in enumerate(f):
            if idx >= startIndexToReturn:
                rspStr += line

    return [rspStr]
#############################################################################

def clearLogFile():
    rspLst = tr.getTimeDate(False)
    curDT  = rspLst[1]
    cDT = '{}'.format(curDT['now'].isoformat( timespec = 'seconds' ))
    with open('sprinklerLog.txt', 'w',encoding='utf-8') as f:
        f.write( 'File cleared on {} \n'.format(cDT))
    return [' sprinklerLog.txt file cleared.']
#############################################################################
