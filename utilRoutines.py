'''
A collection of misc routines for getting version, temp, active threads and
verifying relay args.
'''
import threading
import subprocess
import gpiozero
import timeRoutines  as tr

ver = ' v3.20.7 - 21-Jan-2025'
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
    return [VER]
#############################################################################

def getActiveThreads():
    rspStr = ' Active Threads:'
    for t in threading.enumerate():
        rspStr += '\n   {}'.format(t.name)
    return [rspStr]
#############################################################################

def getLogFile(parmLst):

    usage = ' Usage glf [ numLines [start ["matchStr]] ].'

    # Get total Lines in file.
    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        numLinesInFile = sum(1 for line in f)

    # Get/Calc number of lines to return (parmLst[0]).
    try:
        numLinesToRtnA = int(parmLst[0])
    except ValueError:
        return [ ' Invalid number of lines to read.\n' + usage ]

    numLinesToRtn = min( numLinesToRtnA, numLinesInFile )
    numLinesToRtn = max( numLinesToRtn,  1 ) # Don't allow reading 0 lines.

    # Get/Calc startIdx (parmLst[1]).
    if len(parmLst) > 1:
        try:
            startIdx = max(int(parmLst[1]),0)
        except ValueError:
            return [ ' Invalid startIdx.\n' + usage ]

        if startIdx > numLinesInFile:
            startIdx = max(numLinesInFile - numLinesToRtn, 0)
    else:
        startIdx = max(numLinesInFile - numLinesToRtn, 0)

    # Calc endIdx.
    endIdx = max(startIdx + numLinesToRtn - 1, 0)
    endIdx = min(endIdx, numLinesInFile-1)

    # Build MatchStr.
    matchStr = ''
    if len(parmLst) > 2 and parmLst[2].startswith('\"'):
        for el in parmLst[2:]:
            matchStr += (' ' + el) # Adds a starting space, remove below.
            if el.endswith('\"'):
                break
        matchStr = matchStr[1:].replace('\"', '') # [:1] Removes.

    rspStr  = ' numLinesInFile = {:4}.\n'.format( numLinesInFile )
    rspStr += '  numLinesToRtn = {:4}.\n'.format( numLinesToRtn  )
    rspStr += '       startIdx = {:4}.\n'.format( startIdx       )
    rspStr += '         endIdx = {:4}.\n'.format( endIdx         )
    rspStr += '       matchStr = {}.\n\n'.format( matchStr       )

    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        for idx,line in enumerate(f):
            if startIdx <= idx <= endIdx:
                if matchStr != '' and matchStr in line:
                    rspStr += ' {:4} - {}'.format(idx,line)
                elif matchStr == '':
                    rspStr += ' {:4} - {}'.format(idx,line)

    return [rspStr]
#############################################################################

def clearLogFile():
    rspLst = tr.getTimeDate(False)
    curDT  = rspLst[1]
    cDT    = '{}'.format(curDT['now'].isoformat( timespec = 'seconds' ))
    with open('sprinklerLog.txt', 'w',encoding='utf-8') as f:
        f.write( 'File cleared on {} \n'.format(cDT))
    return [' sprinklerLog.txt file cleared.']
#############################################################################
