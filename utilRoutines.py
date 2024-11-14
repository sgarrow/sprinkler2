import subprocess
import gpiozero

VERSION  = ' Version:  1.94'
RELEASED = ' Released: 13-Nov-2024'
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
        print(rspStr)

    return [rspStr, cpu]
#############################################################################

def getVer():
    rspStr  = VERSION  + '\n'
    rspStr += RELEASED
    print(rspStr)
    return [rspStr]
#############################################################################

def verifyRelayArgs( optArgsStrLst ):

    rspStr = ''
    argsSingleWord  = ''.join(optArgsStrLst)
    argsByIntLst    = [ int(x) for x in filter(str.isdigit,argsSingleWord) ]
    argsByIntNoDups = list(set(argsByIntLst))
    argsByIntNoDupsNo_0 = [ x for x in argsByIntNoDups if 0 < x < 9 ]

    if len(argsSingleWord) != len(argsByIntNoDupsNo_0):
        rspStr += ' Note: Duplicate and/or invalid relay numbers ignored.\n'

    return [rspStr, sorted(argsByIntNoDupsNo_0)]
#############################################################################
