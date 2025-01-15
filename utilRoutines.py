'''
A collection of misc routines for getting version, temp, active threads and
verifying relay args.
'''
import threading
import subprocess
import gpiozero
import timeRoutines  as tr

ver = ' v3.20.0 - 15-Jan-2025'
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

    rspStr  = ''
    print('in  params = ', parmLst)

    # Get total Lines in file.
    numLinesInFile = 0
    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        for line in f:
            numLinesInFile += 1
    rspStr += ' numLinesInFile = {:4}.\n'.format( numLinesInFile )

    # Get/Calc number of lines to return.
    try:
        numLinesToRtnA = int(parmLst[0])
    except ValueError:
        return [' Invalid number of lines to read.' ]
    numLinesToRtn = min( numLinesToRtnA, numLinesInFile )
    numLinesToRtn = max( numLinesToRtn,  1 ) # can't read 0 lines.
    rspStr += '  numLinesToRtn = {:4}.\n'.format( numLinesToRtn )

    # Get/Calc startIdx.
    if len(parmLst) > 1:
        try:
            startIdx = max(int(parmLst[1]),0)
        except ValueError:
            return [' Invalid startIdx.' ]
        else:
            if startIdx > numLinesInFile:
                startIdx = max(numLinesInFile - numLinesToRtn, 0)
    else:
        startIdx = max(numLinesInFile - numLinesToRtn, 0)
    rspStr += '       startIdx = {:4}.\n'.format( startIdx )

    # Calc endIdx.
    endIdx = max(startIdx + numLinesToRtn - 1, 0)
    endIdx = min(endIdx, numLinesInFile-1)
    rspStr += '         endIdx = {:4}.\n'.format( endIdx )

    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        for idx,line in enumerate(f):
            if startIdx <= idx <= endIdx:
                rspStr += '{:4} - {}'.format(idx,line)

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
