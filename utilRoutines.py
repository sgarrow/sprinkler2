'''
A collection of misc routines for getting version, temp, active threads and
verifying relay args.
'''
import threading
import subprocess
import gpiozero

VERSION = ' Version:  2.10'
RELEASED = ' Released: 4-Dec-2024'
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
