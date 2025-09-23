import sys
import multiprocessing as mp
import threading       as th
import subprocess
import gpiozero
import timeRoutines as tr
openSocketsLst = []       # Needed for processing close and ks commands.
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

def getActiveThreads():
    rspStr = ' Running Threads:\n'
    for t in th.enumerate():
        rspStr += '   {}\n'.format(t.name)

    rspStr += '\n Open Sockets:\n'
    for openS in openSocketsLst:
        rspStr += '   {}\n'.format(openS['ca'])

    #rspStr += '\n Running Processes:\n'
    #for k,v in cr.procPidDict.items():
    #    if v is not None:
    #        rspStr += '   {}\n'.format(k)
    return [rspStr]
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
##########################################t###################################

def readFileWrk(parmLst, inFile):
    usage = ' Usage rlf [ numLines [start ["matchStr"]] ].'

    # Get total Lines in file.
    try:
        with open( inFile, 'r',encoding='utf-8') as f:
            numLinesInFile = sum(1 for line in f)
    except:
        return ' Could not open file {} for reading'.format(inFile)

    # Get/Calc number of lines to return (parmLst[0]).
    try:
        numLinesToRtnA = int(parmLst[0])
    except ValueError:
        return ' Invalid number of lines to read.\n' + usage

    numLinesToRtn = min( numLinesToRtnA, numLinesInFile )
    numLinesToRtn = max( numLinesToRtn,  1 ) # Don't allow reading 0 lines.

    # Get/Calc startIdx (parmLst[1]).
    if len(parmLst) > 1:
        try:
            startIdx = max(int(parmLst[1]),0)
        except ValueError:
            return ' Invalid startIdx.\n' + usage

        if startIdx > numLinesInFile:
            startIdx = max(numLinesInFile - numLinesToRtn, 0)
    else:
        startIdx = max(numLinesInFile - numLinesToRtn, 0)

    # Calc endIdx.
    endIdx = max(startIdx + numLinesToRtn - 1, 0)
    endIdx = min(endIdx, numLinesInFile-1)

    # Build matchStr.
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

    with open( inFile, 'r',encoding='utf-8') as f:
        for idx,line in enumerate(f):
            if startIdx <= idx <= endIdx:
                if matchStr != '' and matchStr in line:
                    rspStr += ' {:4} - {}'.format(idx,line)
                elif matchStr == '':
                    rspStr += ' {:4} - {}'.format(idx,line)

    return rspStr
#############################################################################

def clearFileWrk(inFile):
    rspLst = tr.getTimeDate(False)
    curDT  = rspLst[1]
    cDT    = '{}'.format(curDT['now'].isoformat( timespec = 'seconds' ))
    with open(inFile, 'w',encoding='utf-8') as f:
        f.write( 'File cleared on {} \n'.format(cDT))
    return ' {} file cleared.'.format(inFile)
#############################################################################

def readFile(parmLst):
    fName = parmLst[0]
    linesToRead = parmLst[1]
    sys.stdout.flush()
    rspStr = readFileWrk(linesToRead, fName)
    return [rspStr]

def clearFile(parmLst):
    fName = parmLst[0]
    sys.stdout.flush()
    rspStr = clearFileWrk(fName)
    return [rspStr]

def writeFile(fName, inStr):
    with open(fName, 'a', encoding='utf-8') as f:
        f.write( inStr )
        f.flush()
