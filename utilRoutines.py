'''
A collection of misc routines for getting version, temp, active threads and
verifying relay args.
'''
import threading
import subprocess
import gpiozero
import timeRoutines  as tr

# CLEAR IP AND PORTS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
VERSION = ' Version:  3.18'
RELEASED = ' Released:  9-Jan-2025'
# CLEAR IP AND PORTS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
    rspStr  = VERSION  + '\n'
    rspStr += RELEASED
    #print(rspStr)
    return [rspStr]
#############################################################################

def getActiveThreads():
    rspStr = ' Active Threads:'
    for t in threading.enumerate():
        rspStr += '\n   {}'.format(t.name)
    return [rspStr]
#############################################################################

# Read last 25 lines.
# Relay 7 closed at 2024-12-02T16:10:07 # 1024/37 = 27.7 lines.
def getLogFile():
    with open('sprinklerLog.txt', 'r',encoding='utf-8') as f:
        lines = f.readlines()
    rspStr = ' '.join(lines)
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
