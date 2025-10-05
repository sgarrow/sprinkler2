import sys
import multiprocessing as mp
import threading       as th

import subprocess
import gpiozero
import timeRoutines    as tr


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

def getActThrds():
    rspStr = ' Running Threads:\n'
    for t in th.enumerate():
        rspStr += '   {}\n'.format(t.name)

    rspStr += '\n Open Sockets:\n'
    for ii,openS in enumerate(openSocketsLst):

        rspStr+='   Socket {} Object Information \n'.format(ii)
        rspStr+='     Remote Addr, Port: {}\n'.format(openS['cs'].getpeername())
        rspStr+='      Local Addr, Port: {}\n'.format(openS['cs'].getsockname())
        rspStr+='       File descriptor: {}\n'.format(openS['cs'].fileno()     )
        rspStr+='              Protocol: {}\n'.format(openS['cs'].proto        )
        rspStr+='                Family: {}\n'.format(openS['cs'].family       )
        rspStr+='                  Type: {}\n'.format(openS['cs'].type         )

        rspStr+='   Socket {} Address Information \n'.format(ii)
        rspStr+='               Address: {}\n\n'.format(openS['ca'])

    rspStr += '\n Running Processes:\n'
    for k,v in cr.procPidDict.items():
        if v is not None:
            rspStr += '   {}\n'.format(k)
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

